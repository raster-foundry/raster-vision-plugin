import json
import os
from examples.utils import str_to_bool
import rf_raster_vision_plugin.http.raster_foundry as rf
import rastervision as rv
from rastervision.data.raster_source.rasterio_source_config import RasterioSourceConfig
from rastervision.data.label_source.object_detection_label_source_config import ObjectDetectionLabelSourceConfig
from rastervision.data.label_store.object_detection_geojson_store_config import ObjectDetectionGeoJSONStoreConfig
from rastervision.evaluation.object_detection_evaluator_config import ObjectDetectionEvaluatorConfig
from rastervision.rv_config import RVConfig
from everett.manager import NamespacedConfig
import numpy as np
from urllib.parse import unquote

words = [x.strip() for x in open('/opt/plugin/american-english', 'r').readlines()
         if "'" not in x]
random_name = '-'.join(np.random.choice(words, 2))
print('***************************')
print('Experiment name is: ', random_name)
print('***************************')


def _to_rv_feature(annotation: dict, class_map: dict) -> dict:
    """Convert the geojson from Raster Foundry's API into the minimum dict required by Raster Vision
    """

    return {
        "geometry": annotation["geometry"],
        "properties": {"class_id": class_map[annotation["properties"]["label"]]},
    }


def setup(tmp_dir: str, rf_config: NamespacedConfig, name: str) -> dict:
    rf_project_id = rf_config('project_id')
    rf_project_layer_id = rf_config('project_layer_id')
    refresh_token = rf_config('refresh_token')
    rf_host = rf_config('rf_api_host')
    ground_truth_annotation_group = rf_config('ground_truth_annotation_group')

    token = 'Bearer ' + rf.get_api_token(refresh_token, rf_host)
    rf_scenes = rf.get_rf_scenes(token, rf_host, rf_project_id, rf_project_layer_id)
    project = rf.get_project(token, rf_host, rf_project_id)
    colors = ["red", "green", "blue", "yellow"]
    class_map = {
        item["id"]: idx + 1 for idx, item in enumerate(project["extras"]["annotate"]["labels"])
    }
    labels = rf.get_labels(
        token,
        rf_host,
        rf_project_id,
        rf_project_layer_id,
        ground_truth_annotation_group,
        None
    )

    geojson = {
        "features": [
            _to_rv_feature(feat, class_map) for feat in labels["features"]
        ]
    }
    for path in ["label_source_geojson_path",
                 "train_label_store_path",
                 "test_label_store_path",
                 "validation_label_store_path"]:
        geojson_path = os.path.join(tmp_dir, 'rv-labels', rf_config(path))
        with open(geojson_path, 'w') as outf:
            outf.write(json.dumps(geojson))

    rs_config_builder = RasterioSourceConfig.builder(rv.RASTERIO_SOURCE).with_uris(
        [unquote(x["ingestLocation"]) for x in rf_scenes]
    ).with_channel_order([0, 1, 2])
    return {
        "raster_source_builder": rs_config_builder,
        "task_class_map": {
            k: (v, colors[v - 1]) for k, v in class_map.items()
        }
    }


class ObjectDetectionExperiments(rv.ExperimentSet):
    def exp_rfrv(self, root_uri="/tmp", test=True):
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

        config_instance = RVConfig.get_instance()
        rf_config = config_instance.get_subconfig('RASTER_FOUNDRY')

        if test:
            exp_id += '-test'
            batch_size = 1
            num_steps = 1
            debug = True

        init = setup(root_uri, rf_config, random_name)

        rs_config = init["raster_source_builder"].with_stats_transformer().build()
        label_source_config = ObjectDetectionLabelSourceConfig.builder(rv.OBJECT_DETECTION) \
            .with_uri(os.path.join(root_uri, 'rv-labels', rf_config("label_source_geojson_path"))) \
            .build()

        base_store_builder = ObjectDetectionGeoJSONStoreConfig.builder(rv.OBJECT_DETECTION_GEOJSON)

        train_label_store_config = base_store_builder \
            .with_uri(os.path.join(root_uri, 'rv-labels', rf_config("train_label_store_path"))) \
            .build()
        validation_label_store_config = base_store_builder \
            .with_uri(os.path.join(root_uri, 'rv-labels', rf_config("validation_label_store_path"))) \
            .build()
        test_label_store_config = base_store_builder \
            .with_uri(os.path.join(root_uri, 'rv-labels', rf_config("test_label_store_path"))) \
            .build()

        task_config = rv.TaskConfig.builder(rv.OBJECT_DETECTION) \
            .with_chip_size(200) \
            .with_classes(init["task_class_map"]) \
            .build()

        base_scene_builder = rv.SceneConfig.builder() \
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

        dataset_config = rv.DatasetConfig.builder() \
            .with_train_scenes([train_scene_config]) \
            .with_validation_scenes([validation_scene_config]) \
            .with_test_scenes([test_scene_config]) \
            .build()

        evaluator = ObjectDetectionEvaluatorConfig.builder(rv.OBJECT_DETECTION_EVALUATOR) \
            .with_output_uri(os.path.join(root_uri, 'rv-evaluation')) \
            .with_class_map(init["task_class_map"]) \
            .build()

        backend_config = rv.BackendConfig.builder(rv.TF_OBJECT_DETECTION) \
            .with_task(task_config) \
            .with_debug(debug) \
            .with_batch_size(batch_size) \
            .with_num_steps(num_steps) \
            .with_model_defaults(rv.SSD_MOBILENET_V1_COCO) \
            .build()

        # then create an experiment config that uses the evaluator and the task and the dataset
        experiment_config = rv.ExperimentConfig.builder() \
            .with_id('testexperiment') \
            .with_root_uri(root_uri) \
            .with_task(task_config) \
            .with_backend(backend_config) \
            .with_dataset(dataset_config) \
            .with_evaluator(evaluator) \
            .with_stats_analyzer() \
            .build()

        return experiment_config


if __name__ == '__main__':
    rv.main()
