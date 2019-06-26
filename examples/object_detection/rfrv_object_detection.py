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
from rastervision.data.raster_source.rasterio_source_config import RasterioSourceConfig
from rastervision.data.scene_config import SceneConfig
from rastervision.data.raster_transformer.stats_transformer_config import StatsTransformerConfig
from rastervision.experiment.experiment_config import ExperimentConfig
from rastervision.rv_config import RVConfig
import numpy as np
import os
from urllib.parse import unquote


words = [x.strip() for x in open('/opt/plugin/american-english', 'r').readlines()
         if "'" not in x]
short_hash = '-'.join(np.random.choice(words, 2))
print('***************************')
print('Tmp directory is: ', short_hash)
print('***************************')
tmp_dir = '/tmp/' + short_hash
os.mkdir(tmp_dir)


class ObjectDetectionExperiments(rv.ExperimentSet):
    def exp_rfrv(self, root_uri=tmp_dir, test=True):
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

        RVConfig.set_tmp_dir(tmp_dir)
        config_instance = RVConfig.get_instance()
        rf_config = config_instance.get_subconfig('RASTER_FOUNDRY')

        if test:
            exp_id += '-test'
            batch_size = 1
            num_steps = 1
            debug = True

        rf_project_id = rf_config('project_id')
        rf_project_layer_id = rf_config('project_layer_id')
        refresh_token = rf_config('refresh_token')
        rf_host = rf_config('rf_api_host')
        vision_host = rf_config('vision_api_host')
        ground_truth_annotation_group = rf_config('ground_truth_annotation_group')

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
        rf_scenes = rf.get_rf_scenes(token, rf_host, rf_project_id, rf_project_layer_id)

        train_store_annotation_group = rf.create_annotation_group(
            token,
            rf_host,
            rf_project_id,
            rf_project_layer_id,
            'od-example-train-{}'.format(short_hash)
        )['id']
        test_store_annotation_group = rf.create_annotation_group(
            token,
            rf_host,
            rf_project_id,
            rf_project_layer_id,
            'od-example-test-{}'.format(short_hash)
        )['id']
        validation_store_annotation_group = rf.create_annotation_group(
            token,
            rf_host,
            rf_project_id,
            rf_project_layer_id,
            'od-example-validation-{}'.format(short_hash)
        )['id']

        rs_config = RasterioSourceConfig.builder(rv.RASTERIO_SOURCE) \
            .with_uris([unquote(x["ingestLocation"]) for x in rf_scenes]) \
            .build()
        raster_source = rs_config.create_source(tmp_dir)

        label_source_config = RfLabelSourceConfigBuilder() \
            .with_annotation_group(ground_truth_annotation_group) \
            .with_project_id(rf_project_id) \
            .with_project_layer_id(rf_project_layer_id) \
            .with_refresh_token(refresh_token) \
            .with_crs_transformer(raster_source.get_crs_transformer()) \
            .build()
        label_source = label_source_config.create_source()

        base_store_builder = RfLabelStoreConfigBuilder() \
            .with_project_id(rf_project_id) \
            .with_project_layer_id(rf_project_layer_id) \
            .with_refresh_token(refresh_token) \
            .with_crs_transformer(raster_source.get_crs_transformer()) \
            .with_class_map(label_source._class_map)

        train_label_store_config = base_store_builder \
            .with_annotation_group(train_store_annotation_group) \
            .build()
        test_label_store_config = base_store_builder \
            .with_annotation_group(test_store_annotation_group) \
            .build()
        validation_label_store_config = base_store_builder \
            .with_annotation_group(validation_store_annotation_group) \
            .build()

        task_config = TaskConfig.builder(rv.OBJECT_DETECTION) \
            .with_chip_size(200) \
            .with_classes({
                'fb3bb8b9-478b-4106-b13d-d7410aa2cb60': (1, 'red')
            }).build()

        base_scene_builder = SceneConfig.builder() \
            .with_task(task_config) \
            .with_raster_source(rs_config)

        train_scene_config = base_scene_builder \
            .with_label_source(label_source_config) \
            .with_label_store(train_label_store_config) \
            .with_id('example train scene') \
            .build()
        validation_scene_config = base_scene_builder \
            .with_label_source(label_source_config) \
            .with_label_store(validation_label_store_config) \
            .with_id('example validation scene') \
            .build()
        test_scene_config = base_scene_builder \
            .with_label_source(label_source_config) \
            .with_label_store(test_label_store_config) \
            .with_id('example test scene') \
            .build()

        dataset_config = DatasetConfig.builder() \
            .with_train_scenes([train_scene_config]) \
            .with_validation_scenes([validation_scene_config]) \
            .with_test_scenes([test_scene_config]) \
            .build()

        evaluator = VisionObjectDetectionEvaluatorConfigBuilder() \
            .with_project_id(vision_project['id']) \
            .with_experiment_id(vision_experiment['id']) \
            .with_refresh_token(refresh_token) \
            .with_class_map(label_source._class_map) \
            .with_output_uri(tmp_dir) \
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
            .with_root_uri(tmp_dir) \
            .with_task(task_config) \
            .with_backend(backend_config) \
            .with_dataset(dataset_config) \
            .with_evaluator(evaluator) \
            .with_stats_analyzer() \
            .build()

        return experiment_config


if __name__ == '__main__':
    rv.main()
