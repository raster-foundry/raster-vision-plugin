from rastervision.core import Box
from rastervision.data.crs_transformer import CRSTransformer
from rastervision.data.crs_transformer.rasterio_crs_transformer import (
    RasterioCRSTransformer,
)
from rastervision.data.label.object_detection_labels import ObjectDetectionLabels

from mypy.types import List
from uuid import UUID


def annotation_features_from_labels(
    labels: ObjectDetectionLabels,
    crs_transformer: CRSTransformer,
    annotation_group: UUID,
    inverted_class_map: dict,
) -> List[dict]:
    # Build a new RasterioCRSTransformer, which defaults to 4326
    lat_lng_xform = RasterioCRSTransformer(
        crs_transformer.transform, crs_transformer.image_proj.srs
    )
    box_list = labels.boxlist
    boxes = [
        Box.from_npbox(npbox)
        .reproject(lat_lng_xform.pixel_to_map)
        .geojson_coordinates()
        for npbox in box_list.data["boxes"]
    ]

    return [
        {
            "geometry": {"type": "Polygon", "coordinates": [box]},
            "properties": {
                "owner": None,
                "label": inverted_class_map[class_id],
                "description": None,
                "machineGenerated": True,
                "confidence": score,
                "quality": None,
                "annotationGroup": annotation_group,
                "labeledBy": None,
                "verifiedBy": None,
            },
        }
        for box, class_id, score in zip(
            boxes, labels.boxlist.data["classes"], labels.boxlist.data["scores"]
        )
    ]
