import requests
from requests.models import Response


from typing import List, Optional
from uuid import UUID


def create_project(jwt: str, api_host: str, name: str) -> dict:
    """Create a project in the Vision API

    Args:
        name (str): the project to maybe create
    """

    resp = requests.post(
        "https://{vision_api_host}/api/projects".format(vision_api_host=api_host),
        headers={"Authorization": jwt},
        json={"name": name},
    )
    resp.raise_for_status()
    return resp.json()


def create_experiment(
    jwt: str,
    api_host: str,
    name: str,
    project: UUID,
    model: str,
    model_type: str,
    task_type: str,
    status: str = "",
    files_uri: Optional[str] = None,
    config_uri: Optional[str] = None,
    class_map: dict = {},
):
    resp = requests.post(
        "https://{vision_api_host}/api/projects/{project_id}/experiments".format(
            vision_api_host=api_host, project_id=project
        ),
        headers={"Authorization": jwt},
        json={
            "name": name,
            "project": str(project),
            "model": model,
            "modelType": model_type,
            "taskType": task_type,
            "status": status,
            "filesUri": files_uri,
            "configUri": config_uri,
            "classMap": class_map,
        },
    )
    resp.raise_for_status()
    return resp.json()


def save_experiment_scores(
    jwt: str,
    api_host: str,
    vision_project_id: UUID,
    experiment_id: UUID,
    eval_item: dict,
) -> Response:
    """Save evaluation scores for an experiment

    Args:
        experiment (Experiment): the experiment to update
    """
    headers = {"Authorization": jwt}
    fetched = requests.get(
        "https://{api_host}/api/projects/{project_id}/experiments/{experiment_id}".format(
            api_host=api_host, project_id=vision_project_id, experiment_id=experiment_id
        ),
        headers=headers,
    )
    fetched.raise_for_status()
    base_experiment = fetched.json()
    base_experiment["f1Score"] = eval_item["f1"]
    base_experiment["precision"] = eval_item["precision"]
    base_experiment["recall"] = eval_item["recall"]
    resp = requests.put(
        "https://{api_host}/api/projects/{project_id}/experiments/{experiment_id}".format(
            api_host=api_host, project_id=vision_project_id, experiment_id=experiment_id
        ),
        headers=headers,
    )
    resp.raise_for_status()
    return resp


def save_scene_with_eval(
    jwt: str,
    api_host: str,
    vision_project_id: UUID,
    experiment_id: UUID,
    rf_project_id: UUID,
    rf_project_layer_id: UUID,
    source_annotation_group: UUID,
    aoi_annotation_group: Optional[UUID],
    store_annotation_group: Optional[UUID],
    scene_name: str,
    scene_type: str,
    eval_items: List[dict] = [],
) -> Response:
    if eval_items != []:
        class_stats = [x for x in eval_items if x["class_name"] != "average"]
        overall = [x for x in eval_items if x["class_name"] == "average"][0]
    else:
        class_stats = []
        overall = {}
    scene_create = {
        "sceneType": scene_type,
        "sourceProject": rf_project_id,
        "sourceProjectLayer": rf_project_layer_id,
        "sourceAnnotationGroup": source_annotation_group,
        "aoiAnnotationGroup": aoi_annotation_group,
        "storeAnnotationGroup": store_annotation_group,
        "classStatistics": class_stats,
        "f1Score": overall.get("f1"),
        "precision": overall.get("precision"),
        "recall": overall.get("recall"),
    }

    resp = requests.post(
        "https://{vision_api_host}/api/projects/{project_id}/experiments/{experiment_id}/scenes".format(
            vision_api_host=api_host,
            project_id=vision_project_id,
            experiment_id=experiment_id,
        ),
        headers={"Authorization": jwt},
        json=scene_create,
    )
    resp.raise_for_status()
    return resp
