import rastervision as rv

from mypy import typing, Dict
from uuid import UUID


class RfAnnotationGroupLabelStore(rv.LabelStore):
    def __init__(
        self,
        out_annotation_group: UUID,
        project_id: UUID,
        project_layer_id: UUID,
        uri: str,
        crs_transformer: rv.CRSTransformer,
        class_map: Dict[int, str],
    ) -> RfAnnotationGroupLabelStore:
        pass
