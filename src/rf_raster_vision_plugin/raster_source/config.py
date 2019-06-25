from copy import deepcopy
import logging
from uuid import UUID

from google.protobuf import struct_pb2
from rastervision.core.config import ConfigBuilder
from rastervision.data.raster_source.raster_source_config import (
    RasterSourceConfig,
    RasterSourceConfigBuilder,
)
from rastervision.data.crs_transformer import CRSTransformer
from rastervision.data.raster_transformer.raster_transformer_config import (
    RasterTransformerConfig,
)
from rastervision.protos.raster_source_pb2 import (
    RasterSourceConfig as RasterSourceConfigMsg,
)
from typing import List

from .rf_layer_raster_source import RfLayerRasterSource
from ..immutable_builder import ImmutableBuilder


log = logging.getLogger(__name__)

RF_LAYER_RASTER_SOURCE = "RF_LAYER_RASTER_SOURCE"


class RfRasterSourceConfig(RasterSourceConfig):
    _properties = [
        "project_id",
        "project_layer_id",
        "refresh_token",
        "channel_order",
        "num_channels",
        "rf_api_host",
        "source_type",
        "transformers",
    ]
    source_type = "RF_LAYER_RASTER_SOURCE"

    def __init__(
        self,
        project_id,  # type: UUID
        project_layer_id,  # type: UUID
        refresh_token,  # type: str
        channel_order,  # type: List[int]
        num_channels,  # type: int
        rf_api_host,  # type: str
        transformers,  # type: List[RasterTransformerConfig]
    ):
        self.project_id = project_id
        self.project_layer_id = project_layer_id
        self.refresh_token = refresh_token
        self.channel_order = channel_order
        self.num_channels = num_channels
        self.rf_api_host = rf_api_host
        self.transformers = transformers

    @classmethod
    def from_source(cls, source: RfLayerRasterSource):
        return cls(
            source.project_id,
            source.project_layer_id,
            source.refresh_token,
            source.channel_order,
            source.num_channels,
            source.rf_api_host,
            source.transformers,
        )

    def create_local(self, tmp_dir: str):
        return self

    def create_source(
        self, tmp_dir, crs_transformer=None, extent=None, class_map=None
    ) -> RfLayerRasterSource:
        """Create the RfLayerRasterSource for this config

        crs_transformer, extent, and class_map are all provided for ABC compatibility,
        but they are not used.
        """
        return RfLayerRasterSource(
            self.project_id,
            self.project_layer_id,
            self.refresh_token,
            self.channel_order,
            self.num_channels,
            tmp_dir,
            self.rf_api_host,
        )

    def for_prediction(self, image_uri):
        return self

    def to_proto(self):
        struct = struct_pb2.Struct()
        for k in self._properties:
            if k != "transformers":
                struct[k] = getattr(self, k)
        to_merge = RasterSourceConfigMsg(custom_config=struct)
        try:
            b = super().to_proto()
            b.MergeFrom(to_merge)
            return b
        except AttributeError as e:
            log.warn("Could not serialize something to proto: %s", e.args)
            self.transformers = []
            b = super().to_proto()
            b.MergeFrom(to_merge)
            return b

    def save_bundle_files(self, bundle_dir):
        try:
            return super().save_bundle_files(bundle_dir)
        except AttributeError:
            return (self, [])


class RfRasterSourceConfigBuilder(RasterSourceConfigBuilder, ImmutableBuilder):

    _properties = [
        "project_id",
        "project_layer_id",
        "refresh_token",
        "channel_order",
        "num_channels",
        "rf_api_host",
        "source_type",
        "transformers",
    ]
    config_class = RfRasterSourceConfig
    source_type = RF_LAYER_RASTER_SOURCE

    def __init__(self):
        super(ConfigBuilder, self).__init__()
        self.rf_api_host = "app.staging.rasterfoundry.com"

    def from_proto(self, msg):
        b = super().from_proto(msg)
        return (
            b.with_project_id(msg.custom_config["project_id"])
            .with_project_layer_id(msg.custom_config["project_layer_id"])
            .with_refresh_token(msg.custom_config["refresh_token"])
            .with_channel_order([int(x) for x in msg.custom_config["channel_order"]])
            .with_num_channels(int(msg.custom_config["num_channels"]))
            .with_rf_api_host(msg.custom_config["rf_api_host"])
            .with_source_type(msg.custom_config["source_type"])
            .with_transformers(msg.transformers)
        )

    def with_project_id(self, project_id: UUID):
        return self.with_property("project_id", project_id)

    def with_project_layer_id(self, project_layer_id: UUID):
        return self.with_property("project_layer_id", project_layer_id)

    def with_refresh_token(self, refresh_token: str):
        return self.with_property("refresh_token", refresh_token)

    def with_channel_order(self, channel_order: List[int]):
        return self.with_property("channel_order", channel_order)

    def with_num_channels(self, num_channels: int):
        return self.with_property("num_channels", num_channels)

    def with_rf_api_host(self, rf_api_host: str):
        return self.with_property("rf_api_host", rf_api_host)

    def with_source_type(self, source_type: str):
        return self.with_property("source_type", source_type)

    def with_transformers(self, transformers: List[RasterTransformerConfig]):
        return self.with_property("transformers", transformers)
