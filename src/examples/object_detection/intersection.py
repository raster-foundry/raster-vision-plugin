from shapely.geometry import shape, mapping

from rastervision.utils.files import file_to_json, json_to_file


subset_path = '/opt/data/cloudfactory/florence/subset.geojson'
labels_path = '/opt/data/cloudfactory/florence/labels.json'
intersection_path = '/opt/data/cloudfactory/florence/tiny-labels.json'

subset_json = file_to_json(subset_path)
subset_geom = shape(subset_json['features'][0]['geometry'])

labels_json = file_to_json(labels_path)
new_features = []
for f in labels_json['features']:
    g = shape(f['geometry']).buffer(0)
    if g.intersects(subset_geom):
        new_f = dict(f)
        new_f['geometry'] = mapping(g)
        new_features.append(new_f)

json_to_file({'type': 'FeatureCollection', 'features': new_features}, intersection_path)