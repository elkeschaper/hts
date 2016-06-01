.. _config:

HTS configuration files
========================

HTS can read in config files, that contain all information on the data handling of the screen.
There are three kinds of config files, :ref:`plate layouts<plate_layout>`, :ref:`protocol configs<config_protocol>` and :ref:`run configs<config_run>`.

.. _plate_layout:

Plate layout file
---------------------------

The plate layout file provides general information on the .



.. _config_protocol:

Protocol file
---------------------------

The Protocol file defines general aspects of your HTS data handling that are applied to all your experimental runs. This can include

- Data transformations and normalizations
- Quality Control choice
- Hit selection approach

This is an example of a protocol file::

    name = my custom name

    [Global signal normalization]
        tags = preprocessing,
        method = calculate_control_normalized_signal
        data_tag_readout = my_custom_readout_tag
        negative_control_key = neg_0
        positive_control_key = pos_0
        local = False
        data_tag_normalized_readout = my_custom_normalized_readout_tag
        data_tag_pvalue_sample_vs_neg_control = my_custom_pvalue_neg_control_tag
        data_tag_pvalue_sample_vs_pos_control = my_custom_pvalue_pos_control_tag


    [Gaussian process normalization]
        tags = analysis,
        method = data_normalization.do_gaussian_process_normalization
        data_tag_readout = my_custom_normalized_readout_tag
        sample_tag_input = s
        [[rbf]]
            is_per_plate = True
            is_zigzag = False
            [[[RBF]]]
                kernel_type=RBF
                [[[[constraints]]]]
                    [[[[[lengthscale]]]]]
                        fix = 2
                    [[[[[variance]]]]]
                        fix = 1


    [Create an QC Knitr document]
        tags = qc,
        method = qc_knitr.create_report
        qc_helper_methods_path = qc_helper_methods.R
        [[Plate layout]]
            method = plate_layout
        [[1: Net FRET (unchanged)]]
            method = heat_map
            [[[knitr_options]]]
                options = "fig.height=7"
            [[[filter]]]
                y = net_fret






.. _config_run:

Run configuration file
---------------------------


The Run file defines aspects of your HTS data handling specific to individual HTS runs. This can include

- Path and data format of screen data and auxiliary data
- Path and data format of output files (for example QC and analysis files)
- Arbitrary additional information, such as the experimentator who performed the HTS run.

