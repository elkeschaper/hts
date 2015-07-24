# (C) 2015 Elke Schaper

"""
    :synopsis: The Run Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import ast
import configobj
import logging
import os
import pickle
import re

from hts.qc import qc
from hts.run import run_io
from hts.readout import readout_dict
from hts.plate_layout import plate_layout
from hts.protocol import protocol


LOG = logging.getLogger(__name__)


class Run:

    """ ``Run`` describes all information connected to one run of a high
        throughput screening experiment

    Attributes:
        name (str): Name of the run
        plates (list of ``ReadoutDict``): List of ``ReadoutDict`` instances
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

        self.plates = {plate.name: plate for plate in plates}
        #Plates as list: self.plates = plates
        # Later: Check if all plates are of the same height and length
        self.width = plates[0].width
        self.height = plates[0].height
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
        self.plate_tag_numbers = [re.findall("(\d+)", i) for i in self.plates.keys()]

        plate_tag_numbers_t = [list(i) for i in zip(*self.plate_tag_numbers)]
        for i in plate_tag_numbers_t:
            if len(set(i)) == len(self.plates):
                plate_indices = i
                break
        else:
            raise Exception("No plate numbering is informative: {}. {}."
                    "".format(self.plates.keys(), plate_tag_numbers_t))

        # Set index for each plate.
        for i_plate, plate_index in zip(list(self.plates.keys()), plate_indices):
            self.plates[i_plate].index = plate_index
        self.plates = {plate.index: plate for plate in plates}


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
            plates = [readout_dict.ReadoutDict.create(path=os.path.join(config_ps["path"], i), format=config_ps['format']) for i in config_ps["filenames"]]
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
        plates = [readout_dict.ReadoutDict.create(os.path.join(path, i), format="envision_csv") for i in file]
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


    def filter(self, type, tag, subset = None):
        """ Filter run data according to type and tag.

        Filter run data according to type and tag.

        Args:
            type (str): Either per "run_wise" or per "plate_wise".
            tags (str): Defines either the readout (within the plate),
                or the plate (within the run).
            subset (list of str): Defines which plates/plate_readouts shall be included.

        Returns:
            Readout or ReadoutDict (for multiple Readouts)
        """
        #import pdb; pdb.set_trace()
        #if subset:
        #    subset = ast.literal_eval(subset)

        if type == 'run_wise':
            # Return plates across a run.
            if tag != '':
                if not subset:
                    return {index:plate.get_readout(tag) for index, plate in self.plates.items()}
                else:
                    return {index:plate.get_readout(tag) for index, plate in self.plates.items() if index in subset}
            else:
                result = {}
                for tag in list(self.plates.values)[0].read_outs.keys():
                    if not subset:
                        result[tag] =  {index:plate.get_readout(tag) for index, plate in self.plates.items()}
                    else:
                        result[tag] = {index:plate.get_readout(tag) for index, plate in self.plates.items() if index in subset}
                return result
        elif type == 'plate_wise':
            # Return plates across a plate.
            if tag != '':
                if not subset:
                    return self.plates[tag].read_outs
                else:
                    return {i:readout for i,readout in self.plates[tag].read_outs.items() if i in subset}
            else:
                result = {}
                for tag in self.plates.keys():
                    if not subset:
                        result[tag] =  self.plates[tag].read_outs
                    else:
                        result[tag] =  {i:readout for i,readout in self.plates[tag].read_outs.items() if i in subset}
                return result
        else:
            raise Exception("The type: {} is not implemented in "
                            "Run.filter()".format(type))



    def qc(self):
        """ Perform quality control and save the results

        Perform quality control and save the results

        Args:

        .. todo:: Create QC for different plate subsets (e.g. raw/net).
        .. todo:: Use function to get to plate data instead of attributes?
        """

        if hasattr(self, '_qc'):
            return self._qc
        else:
            self._qc = {"plate_wise": {}, "run_wise": {}}
            for iqc, qc_param in self.protocol().qc.items():
                LOG.info(iqc)
                LOG.info(qc_param)
                subset = self.filter(**qc_param['filter'])
                #import pdb; pdb.set_trace()
                if qc_param['filter']['tag'] == '':
                    qc_results = {i: qc.perform_qc(methods=qc_param['methods'], data=j, plate_layout=self.plate_layout()) for i,j in subset.items()}
                else:
                    qc_results = qc.perform_qc(methods=qc_param['methods'], data=subset, plate_layout=self.plate_layout())
                self._qc[iqc] = qc_results

        return self._qc


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
                    raise Exception("ReadoutDict width and length of the plate layout "
                            "({}, {}) are not the same as for the plate data ({}, {})"
                            "".format(len(self._plate_layout.layout), len(self._plate_layout.layout[0]), self.height, self.width))
            else:
                raise Exception("Format: {} is not implemented in "
                            "ScreenData.set_plate_layout()".format(format))

        # Push PlateLayout to plates
        for plate in self.plates.values():
            plate.set_plate_layout(self._plate_layout)

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