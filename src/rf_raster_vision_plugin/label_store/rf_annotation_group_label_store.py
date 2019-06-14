from rastervision.data.crs_transformer import CRSTransformer
from rastervision.data.label.object_detection_labels import ObjectDetectionLabels
from rastervision.data.label_store import LabelStore

from mypy.types import Dict
from uuid import UUID

from ..http import raster_foundry as rf
from ..http.converters import annotation_features_from_labels
from ..label_source.rf_annotation_group_label_source import RfAnnotationGroupLabelSource


class RfAnnotationGroupLabelStore(LabelStore):
    def __init__(
        self,
        annotation_group: UUID,
        project_id: UUID,
        project_layer_id: UUID,
        refresh_token: str,
        crs_transformer: CRSTransformer,
        class_map: Dict[int, str],
        rf_api_host: str = "app.staging.rasterfoundry.com",
    ):
        self.annotation_group = annotation_group
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.crs_transformer = crs_transformer
        self.class_map = class_map
        self.rf_api_host = rf_api_host
        self._refresh_token = refresh_token

        self._get_api_token(refresh_token)

    def _get_api_token(self, refresh_token: str):
        self._token = rf.get_api_token(refresh_token, self.rf_api_host)

    def get_labels(self) -> ObjectDetectionLabels:
        return RfAnnotationGroupLabelSource(
            self.annotation_group,
            self.project_id,
            self.project_layer_id,
            self._refresh_token,
            self.crs_transformer,
            self.rf_api_host,
        ).get_labels()

    def empty_labels(self) -> ObjectDetectionLabels:
        return ObjectDetectionLabels.make_empty()

    def save(self, labels: ObjectDetectionLabels) -> None:
        rf.post_labels(
            self._token,
            self.rf_api_host,
            self.project_id,
            self.project_layer_id,
            annotation_features_from_labels(
                labels,
                self.crs_transformer,
                self.annotation_group,
                {v: k for k, v in self.class_map.items()},
            ),
        )
