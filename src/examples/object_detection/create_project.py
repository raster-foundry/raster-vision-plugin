import json
from uuid import UUID
from os.path import join

from rastervision.rv_config import RVConfig
from rastervision.utils.files import file_to_json

import rf_raster_vision_plugin.http.raster_foundry as rf
from rf_raster_vision_plugin.http import vision

def create_project(rv_profile):
    config_instance = RVConfig(profile=rv_profile)
    rf_config = config_instance.get_subconfig('RASTER_FOUNDRY')
    vision_app_config = config_instance.get_subconfig('VISION_APP')

    project_name = 'florence, alabama'
    token = 'Bearer ' + vision.get_api_token(vision_app_config('refresh_token'), rf_config('vision_api_host'))
    vision_project = vision.create_project(token, rf_config("vision_api_host"), project_name)
    print('new vision project created with id: ', vision_project['id'])
    return vision_project['id']

if __name__ == '__main__':
    rv_profile = 'production'
    create_project(rv_profile)