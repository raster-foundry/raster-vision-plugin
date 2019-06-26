from google.protobuf import struct_pb2
from rasterio import Affine
from rasterio.crs import CRS
from rastervision.core.config import ConfigBuilder
from rastervision.data.crs_transformer import RasterioCRSTransformer
from rastervision.data.label_store.label_store_config import LabelStoreConfig
from rastervision.protos.label_store_pb2 import LabelStoreConfig as LabelStoreConfigMsg
from .rf_annotation_group_label_store import RfAnnotationGroupLabelStore
from ..immutable_builder import ImmutableBuilder

import logging
from typing import Dict
from uuid import UUID


log = logging.getLogger(__name__)

RF_ANNOTATION_GROUP_LABEL_STORE = "RF_ANNOTATION_GROUP_LABEL_STORE"


class RfLabelStoreConfig(LabelStoreConfig):
    store_type = "RF_ANNOTATION_GROUP_LABEL_STORE"

    _properties = [
        "annotation_group",
        "project_id",
        "project_layer_id",
        "refresh_token",
        "crs_transformer",
        "class_map",
        "rf_api_host",
        "store_type",
    ]

    def __init__(
        self,
        annotation_group,  # type: UUID
        project_id,  # type: UUID
        project_layer_id,  # type: UUID
        refresh_token,  # type: str
        crs_transformer,  # type: RasterioCRSTransformer
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

    def for_prediction(self, label_uri):
        test = self.to_builder()
        print('Builder type: ', type(test))
        return self.to_builder() \
                   .with_uri(label_uri) \
                   .build()

    def report_io(self, x, y):
        pass

    def to_proto(self):
        b = super().to_proto()
        struct = struct_pb2.Struct()
        for k in self._properties:
            if k != "crs_transformer":
                struct[k] = getattr(self, k)
            else:
                xform = self.crs_transformer.transform
                struct["map_crs"] = self.crs_transformer.map_crs
                struct["image_crs"] = 'epsg:{}'.format(self.crs_transformer.image_crs.to_epsg())
                struct["transform"] = [xform.a, xform.b, xform.c, xform.d, xform.e, xform.f]
        b.MergeFrom(LabelStoreConfigMsg(custom_config=struct))
        return b


class RfLabelStoreConfigBuilder(ConfigBuilder, ImmutableBuilder):
    store_type = "RF_ANNOTATION_GROUP_LABEL_STORE"
    config_class = RfLabelStoreConfig
    _properties = [
        "annotation_group",
        "project_id",
        "project_layer_id",
        "refresh_token",
        "crs_transformer",
        "class_map",
        "rf_api_host",
        "store_type",
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
            .with_crs_transformer_from_msg(msg)
            .with_rf_api_host(msg.custom_config["rf_api_host"])
            .with_class_map(msg.custom_config["class_map"])
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

    def with_crs_transformer_from_msg(self, msg: LabelStoreConfigMsg):
        custom_config = msg.custom_config
        transform = Affine(*custom_config['transform'])
        crs_transformer = RasterioCRSTransformer(transform=transform, image_crs=CRS({'init': custom_config["image_crs"]}), map_crs=custom_config["map_crs"])
        return self.with_property("crs_transformer", crs_transformer)

    def with_crs_transformer(self, crs_transformer: RasterioCRSTransformer):
        return self.with_property("crs_transformer", crs_transformer)

    def with_rf_api_host(self, rf_api_host: str):
        return self.with_property("rf_api_host", rf_api_host)

    def with_store_type(self, store_type: str):
        return self.with_property("store_type", store_type)
