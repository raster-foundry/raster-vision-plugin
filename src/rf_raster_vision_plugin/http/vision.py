import requests
from requests.models import Response
from rastervision.evaluation.class_evaluation_item import ClassEvaluationItem


from typing import Optional
from uuid import UUID


def create_project(jwt: str, api_host: str, name: str) -> Response:
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


def fetch_project(project_id: UUID) -> Response:
    """Fetch an existing project from the Vision API

    Args:
        project_id (Option[UUID]): the id of the project to fetch
    """

    pass


def save_experiment_scores(
    jwt: str,
    api_host: str,
    vision_project_id: UUID,
    experiment_id: UUID,
    eval_item: ClassEvaluationItem,
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
    return requests.put(
        "https://{api_host}/api/projects/{project_id}/experiments/{experiment_id}".format(
            api_host=api_host, project_id=vision_project_id, experiment_id=experiment_id
        ),
        headers=headers,
    )


def save_scene_with_eval(
    jwt: str,
    api_host: str,
    vision_project_id: UUID,
    experiment_id: UUID,
    scene_name: str,
    eval_item: ClassEvaluationItem,
) -> Response:
    # TODO this creates a scene with the given name and updates its eval info. It's basically like the
    # save scores function for experiments above
    return
