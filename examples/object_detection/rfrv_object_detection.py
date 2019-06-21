from examples.utils import str_to_bool
from rf_raster_vision_plugin.evaluate.config import VisionObjectDetectionEvaluatorConfigBuilder
from rf_raster_vision_plugin.raster_source.config import RfRasterSourceConfigBuilder
from rf_raster_vision_plugin.label_source.config import RfLabelSourceConfigBuilder
from rf_raster_vision_plugin.label_store.config import RfLabelStoreConfigBuilder
import rf_raster_vision_plugin.http.raster_foundry as rf
from rf_raster_vision_plugin.http import vision
import rastervision as rv
from rastervision.task.task_config import TaskConfig
from rastervision.data.dataset_config import DatasetConfig
from rastervision.data.scene_config import SceneConfig
from rastervision.experiment.experiment_config import ExperimentConfig
from rastervision.rv_config import RVConfig


class ObjectDetectionExperiments(rv.ExperimentSet):
    def exp_rfrv(self, root_uri='/tmp', test=True):
        """Object detection experiment on xView data.

        Run the data prep notebook before running this experiment. Note all URIs can be
        local or remote.

        Args:
            root_uri: (str) root directory for experiment output
            test: (bool) if True, run a very small experiment as a test and generate
                debug output
        """
        test = str_to_bool(test)
        exp_id = 'xview-vehicles'
        num_steps = 10000
        batch_size = 16
        debug = False

        # TODO get rf config values
        config_instance = RVConfig.get_instance()
        rf_config = config_instance.get_subconfig('RASTER_FOUNDRY')

        if test:
            exp_id += '-test'
            batch_size = 1
            num_steps = 1
            debug = True

        # These should all come from config
        rf_project_id = rf_config('project_id')
        rf_project_layer_id = rf_config('project_layer_id')
        refresh_token = rf_config('refresh_token')
        rf_host = rf_config('rf_api_host')
        vision_host = rf_config('vision_api_host')

        token = 'Bearer ' + rf.get_api_token(refresh_token, rf_host)
        vision_project = vision.create_project(token, vision_host, 'object detection example')
        vision_experiment = vision.create_experiment(
            token,
            vision_host,
            'object detection example',
            vision_project['id'],
            'super advanced ml model',
            'complicated and good',
            'object detection'
        )

        rs_config = RfRasterSourceConfigBuilder() \
            .with_project_id(rf_project_id) \
            .with_project_layer_id(rf_project_layer_id) \
            .with_refresh_token(refresh_token) \
            .with_channel_order([1, 2, 3]) \
            .with_num_channels(3) \
            .build()
        raster_source = rs_config.create_source('/tmp')

        label_source_config = RfLabelSourceConfigBuilder() \
            .with_annotation_group('59388cf6-5105-467c-a8f3-f098055be8f0') \
            .with_project_id(rf_project_id) \
            .with_project_layer_id(rf_project_layer_id) \
            .with_refresh_token(refresh_token) \
            .with_crs_transformer(raster_source.get_crs_transformer()) \
            .build()
        label_source = label_source_config.create_source()

        label_store_config = RfLabelStoreConfigBuilder() \
            .with_annotation_group('59388cf6-5105-467c-a8f3-f098055be8f0') \
            .with_project_id(rf_project_id) \
            .with_project_layer_id(rf_project_layer_id) \
            .with_refresh_token(refresh_token) \
            .with_crs_transformer(raster_source.get_crs_transformer()) \
            .with_class_map(label_source._class_map) \
            .build()

        task_config = TaskConfig.builder(rv.OBJECT_DETECTION) \
            .with_chip_size(200) \
            .with_classes({
                '870e82d4-0063-44f4-8a14-950266b23619': (1, 'red')
            }).build()

        scene_config = SceneConfig.builder() \
            .with_task(task_config) \
            .with_raster_source(rs_config) \
            .with_label_source(label_source_config) \
            .with_label_store(label_store_config) \
            .with_id('example scene') \
            .build()

        dataset_config = DatasetConfig.builder() \
            .with_train_scenes([scene_config]) \
            .with_validation_scenes([scene_config]) \
            .with_test_scenes([scene_config]) \
            .build()

        evaluator = VisionObjectDetectionEvaluatorConfigBuilder() \
            .with_project_id(vision_project['id']) \
            .with_experiment_id(vision_experiment['id']) \
            .with_refresh_token(refresh_token) \
            .with_class_map(label_source._class_map) \
            .with_output_uri('/tmp') \
            .build()

        backend_config = rv.BackendConfig.builder(rv.TF_OBJECT_DETECTION) \
            .with_task(task_config) \
            .with_debug(debug) \
            .with_batch_size(batch_size) \
            .with_num_steps(num_steps) \
            .with_model_defaults(rv.SSD_MOBILENET_V1_COCO) \
            .build()

        # then create an experiment config that uses the evaluator and the task and the dataset
        experiment_config = ExperimentConfig.builder() \
            .with_id('testexperiment') \
            .with_root_uri('/tmp') \
            .with_task(task_config) \
            .with_backend(backend_config) \
            .with_dataset(dataset_config) \
            .with_evaluator(evaluator) \
            .build()

        return experiment_config


if __name__ == '__main__':
    rv.main()
