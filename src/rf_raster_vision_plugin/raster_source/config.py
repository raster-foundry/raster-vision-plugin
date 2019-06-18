from copy import deepcopy
from uuid import uuid4, UUID

import rastervision as rv
from rastervision.core.config import ConfigBuilder
from rastervision.data.raster_source.raster_source_config import RasterSourceConfig
from typing import List, Optional, TypeVar


class RfRasterSourceConfig(RasterSourceConfig):
    project_id = uuid4()
    project_layer_id = uuid4()
    refresh_token = ""
    channel_order = []  # type: List[int]
    num_channels = 0
    rf_api_host = "app.staging.rasterfoundry.com"

    def __init__(
        self,
        project_id,  # type: Optional[UUID]
        project_layer_id,  # type: Optional[UUID]
        refresh_token,  # type: Optional[str]
        channel_order,  # type: List[int]
        num_channels,  # type: Optional[int]
        rf_api_host,  # type: Optional[str]
    ):
        self.project_id = project_id or self.project_id
        self.project_layer_id = project_layer_id or self.project_layer_id
        self.refresh_token = refresh_token or self.refresh_token
        self.channel_order = channel_order or self.channel_order
        self.num_channels = num_channels or self.num_channels
        self.rf_api_host = rf_api_host or self.rf_api_host

    def create_local(self, tmp_dir):
        pass

    def create_source(self, tmp_dir, crs_transformer, extent, class_map):
        pass

    def for_prediction(self, image_uri):
        pass


class RfRasterSourceConfigBuilder(ConfigBuilder):

    _properties = [
        "project_id",
        "project_layer_id",
        "refresh_token",
        "channel_order",
        "num_channels",
        "rf_api_host",
    ]
    config_class = RfRasterSourceConfig
    T = TypeVar("T")

    def __init__(self):
        super(ConfigBuilder, self).__init__()
        self.rf_api_host = "app.staging.rasterfoundry.com"

    def with_property(self, property_name: str, property_value: T):
        b = deepcopy(self)
        setattr(b, property_name, property_value)
        return b

    @property
    def config(self):
        return {
            k: getattr(self, k)
            for k in self._properties
            if getattr(self, k) is not None
        }

    def from_proto(self, msg):
        return (
            self.with_project_id(msg.project_id)
            .with_project_layer_id(msg.project_layer_id)
            .with_refresh_token(msg.refresh_token)
            .with_channel_order(msg.channel_order)
            .with_num_channels(msg.num_channels)
            .with_rf_api_host(msg.rf_api_host)
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