import rastervision as rv
from rastervision.core import Box
from rastervision.data.crs_transformer import CRSTransformer, RasterioCRSTransformer

from uuid import UUID

from mypy.types import List, Optional, Tuple
import numpy as np
from pyproj import Proj, transform
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import xy
import requests
from shapely.geometry import shape
from shapely.ops import cascaded_union

LAT_LNG = Proj(init="EPSG:4326")


def _zoom_level_from_resolution(target_reso: float) -> int:
    zooms_with_resolutions = [(n, 156412 / (2 ** n)) for n in range(30)]
    out = 0
    for (zoom, zoom_reso) in zooms_with_resolutions:
        if zoom_reso < target_reso:
            out = zoom
            break
    return out


def _to_latlng(point: Tuple[int, int], src: Proj) -> Tuple[int, int]:
    return transform(src, LAT_LNG, point[0], point[1])


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
        self.resolution = None  # Optional[float]
        self.affine = None  # Optional[rasterio.Affine]
        self.channel_order = channel_order
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.rf_api_host = rf_api_host
        self.rf_tile_host = rf_tile_host
        self.refresh_token = refresh_token
        self._get_api_token()

        self.set_rf_scenes()
        self.set_resolution()

    def _get_api_token(self):
        """Use the refresh token on this raster source to obtain a bearer token"""
        resp = requests.post(
            "https://{rf_api_host}/api/tokens".format(rf_api_host=self.rf_api_host),
            json={"refresh_token": self.refresh_token},
        )
        resp.raise_for_status()
        self._token = resp.json()["id_token"]

    def _get_chip(self, window: Box):
        """Get a chip from a window (in pixel coordinates) for this raster source"""
        zoom = _zoom_level_from_resolution(self.resolution)
        transformer = self.get_crs_transformer()
        map_proj = Proj(init=transformer.map_crs)
        lower_left_map_coord = transformer.pixel_to_map((window.xmin, window.ymax))
        upper_right_map_coord = transformer.pixel_to_map((window.xmax, window.ymin))
        lower_left_lat_lng = _to_latlng(lower_left_map_coord, map_proj)
        upper_right_lat_lng = _to_latlng(upper_right_map_coord, map_proj)
        bbox = "{xmin},{ymin},{xmax},{ymax}".format(
            xmin=lower_left_lat_lng[0],
            ymin=lower_left_lat_lng[1],
            xmax=upper_right_lat_lng[0],
            ymax=upper_right_lat_lng[1],
        )

        geotiff_resp = requests.get(
            "https://{tile_host}/{project_id}/layers/{project_layer_id}/export".format(
                tile_host=self.rf_tile_host,
                project_id=self.project_id,
                project_layer_id=self.project_layer_id,
            ),
            params={"zoom": zoom, "bbox": bbox, "token": self._token},
            headers={"Accept": "image/tiff"},
        )
        geotiff_resp.raise_for_status()
        geotiff_bytes = geotiff_resp.content
        with MemoryFile(geotiff_bytes) as inf:
            with inf.open() as dataset:
                return dataset.read()

    def set_rf_scenes(self):
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
        self.rf_scenes = scenes

    def set_resolution(self):
        """Determine the native resolution for this project layer"""
        # If we've already set the resolution, don't do any more work
        if self.resolution:
            return
        # If we don't have any scenes yet, go find them
        if not self.rf_scenes:
            self.set_rf_scenes()

        cell_size = float("inf")
        for i, scene in enumerate(self.rf_scenes):
            with rasterio.open(scene["ingestLocation"], "r") as src:
                # Use the x and y steps from the source transformation's affine matrix
                # to determine the image's native resolution
                cell_size = min(
                    [
                        np.sqrt(abs(src.meta["transform"].a * src.meta["transform"].e)),
                        cell_size,
                    ]
                )
                if i == 0:
                    self.affine = src.meta["transform"]
        self.resolution = cell_size

    # TODO doesn't currently do pixels oops
    def get_extent(self):
        """Calculate the bounding box in pixels of this raster source"""
        if not self.rf_scenes:
            self.set_rf_scenes()

        poly = cascaded_union([shape(x["dataFootprint"]) for x in self.rf_scenes])
        (xmin, ymin, xmax, ymax) = poly.bounds

        # TODO use transformer map_to_pixel to get dims from bounds

        return Box(ymin, xmin, ymax, xmax)

    def get_dtype(self) -> np.dtype:
        """Determine the highest density datatype in this raster source"""
        if not self.rf_scenes:
            self.set_rf_scenes()

        dtype_char = ""
        dtype_itemsize = 0
        char_map = {"i": 1, "f": 2}
        # First scene will always supersede base values, so this won't end up None
        # for any RF project layers with scenes in them
        cell_type = None

        for scene in self.rf_scenes:
            with rasterio.open(scene["ingestLocation"], "r") as src:
                ct = np.dtype(src.meta["dtype"])
                if (
                    char_map[ct.char] > char_map.get(dtype_char, 0)
                    and ct.itemsize > dtype_itemsize
                ):
                    dtype_char = ct.char
                    dtype_itemsize = ct.itemsize
                    cell_type = ct

        return cell_type

    def get_crs_transformer(self) -> CRSTransformer:

        if self._crs_transformer:
            return self._crs_transformer

        if not self.rf_scenes:
            self.set_rf_scenes()

        scene = self.rf_scenes[0]
        with rasterio.open(scene["ingestLocation"], "r") as inf:
            return RasterioCRSTransformer.from_dataset(inf)
