from tempfile import gettempdir
from uuid import UUID

from mypy.types import List, Optional, Tuple
import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import xy
import rastervision as rv
from rastervision.core import Box
from rastervision.data.crs_transformer import CRSTransformer, RasterioCRSTransformer
from rastervision.data.raster_source.rasterio_source import RasterioSource

import requests
from shapely.geometry import shape
from shapely.ops import cascaded_union


class RfLayerRasterSource(rv.data.RasterSource):
    def __init__(
        self,
        project_id: UUID,
        project_layer_id: UUID,
        source_annotation_group_id: UUID,
        experiment_id: UUID,
        refresh_token: str,
        channel_order: List[int],
        num_channels: int,
        rf_api_host: str = "app.staging.rasterfoundry.com",
        rf_tile_host: str = "tiles.staging.rasterfoundry.com",
    ):
        """Construct a new RasterSource

        Args:
            project_id (UUID): A Raster Foundry project id
            project_layer_id (UUID): A Raster Foundry project layer id in this project
            source_annotation_group_id (UUID): A Raster Foundry annotation group id in this project layer
            experiment_id (UUID): A Vision App experiment id
            refresh_token (str): A Raster Foundry refresh token to use to obtain an auth token
            channel_order (List[int]): The order in which to return bands
            num_channels (int): How many bands this raster source expects to have
            rf_api_host (str): The url host name to use for communicating with Raster Foundry
            rf_tile_host (str): The url host name to use for communicating with the Raster Foundry tile server
        """

        self._token = None  # Optional[str]
        self._crs_transformer = None  # Optional[str]
        self.rf_scenes = None  # Optional[dict]
        self.channel_order = channel_order
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.rf_api_host = rf_api_host
        self.rf_tile_host = rf_tile_host
        self.refresh_token = refresh_token
        self._get_api_token()

        self.rf_scenes = self.get_rf_scenes()
        self._rasterio_source = RasterioSource(
            [
                x["ingestLocation"]
                for x in self.rf_scenes
                if x["statusFields"]["ingestStatus"] == "INGESTED"
            ],
            [],
            gettempdir(),
            channel_order=self.channel_order,
        )
        self._rasterio_source._activate()

    def _get_api_token(self):
        """Use the refresh token on this raster source to obtain a bearer token"""
        resp = requests.post(
            "https://{rf_api_host}/api/tokens".format(rf_api_host=self.rf_api_host),
            json={"refresh_token": self.refresh_token},
        )
        resp.raise_for_status()
        self._token = resp.json()["id_token"]

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
            scenes_resp = requests.get(
                scenes_url,
                headers={"Authorization": "Bearer " + self._token},
                params={"page": page},
            ).json()
            scenes.append(next_resp["results"])
            page += 1
        return scenes

    def _get_chip(self, window: Box):
        """Get a chip from a window (in pixel coordinates) for this raster source"""
        return self._rasterio_source._get_chip(window)

    def get_extent(self):
        """Calculate the bounding box in pixels of this raster source"""
        return self._rasterio_source.get_extent()

    def get_dtype(self) -> np.dtype:
        """Determine the highest density datatype in this raster source"""
        return self._rasterio_source.get_dtype()

    def get_crs_transformer(self) -> CRSTransformer:
        return self._rasterio_source.get_crs_transformer()
