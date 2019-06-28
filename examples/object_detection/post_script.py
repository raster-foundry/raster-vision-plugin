import json

from rastervision.rv_config import RVConfig

import raster_vision_plugin.http.raster_foundry as rf
from raster_vision_plugin.http import vision

from uuid import UUID


# TODO
# to see what these look like, `cat /tmp/rv-labels/validation-labels.geojson`
# it's pretty close already
def _object_detection_labels_to_annotations(labels: dict, annotation_group_id: UUID) -> dict:
    return


def after_experiment(tmp_dir: str, class_map: dict) -> None:
    config_instance = RVConfig.get_instance()
    rf_config = config_instance.get_subconfig('RASTER_FOUNDRY')
    vision_app_config = config_instance.get_subconfig('VISION_APP')

    token = 'Bearer ' + rf.get_api_token(rf_config('refresh_token', rf_config('rf_api_host')))

    # TODO it's not obvious to me how the label stores work. In principle I thought that
    # the validation / test stores were supposed to get new labels, but the F1 score is one
    # because they're just using the files that I put in the uris to begin with.
    # also TODO: use the real path -- this one is just the file basename
    validation_labels = json.load(open(rf_config("validation_label_store_path")))
    # TODO make the validation annotation group
    validation_scene_annotation_group = None
    rf.create_annotations(
        token,
        rf_config("rf_api_host"),
        rf_config("project_id"),
        rf_config("project_layer_id"),
        _object_detection_labels_to_annotations(validation_labels, validation_scene_annotation_group["id"])
    )

    vision_project = vision.create_project(token, rf_config("vision_api_host"), vision_app_config("project_name"))
    experiment = vision.create_experiment(token, rf_config("vision_api_host"), vision_app_config("experiment_name"),
                                          vision_app_config("model_name"),
                                          vision_app_config("model_type"),
                                          "Object Detection",
                                          "Complete",
                                          None,
                                          None,
                                          None)

    eval_item = json.load(open(rf_config("eval_path")))
    experiment_eval_item = [
        x for x in eval_item["overall"] if x["class_name"] == "average"
    ][0]
    vision.save_experiment_scores(
        token,
        rf_config("vision_api_host"),
        vision_project["id"],
        experiment["id"],
        experiment_eval_item
    )

    # throw the specific scores into scene statistics
    scene_evals = eval_item["per_scene"]
    for scene_name, evals in scene_evals:
        vision.save_scene_with_eval(
            token,
            rf_config("vision_api_host"),
            vision_project["id"],
            experiment["id"],
            rf_config("project_id"),
            rf_config("project_layer_id"),
            rf_config("ground_truth_annotation_group"),
            validation_scene_annotation_group["id"],
            scene_name,
            "VALIDATION",
            evals
        )
