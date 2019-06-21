import rastervision as rv
from rastervision.core.config import ConfigBuilder
from rastervision.evaluation.evaluator_config import EvaluatorConfig
from rastervision.protos.evaluator_pb2 import EvaluatorConfig as EvaluatorConfigMsg
from google.protobuf import struct_pb2

from uuid import UUID

from ..immutable_builder import ImmutableBuilder
from .vision_evaluator import VisionObjectDetectionEvaluator

RF_RV_EVALUATOR = "RF_RV_EVALUATOR"


class VisionObjectDetectionEvaluatorConfig(EvaluatorConfig):
    _properties = [
        "project_id",
        "experiment_id",
        "refresh_token",
        "class_map",
        "output_uri",
        "rf_api_host",
        "vision_api_host",
    ]

    def __init__(
        self,
        project_id,  # type: UUID
        experiment_id,  # type: UUID
        refresh_token,  # type: str
        class_map,  # type: dict
        output_uri,  # type: str
        rf_api_host,  # type: str
        vision_api_host,  # type: str
    ):
        self.project_id = project_id
        self.experiment_id = experiment_id
        self.refresh_token = refresh_token
        self.class_map = class_map
        self.output_uri = output_uri
        self.rf_api_host = rf_api_host
        self.vision_api_host = vision_api_host

    def create_evaluator(self):
        return VisionObjectDetectionEvaluator(
            self.project_id,
            self.experiment_id,
            self.refresh_token,
            self.class_map,
            self.output_uri,
            self.rf_api_host,
            self.vision_api_host,
        )

    def to_proto(self):
        struct = struct_pb2.Struct()
        for k in self._properties:
            struct[k] = getattr(self, k)
        return EvaluatorConfigMsg(custom_config=struct)

    def report_io(self, x, y):
        pass


class VisionObjectDetectionEvaluatorConfigBuilder(ConfigBuilder, ImmutableBuilder):
    config_class = VisionObjectDetectionEvaluatorConfig
    _properties = [
        "project_id",
        "experiment_id",
        "refresh_token",
        "class_map",
        "output_uri",
        "rf_api_host",
        "vision_api_host",
    ]

    def __init__(self):
        super(ConfigBuilder, self).__init__()
        self.rf_api_host = "app.staging.rasterfoundry.com"
        self.vision_api_host = "prediction.staging.rasterfoundry.com"

    def from_proto(self, msg):
        b = super().from_proto(msg)
        return (
            b.with_project_id(msg.project_id)
            .with_experiment_id(msg.experiment_id)
            .with_refresh_token(msg.refresh_token)
            .with_class_map(msg.class_map)
            .with_output_uri(msg.output_uri)
            .with_rf_api_host(msg.rf_api_host)
            .with_vision_api_host(msg.vision_api_host)
        )

    def with_project_id(self, project_id: UUID):
        return self.with_property("project_id", project_id)

    def with_experiment_id(self, experiment_id: UUID):
        return self.with_property("experiment_id", experiment_id)

    def with_refresh_token(self, refresh_token: str):
        return self.with_property("refresh_token", refresh_token)

    def with_class_map(self, class_map: dict):
        return self.with_property("class_map", class_map)

    def with_output_uri(self, output_uri: str):
        return self.with_property("output_uri", output_uri)

    def with_rf_api_host(self, rf_api_host: str):
        return self.with_property("rf_api_host", rf_api_host)

    def with_vision_api_host(self, vision_api_host: str):
        return self.with_property("vision_api_host", vision_api_host)
