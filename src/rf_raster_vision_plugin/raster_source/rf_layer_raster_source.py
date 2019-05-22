import rastervision as rv

from mypy import typing
from uuid import UUID


class RfLayerRasterSource(rv.RasterSource):
    def __init__(self,
                 project_id: UUID,
                 project_layer_id: UUID,
                 source_annotation_group_id: UUID,
                 experiment_id: UUID,
                 refresh_token: str) -> RfLayerRasterSource:
        pass
