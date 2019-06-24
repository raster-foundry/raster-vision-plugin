import rastervision as rv

from .raster_source.config import RfRasterSourceConfigBuilder, RF_LAYER_RASTER_SOURCE
from .label_source.config import (
    RfLabelSourceConfigBuilder,
    RF_ANNOTATION_GROUP_LABEL_SOURCE,
)
from .label_store.config import (
    RfLabelStoreConfigBuilder,
    RF_ANNOTATION_GROUP_LABEL_STORE,
)
from .evaluate.config import (
    VisionObjectDetectionEvaluatorConfigBuilder,
    RF_RV_OBJECT_DETECTION_EVALUATOR,
)


def register_plugin(plugin_registry):
    plugin_registry.register_config_builder(
        rv.RASTER_SOURCE, RF_LAYER_RASTER_SOURCE, RfRasterSourceConfigBuilder
    )
    plugin_registry.register_config_builder(
        rv.LABEL_SOURCE, RF_ANNOTATION_GROUP_LABEL_SOURCE, RfLabelSourceConfigBuilder
    )
    plugin_registry.register_config_builder(
        rv.LABEL_STORE, RF_ANNOTATION_GROUP_LABEL_STORE, RfLabelStoreConfigBuilder
    )
    plugin_registry.register_config_builder(
        rv.EVALUATOR,
        RF_RV_OBJECT_DETECTION_EVALUATOR,
        VisionObjectDetectionEvaluatorConfigBuilder,
    )
