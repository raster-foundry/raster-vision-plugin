import rastervision as rv

RF_LAYER_RASTER_SOURCE = 'RF_LAYER_RASTER_SOURCE'
RF_ANNOTATION_GROUP_LABEL_SOURCE = 'RF_ANNOTATION_GROUP_LABEL_SOURCE'
RF_ANNOTATION_GROUP_LABEL_STORE = 'RF_ANNOTATION_GROUP_LABEL_STORE'


def register_plugin(plugin_registry):
    # TODO
    plugin_registry.register_config_builder(
        rv.RASTER_SOURCE, RF_LAYER_RASTER_SOURCE, None)
    # TODO
    plugin_registry.register_config_builder(
        rv.LABEL_SOURCE, RF_ANNOTATION_GROUP_LABEL_SOURCE, None)
    # TODO
    plugin_registry.register_config_builder(
        rv.LABEL_STORE, RF_ANNOTATION_GROUP_LABEL_STORE, None)
