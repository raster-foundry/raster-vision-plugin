from ..with_token import WithRefreshToken

from mypy.types import List
import numpy as np
import rastervision as rv
from rastervision.core import Box
from rastervision.core.raster_stats import RasterStats
from rastervision.data.crs_transformer import CRSTransformer
from rastervision.data.activate_mixin import ActivateMixin
from rastervision.data.raster_source.rasterio_source import RasterioSource
from rastervision.data.raster_transformer.stats_transformer import StatsTransformer
import requests

import logging
from urllib.parse import unquote
from uuid import UUID

RF_LAYER_RASTER_SOURCE = "RF_LAYER_RASTER_SOURCE"
log = logging.getLogger(__name__)


class RfLayerRasterSource(rv.data.RasterSource, WithRefreshToken, ActivateMixin):
    source_type = RF_LAYER_RASTER_SOURCE

    def __init__(
        self,
        project_id: UUID,
        project_layer_id: UUID,
        refresh_token: str,
        channel_order: List[int],
        num_channels: int,
        tmp_dir: str,
        rf_api_host: str = "app.staging.rasterfoundry.com",
    ):
        """Construct a new RasterSource

        Args:
            project_id (UUID): A Raster Foundry project id
            project_layer_id (UUID): A Raster Foundry project layer id in this project
            refresh_token (str): A Raster Foundry refresh token to use to obtain an auth token
            channel_order (List[int]): The order in which to return bands
            num_channels (int): How many bands this raster source expects to have
            rf_api_host (str): The url host name to use for communicating with Raster Foundry
        """

        self._crs_transformer = None  # Optional[str]
        self.rf_scenes = None  # Optional[dict]
        self.channel_order = channel_order
        self.num_channels = num_channels
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.rf_api_host = rf_api_host

        self.set_token(rf_api_host, refresh_token)
        self.rf_scenes = self.get_rf_scenes()
        rf_scene_uris = [
            unquote(x["ingestLocation"])
            for x in self.rf_scenes
            if x["statusFields"]["ingestStatus"] == "INGESTED"
        ]
        self._rasterio_source_no_xform = RasterioSource(
            rf_scene_uris, [], tmp_dir, channel_order=self.channel_order
        )
        self.transformers = [StatsTransformer(self.get_stats())]
        self.raster_transformers = self.transformers
        self._rasterio_source = RasterioSource(
            rf_scene_uris, self.transformers, tmp_dir, channel_order=self.channel_order
        )

    def _subcomponents_to_activate(self):
        return [self._rasterio_source]

    def get_stats(self):
        stats = RasterStats()
        stats.compute([self._rasterio_source_no_xform])
        return stats

    def get_rf_scenes(self):
        """Fetch all Raster Foundry scene metadata for this project layer"""
        scenes_url = "https://{api_host}/api/projects/{project_id}/layers/{layer_id}/scenes".format(
            api_host=self.rf_api_host,
            project_id=self.project_id,
            layer_id=self.project_layer_id,
        )
        scenes_resp = requests.get(
            scenes_url, headers={"Authorization": "Bearer " + self._token}
        ).json()
        scenes = scenes_resp["results"]
        page = 1
        while scenes_resp["hasNext"]:
            if page % 10 == 0 and page > 0:
                log.info("Fetching page %s of scenes", page)
            scenes_resp = requests.get(
                scenes_url,
                headers={"Authorization": "Bearer " + self._token},
                params={"page": page},
            ).json()
            if len(scenes_resp["results"]) > 0:
                scenes.append(scenes_resp["results"])
            page += 1
        return scenes

    def _get_chip(self, window: Box):
        """Get a chip from a window (in pixel coordinates) for this raster source"""
        if not self._rasterio_source._mixin_activated:
            print("ACTIVATING RASTER SOURCE")
            self.activate()
        return self._rasterio_source._get_chip(window)

    def get_extent(self):
        """Calculate the bounding box in pixels of this raster source"""
        return self._rasterio_source.get_extent()

    def get_dtype(self) -> np.dtype:
        """Determine the highest density datatype in this raster source"""
        return self._rasterio_source.get_dtype()

    def get_crs_transformer(self) -> CRSTransformer:
        return self._rasterio_source.get_crs_transformer()
