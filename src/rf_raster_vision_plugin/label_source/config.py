from google.protobuf import struct_pb2
from rastervision.core.config import ConfigBuilder
from rastervision.data.raster_source import RasterSource
from rastervision.data.label_source.label_source_config import LabelSourceConfig
from rastervision.protos.label_source_pb2 import (
    LabelSourceConfig as LabelSourceConfigMsg,
)
from .rf_annotation_group_label_source import RfAnnotationGroupLabelSource
from ..raster_source.config import RfRasterSourceConfig
from ..raster_source.rf_layer_raster_source import RfLayerRasterSource
from ..immutable_builder import ImmutableBuilder

from uuid import UUID

RF_ANNOTATION_GROUP_LABEL_SOURCE = "RF_ANNOTATION_GROUP_LABEL_SOURCE"


class RfLabelSourceConfig(LabelSourceConfig):
    source_type = RF_ANNOTATION_GROUP_LABEL_SOURCE
    _properties = [
        "annotation_group",
        "project_id",
        "project_layer_id",
        "refresh_token",
        "raster_source",
        "rf_api_host",
        "source_type",
    ]

    def __init__(
        self,
        annotation_group,  # type: UUID
        project_id,  # type: UUID
        project_layer_id,  # type: UUID
        refresh_token,  # type: str
        raster_source,  # type: RasterSource
        rf_api_host,  # type: str
    ):
        self.annotation_group = annotation_group
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.refresh_token = refresh_token
        self.raster_source = raster_source
        self.rf_api_host = rf_api_host

    def create_source(
        self, task_config=None, extent=None, crs_transformer=None, tmp_dir=None
    ):
        return RfAnnotationGroupLabelSource(
            self.annotation_group,
            self.project_id,
            self.project_layer_id,
            self.refresh_token,
            self.raster_source.get_crs_transformer(),
            self.rf_api_host,
        )

    def report_io(self, x, y):
        pass

    def to_proto(self):
        b = super().to_proto()
        struct = struct_pb2.Struct()
        for k in self._properties:
            if k != "raster_source":
                struct[k] = getattr(self, k)
            else:
                conf = RfRasterSourceConfig.from_source(self.raster_source)
                struct["channel_order"] = conf.channel_order
                struct["num_channels"] = conf.num_channels

        b.MergeFrom(LabelSourceConfigMsg(custom_config=struct))
        return b


class RfLabelSourceConfigBuilder(ConfigBuilder, ImmutableBuilder):
    config_class = RfLabelSourceConfig
    source_type = RF_ANNOTATION_GROUP_LABEL_SOURCE
    _properties = [
        "annotation_group",
        "project_id",
        "project_layer_id",
        "refresh_token",
        "raster_source",
        "rf_api_host",
        "source_type",
    ]

    def __init__(self):
        super(ConfigBuilder, self).__init__()
        self.rf_api_host = "app.staging.rasterfoundry.com"

    def from_proto(self, msg):
        return (
            self.with_annotation_group(msg.custom_config["annotation_group"])
            .with_project_id(msg.custom_config["project_id"])
            .with_project_layer_id(msg.custom_config["project_layer_id"])
            .with_refresh_token(msg.custom_config["refresh_token"])
            .with_raster_source_from_msg(msg)
            .with_rf_api_host(msg.custom_config["rf_api_host"])
            .with_source_type(msg.custom_config["source_type"])
        )

    def with_annotation_group(self, annotation_group: UUID):
        return self.with_property("annotation_group", annotation_group)

    def with_project_id(self, project_id: UUID):
        return self.with_property("project_id", project_id)

    def with_project_layer_id(self, project_layer_id: UUID):
        return self.with_property("project_layer_id", project_layer_id)

    def with_refresh_token(self, refresh_token: str):
        return self.with_property("refresh_token", refresh_token)

    def with_raster_source(self, raster_source: RfLayerRasterSource):
        return self.with_property("raster_source", raster_source)

    def with_raster_source_from_msg(self, msg: LabelSourceConfigMsg):
        custom_config = msg.custom_config
        channel_order = [int(x) for x in list(custom_config["channel_order"])]
        num_channels = custom_config["num_channels"]
        rs = RfLayerRasterSource(
            custom_config["project_id"],
            custom_config["project_layer_id"],
            custom_config["refresh_token"],
            channel_order,
            num_channels,
            "/tmp",
            custom_config["rf_api_host"],
        )
        return self.with_property("raster_source", rs)

    def with_rf_api_host(self, rf_api_host: str):
        return self.with_property("rf_api_host", rf_api_host)

    def with_source_type(self, source_type: str):
        return self.with_property("source_type", source_type)
