import requests

from mypy.types import Optional
from uuid import UUID


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

    base_params = {"annotationGroup": annotation_group_id, "pageSize": 100, "page": 0}

    geojson = make_request(base_params)

    while geojson["hasNext"]:
        params["page"] += 1
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
