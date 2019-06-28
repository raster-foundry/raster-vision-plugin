========
Overview
========

.. start-badges

.. |version| image:: https://img.shields.io/pypi/v/rf-raster-vision-plugin.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/rf-raster-vision-plugin

.. |commits-since| image:: https://img.shields.io/github/commits-since/raster-foundry/raster-vision-plugin/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/raster-foundry/raster-vision-plugin/compare/v0.0.1...master

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/rf-raster-vision-plugin.svg
    :alt: Supported versions
    :target: https://pypi.org/project/rf-raster-vision-plugin

.. end-badges

A plugin to use Raster Foundry as a data management layer in Raster Vision

* Free software: Apache Software License 2.0

An example is included in the examples/ repository. To run the example, setup a configuration file
in `$HOME/.rastervision/production` like the following:

::
   [RASTER_FOUNDRY]
   refresh_token=<your RF production refresh token>
   project_id=7e584c31-f5d1-4a02-9428-e83006642375
   project_layer_id=1a8c1632-fa91-4a62-b33e-3a87c2ebdf16
   ground_truth_annotation_group=600c79f2-3a68-4315-abfb-3a959fe1d443
   rf_api_host=app.rasterfoundry.com
   vision_api_host=prediction.staging.rasterfoundry.com
   label_source_geojson_path=ground-truth.geojson
   train_label_store_path=train-labels.geojson
   test_label_store_path=test-labels.geojson
   validation_label_store_path=validation-labels.geojson
   eval_path=rf-exp-eval-item.json
   train_aoi_path=/opt/data/aoi-train.geojson
   test_aoi_path=/opt/data/aoi-test.geojson
   validation_aoi_path=/opt/data/aoi-validation.geojson
   [VISION_APP]
   experiment_name=very-fancy-exp
   project_name=very-fancy-project
   model_name=very good model
   [PLUGINS]
   modules=[]

The listed project / id / annotation group is accessible to anyone in the Azavea organization in the
production Raster Foundry application. You can name the file something else as long as you change the
`-p production` option passed to the `rastervision` command below. After creating your config, run
the following from the repository root:

::

   AWS_PROFILE=raster-foundry docker/run --aws
   rastervision -p production run local -e examples.object_detection.rfrv_object_detection

After the example has completed (give it a while), send artifacts to the Raster Foundry and
Vision App APIs with

::

   python examples/object_detection/post_script.py


Installation
============

::

    pip install rf-raster-vision-plugin

Documentation
=============

Development
===========
