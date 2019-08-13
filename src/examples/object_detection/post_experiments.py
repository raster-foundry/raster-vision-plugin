import json
from uuid import UUID
from os.path import join

from rastervision.rv_config import RVConfig
from rastervision.utils.files import file_to_json

import rf_raster_vision_plugin.http.raster_foundry as rf
from rf_raster_vision_plugin.http import vision


def _object_detection_labels_to_annotations(labels: dict, annotation_group_id: UUID, class_map: dict) -> dict:
    features = []
    for f in labels['features']:
        label = class_map[f['properties']['class_id']]
        new_f = {
            'type': 'Feature',
            'properties': {
                'label': label,
                'description': None,
                'machineGenerated': True,
                'confidence': f['properties']['score'],
                'quality': None,
                'annotationGroup': annotation_group_id,
                'taskId': None
            },
            'geometry': f['geometry']
        }
        features.append(new_f)

    return {
        'type': 'FeatureCollection',
        'features': features
    }

def post_experiments(rv_profile, vision_project_id, experiment_configs):
    config_instance = RVConfig(profile=rv_profile)
    rf_config = config_instance.get_subconfig('RASTER_FOUNDRY')
    vision_app_config = config_instance.get_subconfig('VISION_APP')
    rf_token = 'Bearer ' + rf.get_api_token(rf_config('refresh_token'), rf_config('rf_api_host'))
    vision_token = 'Bearer ' + vision.get_api_token(vision_app_config('refresh_token'), rf_config('vision_api_host'))

    for exp_config in experiment_configs:
        print('Posting experiment: ', exp_config['name'])
        project = rf.get_project(rf_token, rf_config('rf_api_host'), exp_config['rf_project_id'])
        class_map = {
            idx + 1: item['id'] for idx, item in enumerate(project['extras']['annotate']['labels'])
        }

        # Store validation predictions in RF.
        validation_labels = file_to_json(exp_config['validation_labels_uri'])
        validation_scene_annotation_group = rf.create_annotation_group(
            rf_token, rf_config('rf_api_host'), exp_config['rf_project_id'],
            exp_config['rf_project_layer_id'], 'validation')
        validation_annotations = _object_detection_labels_to_annotations(
            validation_labels, validation_scene_annotation_group['id'], class_map)
        resp = rf.create_annotations(
            rf_token,
            rf_config('rf_api_host'),
            exp_config['rf_project_id'],
            exp_config['rf_project_layer_id'],
            validation_annotations
        )
        store_annotation_group = resp['features'][0]['properties']['annotationGroup']

        # Create experiment in Vision app.
        exp_class_map = [
            {
                'labelId': label['id'],
                'classId': idx+1,
                'className': label['name'],
                'colorHexCode': label['colorHexCode']
            }
            for idx, label in enumerate(project['extras']['annotate']['labels'])]

        experiment = vision.create_experiment(
            vision_token,
            rf_config('vision_api_host'),
            exp_config['name'],
            vision_project_id,
            exp_config['model_name'],
            exp_config['model_type'],
            'Object Detection',
            'Complete',
            None,
            None,
            exp_class_map)

        # Post overall eval scores.
        eval_item = file_to_json(exp_config['eval_uri'])
        experiment_eval_item = [
            x for x in eval_item['overall'] if x['class_name'] == 'average'
        ][0]
        vision.save_experiment_scores(
            vision_token,
            rf_config('vision_api_host'),
            vision_project_id,
            experiment['id'],
            experiment_eval_item
        )

        aoi_annotation_group_id = None

        # Post eval scores for each scene.
        scene_evals = eval_item['per_scene']
        for scene_name, evals in scene_evals.items():
            vision.save_scene_with_eval(
                vision_token,
                rf_config('vision_api_host'),
                vision_project_id,
                experiment['id'],
                exp_config['rf_project_id'],
                exp_config['rf_project_layer_id'],
                exp_config['rf_ground_truth_annotation_group'],
                aoi_annotation_group_id,
                store_annotation_group,
                scene_name,
                'VALIDATION',
                evals
            )

if __name__ == '__main__':
    rv_profile = 'production'
    # Created by running create_project.py
    vision_project_id = 'deadb0fa-0dbd-4fb8-bd2e-a960ba76398a'

    # TODO handle multiple validation scenes per project
    # TODO handle training scenes

    rf_project_id = '7e584c31-f5d1-4a02-9428-e83006642375'
    rf_project_layer_id = '1a8c1632-fa91-4a62-b33e-3a87c2ebdf16'
    rf_ground_truth_annotation_group = '600c79f2-3a68-4315-abfb-3a959fe1d443'

    experiments = [
        {
            'name': 'florence_bs',
            'model_name': 'my model name',
            'model_type': 'ssd_mobilenet',
            'rf_project_id': rf_project_id,
            'rf_project_layer_id': rf_project_layer_id,
            'rf_ground_truth_annotation_group': rf_ground_truth_annotation_group,
            'validation_labels_uri': 's3://raster-vision-lf-dev/cloudfactory/florence/remote-output/predict/florence-object-detection/tiny-validation.json',
            'eval_uri': 's3://raster-vision-lf-dev/cloudfactory/florence/remote-output/eval/florence-object-detection/eval.json',
        },
        {
            'name': 'florence_bs16',
            'model_name': 'my model name',
            'model_type': 'ssd_mobilenet',
            'rf_project_id': rf_project_id,
            'rf_project_layer_id': rf_project_layer_id,
            'rf_ground_truth_annotation_group': rf_ground_truth_annotation_group,
            'validation_labels_uri': 's3://raster-vision-lf-dev/cloudfactory/florence/remote-output/predict/florence-object-detection-bs16/tiny-validation.json',
            'eval_uri': 's3://raster-vision-lf-dev/cloudfactory/florence/remote-output/eval/florence-object-detection-bs16/eval.json',
        },
        {
            'name': 'florence_bs4',
            'model_name': 'my model name',
            'model_type': 'ssd_mobilenet',
            'rf_project_id': rf_project_id,
            'rf_project_layer_id': rf_project_layer_id,
            'rf_ground_truth_annotation_group': rf_ground_truth_annotation_group,
            'validation_labels_uri': 's3://raster-vision-lf-dev/cloudfactory/florence/remote-output/predict/florence-object-detection-bs4/tiny-validation.json',
            'eval_uri': 's3://raster-vision-lf-dev/cloudfactory/florence/remote-output/eval/florence-object-detection-bs4/eval.json',
        },
    ]

    post_experiments(rv_profile, vision_project_id, experiments)