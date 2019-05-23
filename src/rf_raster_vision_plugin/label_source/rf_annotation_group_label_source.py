import rastervision as rv

from mypy import typing
from uuid import UUID

class RfAnnotationGroupLabelSource(rv.LabelSource):
    def __init__(self,
                 ground_truth_annotation_group: UUID,
                 aois_annotation_group: UUID,
                 project_id: UUID,
                 project_layer_id: UUID,
                 experiment_id: UUID,
                 refresh_token: str) -> RfAnnotationGroupLabelSource:
        pass
