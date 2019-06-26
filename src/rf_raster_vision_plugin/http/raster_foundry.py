import requests

import logging
from mypy.types import List, Optional
from uuid import UUID


log = logging.getLogger(__name__)


def get_api_token(refresh_token: str, api_host: str) -> str:
    resp = requests.post(
        "https://{rf_api_host}/api/tokens".format(rf_api_host=api_host),
        json={"refresh_token": refresh_token},
    )
    resp.raise_for_status()
    return resp.json()["id_token"]


def get_labels(
    jwt: str,
    api_host: str,
    project_id: UUID,
    project_layer_id: UUID,
    annotation_group_id: UUID,
    window: Optional[str],
) -> dict:

    log.info(
        "Fetching labels for project %s, project layer %s, annotation group %s",
        project_id,
        project_layer_id,
        annotation_group_id,
    )

    def make_request(params):
        resp = requests.get(
            "https://{rf_api_host}/api/projects/{project_id}/layers/{layer_id}/annotations".format(
                rf_api_host=api_host, project_id=project_id, layer_id=project_layer_id
            ),
            params=params,
            headers={"Authorization": jwt},
        )
        resp.raise_for_status()
        return resp.json()

    params = {"annotationGroup": annotation_group_id, "pageSize": 100, "page": 0}

    geojson = make_request(params)

    while geojson["hasNext"]:
        params["page"] = params["page"] + 1  # type: ignore
        if params["page"] % 10 == 0 and params["page"] > 0:  # type: ignore
            log.info("Fetching page %s of labels", params["page"])
        resp = make_request(params)
        geojson["hasNext"] = resp["hasNext"]
        geojson["features"] += resp["features"]

    return geojson


def get_project(jwt: str, api_host: str, project_id: UUID) -> dict:
    resp = requests.get(
        "https://{rf_api_host}/api/projects/{project_id}".format(
            rf_api_host=api_host, project_id=project_id
        ),
        headers={"Authorization": jwt},
    )
    resp.raise_for_status()
    return resp.json()


def post_labels(
    jwt: str,
    api_host: str,
    project_id: UUID,
    project_layer_id: UUID,
    labels: List[dict],
) -> dict:
    resp = requests.post(
        "https://{rf_api_host}/api/projects/{project_id}/layers/{project_layer_id}/annotations".format(
            rf_api_host=api_host,
            project_id=project_id,
            project_layer_id=project_layer_id,
        ),
        headers={"Authorization": jwt},
        json={"features": labels},
    )
    resp.raise_for_status()
    return resp.json()


def create_annotation_group(
    jwt: str,
    api_host: str,
    project_id: UUID,
    project_layer_id: UUID,
    annotation_group_name: str,
) -> dict:
    resp = requests.post(
        "https://{rf_api_host}/api/projects/{project_id}/layers/{project_layer_id}/annotation-groups".format(
            rf_api_host=api_host,
            project_id=project_id,
            project_layer_id=project_layer_id,
        ),
        headers={"Authorization": jwt},
        json={"name": annotation_group_name, "defaultStyle": {}},
    )
    resp.raise_for_status()
    return resp.json()


def get_rf_scenes(jwt: str, api_host: str, project_id: UUID, project_layer_id: UUID):
    """Fetch all Raster Foundry scene metadata for this project layer"""
    scenes_url = "https://{api_host}/api/projects/{project_id}/layers/{layer_id}/scenes".format(
        api_host=rf_api_host,
        project_id=project_id,
        layer_id=project_layer_id,
    )
    scenes_resp = requests.get(
        scenes_url, headers={"Authorization": jwt}
    ).json()
    scenes = scenes_resp["results"]
    page = 1
    while scenes_resp["hasNext"]:
        if page % 10 == 0 and page > 0:
            log.info("Fetching page %s of scenes", page)
            scenes_resp = requests.get(
                scenes_url,
                headers={"Authorization": "Bearer " + self._token},
                params={"page": page},
            ).json()
        if len(scenes_resp["results"]) > 0:
            scenes.append(scenes_resp["results"])
            page += 1
    return scenes
