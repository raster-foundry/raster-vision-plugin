from rastervision.core.config import ConfigBuilder
from rastervision.data.crs_transformer import CRSTransformer
from rastervision.data.label_store.label_store_config import LabelStoreConfig
from .rf_annotation_group_label_store import RfAnnotationGroupLabelStore
from ..immutable_builder import ImmutableBuilder

from typing import Dict
from uuid import UUID


class RfLabelStoreConfig(LabelStoreConfig):
    def __init__(
        self,
        annotation_group,  # type: UUID
        project_id,  # type: UUID
        project_layer_id,  # type: UUID
        refresh_token,  # type: str
        crs_transformer,  # type: CRSTransformer
        class_map,  # type: Dict[int, str]
        rf_api_host,  # type:  str
    ):
        self.annotation_group = annotation_group
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.refresh_token = refresh_token
        self.crs_transformer = crs_transformer
        self.class_map = class_map
        self.rf_api_host = rf_api_host

    def create_store(
        self, task_config=None, extent=None, crs_transformer=None, tmp_dir=None
    ):
        return RfAnnotationGroupLabelStore(
            self.annotation_group,
            self.project_id,
            self.project_layer_id,
            self.refresh_token,
            self.crs_transformer,
            self.class_map,
            self.rf_api_host,
        )

    def for_prediction(self):
        return self

    def report_io(self):
        pass


class RfLabelStoreConfigBuilder(ConfigBuilder, ImmutableBuilder):
    config_class = RfLabelStoreConfig
    _properties = [
        "annotation_group",
        "project_id",
        "project_layer_id",
        "refresh_token",
        "crs_transformer",
        "class_map",
        "rf_api_host",
    ]

    def __init__(self):
        super(ConfigBuilder, self).__init__()
        self.rf_api_host = "app.staging.rasterfoundry.com"

    def from_proto(self, msg):
        return (
            self.with_annotation_group(msg.annotation_group)
            .with_project_id(msg.project_id)
            .with_project_layer_id(msg.project_layer_id)
            .with_refresh_token(msg.refresh_token)
            .with_crs_transformer(msg.crs_transformer)
            .with_rf_api_hsot(msg.rf_api_host)
        )

    def with_class_map(self, class_map: Dict[int, str]):
        return self.with_property("class_map", class_map)

    def with_annotation_group(self, annotation_group: UUID):
        return self.with_property("annotation_group", annotation_group)

    def with_project_id(self, project_id: UUID):
        return self.with_property("project_id", project_id)

    def with_project_layer_id(self, project_layer_id: UUID):
        return self.with_property("project_layer_id", project_layer_id)

    def with_refresh_token(self, refresh_token: str):
        return self.with_property("refresh_token", refresh_token)

    def with_crs_transformer(self, crs_transformer: CRSTransformer):
        return self.with_property("crs_transformer", crs_transformer)

    def with_rf_api_host(self, rf_api_host: str):
        return self.with_property("rf_api_host", rf_api_host)
