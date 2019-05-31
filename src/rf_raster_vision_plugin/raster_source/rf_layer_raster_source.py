import rastervision as rv
from rastervision.core import Box

from uuid import UUID

from mypy.types import List, Optional
from rasterio.io import MemoryFile
import requests


def _zoom_level_from_resolution(target_reso: float) -> int:
    zooms_with_resolutions = [(n, 156412 / (2 ** n)) for n in range(30)]
    out = 0
    for (zoom, zoom_reso) in zooms_with_cell_sizes:
        if zoom_reso < target_reso:
            out = zoom
            break
    return out


class RfLayerRasterSource(rv.data.RasterSource):
    def __init__(
        self,
        project_id: UUID,
        project_layer_id: UUID,
        source_annotation_group_id: UUID,
        experiment_id: UUID,
        refresh_token: str,
        resolution: float,
        channel_order: List[int],
        num_channels: int,
        rf_api_host: str = "app.staging.rasterfoundry.com",
        rf_tile_host: str = "tiles.staging.rasterfoundry.com",
    ):

        self._token = None  # Optional[str]
        self.channel_order = channel_order
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.rf_api_host = rf_api_host
        self.rf_tile_host = rf_tile_host
        self.refresh_token = refresh_token
        self.resolution = resolution
        self._get_api_token()

    def _get_api_token(self):
        self._token = requests.post(
            "https://{rf_api_host}/api/tokens".format(rf_api_host=self.rf_api_host),
            json={"refreshToken": self.refresh_token},
        ).json()["id_token"]

    def _get_chip(self, window: Box):
        zoom = _zoom_level_from_resolution(self.resolution)
        geotiff_bytes = requests.get(
            "{tile_host}/{project_id}/layers/{project_layer_id}/export".format(
                tile_host=self.rf_tile_host,
                project_id=self.project_id,
                project_layer_id=self.project_layer_id,
            ),
            params={
                "zoom": zoom,
                "bbox": "{xmin},{ymin},{xmax},{ymax}".format(
                    xmin=box.xmin, ymin=box.ymin, xmax=box.xmax, ymax=box.ymax
                ),
                "token": self._token,
            },
        ).content
        with MemoryFile(geotiff_bytes) as inf:
            with inf.open() as dataset:
                return dataset.read()

    def get_extent(self):
        pass

    def get_dtype(self):
        pass

    def get_crs_transformer(self):
        pass
