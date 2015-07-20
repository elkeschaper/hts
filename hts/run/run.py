# (C) 2015 Elke Schaper

"""
    :synopsis: The Run Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import configobj
import logging
import os
import pickle
import re

from hts.qc import qc
from hts.run import run_io
from hts.plate import plate
from hts.plate_layout import plate_layout
from hts.protocol import protocol


LOG = logging.getLogger(__name__)


class Run:

    """ ``Run`` describes all information connected to one run of a high
        throughput screening experiment

    Attributes:
        name (str): Name of the run
        plates (list of ``Plate``): List of ``Plate`` instances
        width (int): Width of the plates
        height (int): Height of the plates
        _protocol (``Protocol``): ``Protocol`` instance
        _platelayout (``PlateLayout``): ``PlateLayout`` instance
        _qc (dict of dict of ``QualityControl`` instance): A collection of ``QualityControl`` instance
        raw_qc (``QualityControl``): ``QualityControl`` instance - NEEDED?
        net_qc (``QualityControl``): ``QualityControl`` instance - NEEDED?
        experimenter (str): Name of the experimenter
        experimenter (str): Mail adress of the experimenter


    ..todo:: Implement me :)
    """

    def __str__(self):
        """
            Create string for Run instance.
        """
        try:
            run = ("<Run instance>\nNumber of plates: {}\nwidth: {}\nheight: {}"
                "".format(len(self.plates), self.width, self.height))
        except:
            run = "<Run instance>"
            LOG.warning("Could not create string of Run instance.")

        return run


    def __init__(self, plates, **kwargs):

        self.plates = plates
        # Later: Check if all plates are of the same height and length
        self.width = self.plates[0].width
        self.height = self.plates[0].height
        if "protocol" in kwargs:
            param = kwargs.pop('protocol')
            if not type(param) == configobj.Section:
                raise Exception("param for protocol is not of type "
                    "configobj.Section: {}, {}".format(param, type(param)))
            self.protocol(path = param['path'], format = param['format'])
        if "plate_layout" in kwargs:
            param = kwargs.pop('plate_layout')
            if not type(param) == configobj.Section:
                raise Exception("param for plate_layout is not of type "
                    "configobj.Section: {}, {}".format(param, type(param)))
            self.plate_layout(path = param['path'], format = param['format'])

        # Save all other kwargs simply as attributes.
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

        # Extract plate numbering for multiple plates and set index for each plate.
        plate_tags = [i.name for i in self.plates]
        plate_tag_numbers = [re.findall("(\d+)", i) for i in plate_tags]
        plate_tag_numbers_t = [list(i) for i in zip(*plate_tag_numbers)]
        for i in plate_tag_numbers_t:
            if len(set(i)) == len(plate_tags):
                plate_indices = i
                break
        else:
            raise Exception("No plate numbering is informative: {}. {}."
                    "".format(plate_tags, plate_tag_numbers_t))

        # Set index for each plate.
        for i_plate, plate_index in zip(self.plates, plate_indices):
            i_plate.index = plate_index


    def create(origin, path, format = None, dir = False):
        """ Create ``Run`` instance.

        Create ``Run`` instance.

        Args:
            origin (str):  At current only "config" or "plates"
            format (str):  Format of the origin, at current not specified
            path (str): Path to input file or directory

            dir (Bool): True if all files in directory shall be read, else false.

        .. todo:: Write checks for ``format`` and ``path``.
        """

        if dir == True:
            file = os.listdir(path)
        else:
            path, file = os.path.split(path)

        if origin == 'config':
            return Run.create_from_config(path, file)
        if origin == 'envision':
            return Run.create_from_envision(path, file)
        elif origin == 'pickle':
            with open(file, 'rb') as fh:
                return pickle.load(fh)
        else:
            raise Exception("The combination of origin: {} and format: {} is "
                            "not implemented in "
                            "Run.create()".format(origin, format))


    def create_from_config(path, file):
        """ Read config and use data to create `Run` instance.

        Read config and use data to create `Run` instance.

        Args:
            path (str): Path to input configobj file
            file (str): Filename of configobj file

        .. todo:: Write checks if path and file exists when necessary.
        """

        config = configobj.ConfigObj(os.path.join(path, file), stringify=True)
        if "plate_source" in config:
            config_ps = config["plate_source"]
            plates = [plate.Plate.create(path=os.path.join(config_ps["path"], i), format=config_ps['format']) for i in config_ps["filenames"]]
        else:
            raise Exception("plate_source is not defined in config file: {}"
                            "".format(os.path.join(path, file)))
        return Run(plates = plates, **config)


    def create_from_envision(path, file):
        """ Read envision data and create `Run` instance.

        Read envision data and create `Run` instance.

        Args:
            path (str): Path to input configobj file
            file (str): Filename of configobj file

        .. todo:: Write checks if path and file exists when necessary.
        """

        if type(file) != list:
            file = [file]
        plates = [plate.Plate.create(os.path.join(path, i), format="envision_csv") for i in file]
        return Run(plates = plates)


    def create_qc_report(self, path):
        """ Create quality control report (.pdf) in path.

        Create quality control report (.pdf) in path.

        Args:
            path (str): Path to result quality control report file

        .. todo:: Write checks if the path exists.
        """

        self.run_qc()
        # Create pdf


    def qc(self, type, tag):
        """ Create ``QualityControl`` instance.

        Create ``QualityControl`` instance.

        Args:
            type (str): either "run" or "plate"
            tag (str): Defines either the channel (within the plate),
                or the plate (within the run)

        .. todo:: Create QC for different plate subsets (e.g. raw/net).
        .. todo:: Use function to get to plate data instead of attributes?
        """

        if not hasattr(self, '_qc'):
            self._qc = {"plate": {}, "run": {}}
        if tag in self._qc[type]:
            my_qc = self._qc[type]["tag"]
        else:
            if type == "plate":
                run_data = {i:j for i,j in self.plates[tag].raw_read_outs.items()}
                my_qc = qc.QualityControl(run_data=run_data, plate_layout=self.plate_layout(), methods=self.protocol().qc['methods'])
                my_qc.perform_qc()
            elif type == "run":
                run_data = {iPlate.name:iPlate.raw_read_outs[tag] for iPlate in self.plates}
                my_qc = qc.QualityControl(run_data=run_data, plate_layout=self.plate_layout(), methods=self.protocol().qc['methods'])
                my_qc.perform_qc()
            else:
                raise Exception("tpe: {} is not implemented in "
                            "Run.qc()".format(type))
            self._qc[type][tag] = my_qc

        return my_qc


    def plate_layout(self, path = None, format = None):
        """ Read plate_layout and attach to `Run` instance.

        Read plate_layout and attach to `Run` instance.

        Args:
            path (str): Path to input file
            format (str):  At current only "csv"

        .. todo:: Write checks if path and format exists when necessary.
        """

        if not hasattr(self, '_plate_layout'):
            if format == "csv":
                self._plate_layout = plate_layout.PlateLayout.create(path, format)
                if len(self._plate_layout.layout) != self.height or len(self._plate_layout.layout[0]) != self.width:
                    raise Exception("Plate width and length of the plate layout "
                            "({}, {}) are not the same as for the plate data ({}, {})"
                            "".format(len(self._plate_layout.layout), len(self._plate_layout.layout[0]), self.height, self.width))
            else:
                raise Exception("Format: {} is not implemented in "
                            "ScreenData.set_plate_layout()".format(format))

        return self._plate_layout


    def protocol(self, path = None, format = None):
        """ Read protocol and attach to `Run` instance.

        Read protocol and attach to `Run` instance.

        Args:
            path (str): Path to input file
            format (str):  At current only "csv"

        .. todo:: Write checks if path and format exists when necessary.
        """

        if not hasattr(self, '_protocol'):
            self._protocol = protocol.Protocol.create(path, format)
        return self._protocol


    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``Run`` instances.

        Serialize ``Run`` instance using the stated ``format``.

        Args:
            format (str):  The output format: Currently only "pickle".
            path (str): Path to output file

        .. todo:: Write checks for ``format`` and ``path``.
        """

        if format == 'pickle':
            with open(file, 'wb') as fh:
                pickle.dump(self, fh)
        elif format == 'csv':
            output = run_io.serialize_run_for_r(self)
        else:
            raise Exception('Format is unknown: {}'.format(format))

        if path:
            with open(path, 'w') as fh:
                fh.write(output)
        if return_string:
            return output