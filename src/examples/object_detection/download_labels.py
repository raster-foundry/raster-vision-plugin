from urllib.parse import unquote

import rf_raster_vision_plugin.http.raster_foundry as rf
from rastervision.rv_config import RVConfig
from .rfrv_object_detection import _to_rv_feature


def download_labels(rf_project_id, rf_project_layer_id,
                    ground_truth_annotation_group, out_path, rv_profile=None):
    config_instance = RVConfig(profile=rv_profile)
    rf_config = config_instance.get_subconfig('RASTER_FOUNDRY')
    rf_host = rf_config('rf_api_host')
    refresh_token = rf_config('refresh_token')

    token = 'Bearer ' + rf.get_api_token(refresh_token, rf_host)

    project = rf.get_project(token, rf_host, rf_project_id)

    class_map = {
        item["id"]: idx + 1 for idx, item in enumerate(project["extras"]["annotate"]["labels"])
    }
    print(project['extras']['annotate'])

    labels = rf.get_labels(
        token,
        rf_host,
        rf_project_id,
        rf_project_layer_id,
        ground_truth_annotation_group,
        None
    )

    rf_scenes = rf.get_rf_scenes(token, rf_host, rf_project_id, rf_project_layer_id)
    print([unquote(x["ingestLocation"]) for x in rf_scenes])

    geojson = {
        "type": "FeatureCollection",
        "features": [
            _to_rv_feature(feat, class_map) for feat in labels["features"]
        ]
    }
    from rastervision.utils.files import json_to_file
    json_to_file(geojson, out_path)


if __name__ == '__main__':
    '''
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    '''

    rf_project_id = '7e584c31-f5d1-4a02-9428-e83006642375'
    rf_project_layer_id = '1a8c1632-fa91-4a62-b33e-3a87c2ebdf16'
    ground_truth_annotation_group = '600c79f2-3a68-4315-abfb-3a959fe1d443'
    out_path = '/opt/data/labels.json'
    download_labels(rf_project_id, rf_project_layer_id,
                    ground_truth_annotation_group, out_path,
                    rv_profile='production')