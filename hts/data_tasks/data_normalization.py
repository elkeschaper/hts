# (C) 2016 Elke Schaper

"""
    :synopsis: ``data_normalization`` implements methods connected to the
    readout normalization of a high throughput screening experiment

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""


def calculate_local_ssmd(run, **kwargs):
    for plate_tag, plate in run.plates.items():
        plate.calculate_local_ssmd(**kwargs)


def classify_by_cutoff(run, **kwargs):
    for plate_tag, plate in run.plates.items():
        plate.classify_by_cutoff(**kwargs)