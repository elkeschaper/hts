# (C) 2015 Elke Schaper

"""
    :synopsis: The Run Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import ast
import collections
import configobj
import copy
import logging
import os
import pickle
import re

from hts.analysis import analysis
from hts.data_tasks import data_tasks
from hts.run import run_io
from hts.plate import plate
from hts.plate_data import plate_layout
from hts.protocol import protocol


LOG = logging.getLogger(__name__)

KNOWN_DATA_TYPES = plate.KNOWN_DATA_TYPES

class Run:

    """ ``Run`` describes all information connected to one run of a high
        throughput screening experiment

    Attributes:
        name (str): Name of the run
        plates (collections.OrderedDict of ``Plate``): collections.OrderedDict of ``Plate`` instances
        width (int): Width of the plates
        height (int): Height of the plates
        _protocol (``Protocol``): ``Protocol`` instance
        _platelayout (``PlateLayout``): ``PlateLayout`` instance
        _qc (dict of dict of ``QualityControl`` instance): A collection of ``QualityControl`` instance
        raw_qc (``QualityControl``): ``QualityControl`` instance - NEEDED?
        net_qc (``QualityControl``): ``QualityControl`` instance - NEEDED?
        experimenter (str): Name of the experimenter
        experimenter (str): Mail address of the experimenter


    ..todo:: Implement me :)
    """

    def __str__(self):
        """
            Create string for Run instance.
        """
        try:
            run = ("<Run instance>\nPath to run config file: {}\n"
                "Number of plates: {}\nwidth: {}\nheight: {}"
                "".format(self.path, len(self.plates), self.width, self.height))
        except:
            run = "<Run instance>"
            LOG.warning("Could not create string of Run instance.")

        return run


    def __init__(self, plates, path = None, **kwargs):

        self.path = path
        self.plates = collections.OrderedDict((plate.name, plate) for plate in plates)
        #Plates as list: self.plates = plates
        # Later: Check if all plates are of the same height and length
        try:
            self.width = plates[0].width
            self.height = plates[0].height
        except:
            LOG.info("Could not discern plate width/height from first plate.")

        if "protocol" in kwargs:
            param = kwargs.pop('protocol')
            if not type(param) == configobj.Section:
                raise Exception("param for protocol is not of type "
                    "configobj.Section: {}, {}".format(param, type(param)))
            self.protocol(path = param['path'], format = param['format'])

        # Save all other kwargs simply as attributes.
        #for key, value in kwargs.items():
        #    if not hasattr(self, key):
        #        setattr(self, key, value)
        self.meta_data = kwargs

        # Extract plate numbering for multiple plates and set index for each plate.
        self.plate_tag_numbers = [re.findall("(\d+)", i) for i in self.plates.keys()]

        plate_tag_numbers_t = [list(i) for i in zip(*self.plate_tag_numbers)]
        for i in plate_tag_numbers_t:
            if len(set(i)) == len(self.plates):
                plate_indices = i
                break
        else:
            raise Exception("No plate numbering is informative: {}. {}. Please check if the files have useful names"
                            "from which a numbering could be derived. Otherwise, change the implementation ;) "
                            "".format(list(self.plates.keys()), plate_tag_numbers_t))

        # Set index for each plate.
        for i_plate, plate_index in zip(list(self.plates.keys()), plate_indices):
            self.plates[i_plate].index = plate_index
        self.plates = collections.OrderedDict((plate.index, plate) for plate in self.plates.values())

        if self.protocol():
            # Todo: Include check that plate layout is defined.
            self.preprocess()


    @classmethod
    def create(cls, origin, path, format = None, dir = False):
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
            if os.path.isdir(path):
                file = os.listdir(path)
            else:
                raise ValueError("Run create directory {} does not exist.".format(path))
        else:
            if os.path.isfile(path):
                path, file = os.path.split(path)
            else:
                raise ValueError("Run create file {} does not exist.".format(path))


        if origin == 'config':
            return cls.create_from_config(path, file)
        if origin == 'envision':
            return cls.create_from_envision(path, file)
        elif origin == 'pickle':
            with open(file, 'rb') as fh:
                return pickle.load(fh)
        else:
            raise ValueError("The combination of origin: {} and format: {} is "
                            "not implemented in "
                            "cls.create()".format(origin, format))


    @classmethod
    def create_from_config(cls, path, file):
        """ Read config and use data to create `Run` instance.

        Read config and use data to create `Run` instance.

        Args:
            path (str): Path to input configobj file
            file (str): Filename of configobj file
        """

        config = configobj.ConfigObj(os.path.join(path, file), stringify=True)
        n_plate = int(config["n_plate"])

        defined_data_types = [data_type for data_type in KNOWN_DATA_TYPES if data_type in config]
        LOG.info(defined_data_types)

        config_plate_wise = [{} for _ in range(n_plate)]
        additional_data = {}
        for data_type in defined_data_types:
            config_local = config[data_type].copy()
            if isinstance(config_local[next(iter(config_local))], configobj.Section):
                # multiple = True
                l_config_set = []
                l_paths = []
                l_tags = []
                l_format = []
                for local_set, config_set in config_local.items():
                    config_set, paths, tags = cls.map_config_file_definition(config_set, n_plate=n_plate)
                    l_config_set.append(config_set)
                    l_paths.append(paths)
                    l_tags.append(tags)
                    l_format.append(config_set.pop("format"))
                if all([len(paths) == 1 for paths in l_paths]) and n_plate != 1:
                    # One file for all plates
                    if data_type == "plate_layout":
                        data = plate_layout.PlateLayout.create(paths=l_paths, formats=l_format, tags=l_tags, configs=l_config_set)
                    else:
                        raise Exception("Reading in general info for data_type {} is not yet implemented."
                                        "".format(data_type))
                    additional_data[data_type] = data
                elif all([len(paths) == n_plate for paths in l_paths]):
                    # One file for every plate
                    for i_plate in range(n_plate):
                        paths = [i[i_plate] for i in l_paths]
                        tags = [i[i_plate] for i in l_tags]
                        config_plate_wise[i_plate][data_type] = {"paths": paths, "tags": tags, "formats": l_format, "configs": l_config_set}
                else:
                    raise Exception("Currently option for multiple plates per plate data with some being one per plate "
                                    "and some one for all is not yet implemented.")
            else:
                # multiple = False
                config_local, paths, tags = cls.map_config_file_definition(config_local, n_plate=n_plate)
                format = config_local.pop("format")
                if len(paths) == 1 and n_plate != 1:
                    if data_type == "plate_layout":
                        data = plate_layout.PlateLayout.create(paths=paths, formats=[format], **config_local)
                    else:
                        raise Exception("Reading in general info for data_type {} is not yet implemented."
                                        "".format(data_type))
                    additional_data[data_type] = data
                else:
                    for i_plate, (i_path, tag) in enumerate(zip(paths, tags)):
                        config_local.update({"paths": [i_path], "tags": [tag], "formats": [format]})
                        config_plate_wise[i_plate][data_type] = copy.deepcopy(config_local) # For current shallow dicts, config_local.copy() is ok.

        # plate.Plate.create expects: formats, paths, configs = None, names=None, tags=None
        plates = [plate.Plate.create(format="config", **config_plate) for config_plate in config_plate_wise]
        for data_type, data in additional_data.items():
            for i_plate in plates:
                i_plate.add_data(data_type, data, force=True)

        # Data: may be all in one file (csv .xlxs), or in separated .csv files (default case, e.g. .csv)
        # Data: In particular for readouts, there may be several sets of data (e.g. Readouts for different points in time.)

        #if len(data_types_plate_wise) == 0:
        #    raise Exception("No plate wise information was defined in Run config.")


        # Check if the number of files is equal for all data_types_plate_wise:

        return Run(path=os.path.join(path, file), plates=plates, **config)


    @classmethod
    def map_config_file_definition(cls, config, n_plate):
        """
            Extract the files from the config file.
        """

        config_file = {i: config.pop(i) for i in ["filenames", "path", "filename", "filenumber", "tags"] if i in config}
        tags = [i for i in range(n_plate)]
        if all(i in config_file for i in ["path", "filenames"]): #"filenames" predominates "filename", "filenumber"
            files = [os.path.join(config_file["path"], i_file) for i_file in config_file['filenames']]
        elif all(i in config_file for i in ["path", "filename", "filenumber"]):
            files = [os.path.join(config_file["path"], config_file["filename"].format(i_index)) for i_index in config_file['filenumber']]
            tags = config_file['filenumber']
        elif all(i in config_file for i in ["path", "tags"]):
            # In reality, we are in this case only dealing with one file, in which the information for all plates is stored.
            # For these cases, for now, we pass the path information in hidden as config["file"]
            files = config_file["tags"]
            config["file"] = config_file["path"]
        elif "path" in config_file:
            # There is only one file defined. We assumed it is defined for all plates.
            files = [config_file["path"]]
            tags = [0]
        else:
            raise Exception("Not enough information given to decipher data files.")

        if len(files) != n_plate and len(files) != 1:
            raise Exception("The number of user defined files {} is not equal to "
                            "the user defined n_plate {} nor 1.".format(len(files), n_plate))

        return config, files, tags


    @classmethod
    def create_from_envision(cls, path, file):
        """ Read envision data and create `Run` instance.

        Read envision data and create `Run` instance.

        Args:
            path (str): Path to input configobj file
            file (str): Filename of configobj file

        .. todo:: Write checks if path and file exists when necessary.
        """

        if type(file) != list:
            file = [file]

        plates = []
        for i_file in file:
            config = {"readout": {"paths": [os.path.join(path, i_file)], "formats": ["envision_csv"]}}
            plates.append(plate.Plate.create(format="config", **config))

        return Run(path=path, plates=plates)


    def create_qc_report(self, path):
        """ Create quality control report (.pdf) in path.

        Create quality control report (.pdf) in path.

        Args:
            path (str): Path to result quality control report file

        .. todo:: Write checks if the path exists.
        """

        self.run_qc()
        # Create pdf


    def filter(self, type, tag, subset=None):
        """ Filter run data according to type and tag.

        Filter run data according to type and tag.

        Args:
            type (str): Either per "run_wise" or per "plate_wise".
            tags (str): Defines either the plate (within the plate),
                or the plate (within the run).
            subset (list of str): Defines which plates/plate_readouts shall be included.

        Returns:
            Readout or Plate (for multiple Readouts)
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


    def preprocess(self):
        """ Perform data preprocessing.

        Perform data preprocessing.

        """
        tasks = self.protocol().get_tasks_by_tag("preprocessing")
        for task in tasks:
            for i_plate in self.plates.values():
                i_plate.preprocess(task.method, **task.config)
        else:
            LOG.info("No preprocessing tasks defined in protocol: {}".format(self.protocol().name))


    def get_run_meta_data(self):
        """
            Extract relevant meta data for qc and analysis reports.
            Returns list of tuples: [(key_str, value_str)]
        """


        # You could try to flatten the dict automagically to increase elegance:
        # http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
        meta_data_order = ["protocol_name", "protocol_file", "experimenter", "experimenter_mail", "run_config"]
        meta_data = {}
        for i, j in self.meta_data.items():
            if i in ["qc"]:
                continue
            elif type(j) == configobj.Section:
                for k, l in j.items():
                    meta_data["_".join([i,k])] = l
            else:
                meta_data[i] = j
        meta_data["protocol_name"] = self.protocol().name
        meta_data["protocol_file"] = self.protocol().file
        meta_data["run_config"] = self.path
        meta_data = {i: str(j) if type(j) != list else ", ".join([str(k) for k in j]) for i,j in meta_data.items()}

        meta_data_ordered = [(i_o,meta_data[i_o]) for i_o in meta_data_order]
        meta_data_ordered += [(i_m, str(i_v)) for i_m, i_v in meta_data.items() if i_m not in meta_data_order]

        return meta_data_ordered


    def qc(self):
        """ Perform quality control and save the results

        Perform quality control and save the results

        Args:

        .. todo:: Create QC for different plate subsets (e.g. raw/net).
        .. todo:: Use function to get to plate data instead of attributes?
        """

        if hasattr(self, '_qc'):
            return self._qc

        self._qc = {}
        tasks = self.protocol().get_tasks_by_tag("qc")
        for task in tasks:
            methods_from_protocol = {i:j for i,j in task.config.items() if isinstance(j, configobj.Section)}
            meta_data_from_protocol = {i:j for i,j in task.config.items() if not isinstance(j, configobj.Section)}
            # This will work Python 3.5 onwards: return {**protocol_qc, **run_qc}
            if "qc" in self.meta_data:
                qc_meta_data = dict(meta_data_from_protocol, **self.meta_data["qc"])
            else:
                qc_meta_data = meta_data_from_protocol
            self._qc[task.name] = data_tasks.perform_task(run=self,
                                                          task_name=task.method,
                                                          qc_methods=methods_from_protocol,
                                                          meta_data=self.get_run_meta_data(),
                                                          **qc_meta_data)

        if "send_mail_upon_qc" in self.meta_data and self.meta_data["send_mail_upon_qc"].lower() == "true":
            send_mail(email_to = [self.meta_data['experimenter_mail']], body = "QC report for Run config '{}' is prepared.".format(self.path))
        return self._qc


    def analysis(self):
        """ Perform analysis and save the results

        Perform analysis and save the results

        Args:

        """

        if hasattr(self, '_analysis'):
            return self._analysis
        else:
            self._analysis = {}
            for i_ana, protocol_analysis_param in self.protocol().analysis.items():
                LOG.info(i_ana)
                LOG.info(protocol_analysis_param)
                subset = self.filter(**protocol_analysis_param['filter'])
                #import pdb; pdb.set_trace()
                if protocol_analysis_param['filter']['tag'] == '':
                    analysis_results = {i: analysis.perform_analysis(methods=protocol_analysis_param['methods'], data=j, plate_layout=self.plate_layout(), **self.meta_data['meta']) for i,j in subset.items()}
                else:
                    analysis_results = analysis.perform_analysis(methods=protocol_analysis_param['methods'], data=subset, plate_layout=self.plate_layout(), **self.meta_data['meta'])
                self._analysis[i_ana] = analysis_results

        return self._analysis


    def protocol(self, path = None, format = None):
        """ Read protocol and attach to `Run` instance.

        Read protocol and attach to `Run` instance.

        Args:
            path (str): Path to input file
            format (str):  At current only "csv"

        .. todo:: Write checks if path and format exists when necessary.
        """

        if not hasattr(self, '_protocol'):
            if path and format:
                self._protocol = protocol.Protocol.create(path, format)
            else:
                return None
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
            with open(path, 'wb') as fh:
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

def send_mail(body,
                email_to,
                email_from = "adriano_conrad_aguzzi@gmail.com",
                smtp_server = "smtp.gmail.com",
                smtp_port = 587,
                smtp_username = "elkewschaper@gmail.com",
                email_subject = "QC_report finished"):

    LOG.info("Sending email to {}".format(email_to))

    from email.mime.text import MIMEText
    from datetime import date
    import smtplib

    smtp_password = input('Enter password for {}:  '.format(smtp_username))
    #email_from = smtp_username

    DATE_FORMAT = "%d/%m/%Y"
    EMAIL_SPACE = ", "

    msg = MIMEText(body)
    msg['Content-Type'] = 'text/html; charset=UTF8'
    msg['Subject'] = email_subject + " %s" % (date.today().strftime(DATE_FORMAT))
    msg['From'] = email_from
    msg['To'] = EMAIL_SPACE.join(email_to)
    mail = smtplib.SMTP(smtp_server, smtp_port)
    mail.starttls()
    mail.login(smtp_username, smtp_password)
    mail.sendmail(email_from, email_to, msg.as_string())
    mail.quit()

