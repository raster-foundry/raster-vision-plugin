from ..http.vision import save_experiment_scores
from ..with_token import WithRefreshToken

from requests.models import Response
from rastervision.evaluation.object_detection_evaluator import ObjectDetectionEvaluator

from uuid import UUID


class VisionObjectDetectionEvaluator(ObjectDetectionEvaluator, WithRefreshToken):
    def __init__(
        self,
        project_id: UUID,
        experiment_id: UUID,
        refresh_token: str,
        class_map: dict,
        output_uri: str,
        rf_api_host: str,
        vision_api_host: str = "prediction.staging.rasterfoundry.com",
    ):
        self.project_id = project_id
        self.experiment_id = experiment_id
        self.set_token(rf_api_host, refresh_token)
        super(ObjectDetectionEvaluator, self).__init__(class_map, output_uri)

    def process(self, scenes, tmp_dir) -> Response:
        super(ObjectDetectionEvaluator, self).process(scenes, tmp_dir)
        return save_experiment_scores(
            self._token,
            self.vision_api_host,
            self.project_id,
            self.experiment_id,
            self.eval,
        )
