import os
from os.path import join

import rastervision as rv
from examples.utils import str_to_bool, save_image_crop

class FlorenceObjectDetectionExperiments(rv.ExperimentSet):
    def exp_main(self, raw_uri, processed_uri, root_uri, test=False):
        """Object detection on Florence, AL car dataset.

        Args:
            raw_uri: (str) directory of raw data
            processed_uri: (str) directory of processed data
            root_uri: (str) root directory for experiment output
            test: (bool) if True, run a very small experiment as a test and generate
                debug output
        """
        test = str_to_bool(test)
        exp_id = 'florence-object-detection-bs4'
        num_steps = 50000
        batch_size = 4
        debug = False

        if test:
            exp_id += '-test'
            num_steps = 1
            batch_size = 1
            debug = True

        task = rv.TaskConfig.builder(rv.OBJECT_DETECTION) \
                            .with_chip_size(300) \
                            .with_classes({
                                'truck': (1, 'red'),
                                'bus': (2, 'green'),
                                'vehicle': (3, 'blue')
                            }) \
                            .with_chip_options(neg_ratio=1.0,
                                               ioa_thresh=0.8) \
                            .with_predict_options(merge_thresh=0.1,
                                                  score_thresh=0.5) \
                            .build()

        backend = rv.BackendConfig.builder(rv.TF_OBJECT_DETECTION) \
                                  .with_task(task) \
                                  .with_model_defaults(rv.SSD_MOBILENET_V1_COCO) \
                                  .with_debug(debug) \
                                  .with_batch_size(batch_size) \
                                  .with_num_steps(num_steps) \
                                  .build()

        def make_scene(split):
            raster_uri = join(raw_uri, 'tiny-image.tif')
            label_uri = join(raw_uri, 'tiny-labels.json')

            return rv.SceneConfig.builder() \
                                 .with_id(split) \
                                 .with_task(task) \
                                 .with_aoi_uris([join(raw_uri, '{}.geojson'.format(split))]) \
                                 .with_raster_source(raster_uri, channel_order=[0, 1, 2]) \
                                 .with_label_source(label_uri) \
                                 .build()

        train_scenes = [make_scene('tiny-train')]
        val_scenes = [make_scene('tiny-validation')]

        dataset = rv.DatasetConfig.builder() \
                                  .with_train_scenes(train_scenes) \
                                  .with_validation_scenes(val_scenes) \
                                  .build()

        experiment = rv.ExperimentConfig.builder() \
                                        .with_id(exp_id) \
                                        .with_root_uri(root_uri) \
                                        .with_task(task) \
                                        .with_backend(backend) \
                                        .with_dataset(dataset) \
                                        .build()

        return experiment


if __name__ == '__main__':
    rv.main()