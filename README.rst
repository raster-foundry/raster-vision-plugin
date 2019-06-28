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

An example is included in the examples/ repository. To run the example:

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
