.. _model:


When HTS is useful ...
======================

HTS was build to handle High-throughput screening data in line with the following model:

.. image:: images/hts_data_model.png
   :scale: 80 %
   :alt: alternate text
   :align: left


HTS was designed to handle the information flow, and allow for normalization and hit selection of well-plate based High-throughput screens with an arbitrary number of single readouts per well.
Meta information to each well, such as the tested samples, can be stored in the same way alongside.
Results of analysis steps, such as normalization steps, can be stored in the same way alongside.


... and when it is not.
=======================

HTS was not designed with image-based high throughput screening data in mind.