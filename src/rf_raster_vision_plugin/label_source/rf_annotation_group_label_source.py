from uuid import UUID

from mypy.types import Optional
import rastervision as rv
from rastervision.core import Box
from rastervision.data.crs_transformer import CRSTransformer
from rastervision.data.label.object_detection_labels import ObjectDetectionLabels
from rastervision.data.label_source import LabelSource
from rastervision.data.vector_source.vector_source import transform_geojson
from shapely.geometry import Polygon, shape

import rf_raster_vision_plugin.http.raster_foundry as rf


def _to_rv_feature(annotation: dict, class_map: dict) -> dict:
    """Convert the geojson from Raster Foundry's API into the minimum dict required by Raster Vision
    """

    return {
        "geometry": annotation["geometry"],
        "properties": {"class_id": class_map[annotation["properties"]["label"]]},
    }


class RfAnnotationGroupLabelSource(LabelSource):
    def __init__(
        self,
        annotation_group: UUID,
        project_id: UUID,
        project_layer_id: UUID,
        refresh_token: str,
        crs_transformer: CRSTransformer,
        rf_api_host: str = "app.staging.rasterfoundry.com",
        rf_tile_host: str = "tiles.staging.rasterfoundry.com",
    ):
        """Construct a new LabelSource

        Args:
            annotation_group (UUID): The annotation group that holds the label annotations
            project_id (UUID): A Raster Foundry project id
            project_layer_id (UUID): A Raster Foundry project layer id in this project
            refresh_token (str): A Raster Foundry refresh token to use to obtain an auth token
            rf_api_host (str): The url host name to use for communicating with Raster Foundry
            rf_tile_host (str): The url host name to use for communicating with the Raster Foundry tile server
        """

        self._token = None
        self._labels = None  # dict
        self.annotation_group = annotation_group
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.refresh_token = refresh_token
        self.crs_transformer = crs_transformer
        self.rf_api_host = rf_api_host
        self.rf_tile_host = rf_tile_host

        self._get_api_token()
        self._set_labels()
        self._set_class_map()
        self._set_rv_labels()

    def _set_rv_labels(self, window=None) -> ObjectDetectionLabels:
        self._rv_label_geojson = transform_geojson(
            {
                "features": [
                    _to_rv_feature(feat, self._class_map)
                    for feat in self._raw_labels["features"]
                ]
            },
            self.crs_transformer,
        )

    def _get_api_token(self):
        self._token = rf.get_api_token(self.refresh_token, self.rf_api_host)

    def _set_labels(self):
        self._raw_labels = rf.get_labels(
            self._token,
            self.rf_api_host,
            self.project_id,
            self.project_layer_id,
            self.annotation_group,
            None,
        )

    def _set_class_map(self):
        project = rf.get_project(self._token, self.rf_api_host, self.project_id)
        class_map = project["extras"]["annotate"]["labels"]
        self._class_map = {item["id"]: idx + 1 for idx, item in enumerate(class_map)}

    def get_labels(self, window: Box = None):
        return ObjectDetectionLabels.from_geojson(self._rv_label_geojson, window)
