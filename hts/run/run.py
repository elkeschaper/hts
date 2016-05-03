# (C) 2015, 2016  Elke Schaper

"""
    :synopsis: The Run Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import collections
import configobj
import copy
import logging
import numpy as np
import os
import pickle
import scipy.stats

from hts.data_tasks import data_tasks
from hts.plate_data.meta_data import MetaData
from hts.plate_data.plate_data import PlateData
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

    def __iter__(self):
        """
            Iterates over plates.
        """
        for plate_name, plate in self.plates.items():
            yield plate

    def __getitem__(self, i):
        return list(self.plates.values())[i]

    def __init__(self, plates, path=None, **kwargs):

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
        self.config_data = kwargs

        self.plates = collections.OrderedDict((plate.name, plate) for plate in self.plates.values())

        if self.protocol():
            # Todo: Include check that plate layout is defined.
            self.preprocess()


    @classmethod
    def create(cls, origin, path, format=None, dir=False, **kwargs):
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
        if origin == 'csv':
            return cls.create_from_csv_file(path, file, **kwargs)
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
        plate_names = config["plate_names"]
        n_plate = len(plate_names)

        defined_data_types = [data_type for data_type in KNOWN_DATA_TYPES if data_type in config]
        LOG.info(defined_data_types)

        plates = None
        config_plate_wise = [{} for _ in plate_names]
        additional_data = {}
        for data_type in defined_data_types:
            config_local = config[data_type].copy()
            if isinstance(config_local[next(iter(config_local))], configobj.Section):
                # Multiple files for each plate are defined.
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
                    # Per datatype, one file for all plates
                    if data_type == "plate_layout":
                        data = plate_layout.PlateLayout.create(paths=l_paths, formats=l_format, tags=l_tags, configs=l_config_set)
                    else:
                        raise Exception("Reading in general info for data_type {} is not yet implemented."
                                        "".format(data_type))
                    additional_data[data_type] = data
                elif all([len(paths) == n_plate for paths in l_paths]):
                    # Per datatype, one file for every plate
                    for i_plate in range(n_plate):
                        paths = [i[i_plate] for i in l_paths]
                        tags = [i[i_plate] for i in l_tags]
                        config_plate_wise[i_plate][data_type] = {"paths": paths, "tags": tags, "formats": l_format, "configs": l_config_set, "types": list(config_local.keys())}
                else:
                    raise Exception("Currently option for multiple plates per plate data with some being one per plate "
                                    "and some one for all is not yet implemented.")
            else:
                # Only a single file for each plate is defined.
                config_local, paths, tags = cls.map_config_file_definition(config_local, n_plate=n_plate)
                format = config_local.pop("format")
                if len(paths) == 1 and n_plate != 1:
                    if data_type == "plate_layout":
                        data = plate_layout.PlateLayout.create(paths=paths, formats=[format], **config_local)
                        additional_data[data_type] = data
                    elif data_type == "readout" and format == "csv_one_well_per_row":
                        width = int(config_local.pop("width"))
                        height = int(config_local.pop("height"))
                        plates = run_io.read_csv(file=paths[0], width=width, height=height, **config_local)
                    else:
                        raise Exception("Reading in general info for data_type {} is not yet implemented."
                                        "".format(data_type))
                else:
                    for i_plate, (i_path, tag) in enumerate(zip(paths, tags)):
                        config_local.update({"paths": [i_path], "tags": [tag], "formats": [format]})
                        config_plate_wise[i_plate][data_type] = copy.deepcopy(config_local) # For current shallow dicts, config_local.copy() is ok.

        if not plates:
            # plate.Plate.create expects: formats, paths, configs = None, names=None, tags=None
            plates = [plate.Plate.create(format="config", name=plate_name, **config_plate) for config_plate, plate_name in zip(config_plate_wise, plate_names)]
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


    @classmethod
    def create_from_csv_file(cls, path, file, **kwargs):
        """ Read csv data and create `Run` instance.

        Read csv data and create `Run` instance.

        Args:
            path (str): Path to input csv file
            file (str): Filename of csv file

        """

        plates = run_io.read_csv(file=os.path.join(path, file), **kwargs)
        return Run(path=path, plates=plates)


    def filter(self, **kwargs):
        """ Filter run data according to filter keyword arguments.

        Filter run data according to filter arguments. The values for each plates are concatenated.

        Args:
            kwargs: Keyword arguments for filtering.

        Returns:
            list of floats
        """

        data = [plate.filter(**kwargs) for plate in self.plates.values()]
        #return [item for sublist in data for item in sublist]
        return data

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


    def get_run_config_data(self):
        """
            Extract relevant meta data for qc and analysis reports.
            Returns list of tuples: [(key_str, value_str)]
        """


        # You could try to flatten the dict automagically to increase elegance:
        # http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
        config_data_order = ["protocol_name", "protocol_file", "experimenter", "experimenter_mail", "run_config"]
        config_data = {}
        for i, j in self.config_data.items():
            if i in ["qc"]:
                continue
            elif type(j) == configobj.Section:
                for k, l in j.items():
                    config_data["_".join([i,k])] = l
            else:
                config_data[i] = j
        config_data["protocol_name"] = self.protocol().name
        config_data["protocol_file"] = self.protocol().file
        config_data["run_config"] = self.path
        config_data = {i: str(j) if type(j) != list else ", ".join([str(k) for k in j]) for i,j in config_data.items()}

        config_data_ordered = [(i_o, config_data[i_o]) for i_o in config_data_order]
        config_data_ordered += [(i_m, str(i_v)) for i_m, i_v in config_data.items() if i_m not in config_data_order]

        return config_data_ordered


    def qc(self):
        """ Perform quality control and save the results

        Perform quality control and save the results

        Args:

        .. todo:: qc() and analysis() as pretty similar. Perhaps, refactoring/merging may be useful.
        """

        if hasattr(self, '_qc'):
            return self._qc

        self._qc = {}
        tasks = self.protocol().get_tasks_by_tag("qc")
        for task in tasks:
            LOG.info(task.name)
            LOG.info(task.type)
            methods_from_protocol = collections.OrderedDict([(i,j) for i,j in task.config.items() if isinstance(j, configobj.Section)])
            config_data_from_protocol = collections.OrderedDict([(i,j) for i,j in task.config.items() if not isinstance(j, configobj.Section)])
            # This will work Python 3.5 onwards: return {**protocol_qc, **run_qc}
            if task.name in self.config_data:
                qc_config_data = dict(config_data_from_protocol, **self.config_data[task.name])
            else:
                qc_config_data = config_data_from_protocol
            self._qc[task.name] = data_tasks.perform_task(run=self,
                                                          task_name=task.method,
                                                          qc_methods=methods_from_protocol,
                                                          config_data=self.get_run_config_data(),
                                                          **qc_config_data)

        if "send_mail_upon_qc" in self.config_data and self.config_data["send_mail_upon_qc"].lower() == "true":
            send_mail(email_to = [self.config_data['experimenter_mail']], body ="QC report for Run config '{}' is prepared.".format(self.path))
        return self._qc


    def analysis(self):
        """ Perform analysis and save the results.

        Perform analysis and save the results. Parameters are taken from the protocol and the run config. Each
        ProtocolTask tagged with "analysis" is run. Each ProtocolTask may be run multiple times, if several dicts
        are defined for it (this could be either in protocol, or in the run config.)
        """

        if hasattr(self, '_analysis'):
            return self._analysis

        self._analysis = {}
        tasks = self.protocol().get_tasks_by_tag("analysis")
        for task in tasks:
            LOG.info(task.name)
            LOG.info(task.type)

            # Merge the data about the task from the Run config and the Protocol config:
            # This will work Python 3.5 onwards:  {**task.config, **analysis_config_run}
            subtasks = {i:j for i,j in self.config_data[task.name].items() if isinstance(j, configobj.Section)}
            analysis_config_run = {i:j for i,j in self.config_data[task.name].items() if not isinstance(j, configobj.Section)}
            analysis_config_meta = dict(task.config, **analysis_config_run)

            analysis_results = {}
            for subtask_name, subtask_config in subtasks.items():
                analysis_config = dict(analysis_config_meta, **subtask_config)
                analysis_results[subtask_name] = data_tasks.perform_task(run=self, tag=subtask_name, task_name=task.method, **analysis_config)

            self._analysis[task.name] = analysis_results

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


    def write(self, format, path=None, return_string=None, **kwargs):
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
        elif format == 'csv_one_well_per_row':
            output = run_io.serialize_as_csv_one_row_per_well(self, **kwargs)
        elif format == 'serialize_as_pandas':
            output = run_io.serialize_as_pandas(self, **kwargs)
            self.data_frame = output
        else:
            raise Exception('Format is unknown: {}'.format(format))

        if path:
            with open(path, 'w') as fh:
                fh.write(output)
        if return_string:
            return output

    ###### Handle Run data as a pandas.data_frame:
    ## - less or no emphasis on plate_layout structure
    ## - calculations that are oblivous of plate_layout may want to go here.
    ## - one data_frame row per well or per sample

    @property
    def data_frame(self):
        if not hasattr(self, "_data_frame"):
            self._data_frame = self.write(format='serialize_as_pandas', path=None, return_string=False)
        return self._data_frame

    @data_frame.setter
    def data_frame(self, value):
        self._data_frame = value

    @property
    def data_frame_samples(self):
        if not hasattr(self, "_data_frame_samples"):
            self._data_frame_samples = self.data_frame[self.data_frame.sample_type == "s"]
        return self._data_frame_samples

    @data_frame_samples.setter
    def data_frame_samples(self, value):
        self._data_frame_samples = value

    def add_meta_data(self, tag, **kwargs):
        config_data = self.config_data["meta_data"][tag]
        LOG.debug(config_data)
        merged_data = run_io.add_meta_data(self,
                                           meta_data_kwargs=config_data["data_kwargs"],
                                           meta_data_rename=config_data["join_columns"],
                                           meta_data_exclude_columns=config_data["exclude_columns"],
                                           meta_data_well_name_pattern=config_data["well_name_pattern"],
                                           filter_condition=lambda x: x=="s", # Only allow sample data after merging
                                           **kwargs)
        self.data_frame_samples = merged_data


    def add_data_from_data_frame(self, tags, plate_data_type="meta_data"):

        df = self.data_frame_samples
        data = {plate: {tag: {} for tag in tags} for plate in self.plates.values()}
        for tag in tags:
            for readout, plate_name, i_row, i_column in zip(df[tag], df['plate_name'], df['well_i1'], df['well_i2']):
                data[self.plates[plate_name]][tag][(i_row, i_column)] = readout

        for plate, plate_data in data.items():
            # ToDo: Allow creation of any type of PlateData (e.g. via registries).
            meta_data = MetaData.create_from_coordinate_tuple_dict(data=plate_data, width=self.width, height=self.height)
            plate.add_data(data=meta_data, data_type=plate_data_type)


    def summarize_statistical_significance(self, replicate_defining_column,
                                           data_tag_normalized_readout,
                                           data_tag_pvalue_sample_vs_neg_control,
                                           data_tag_pvalue_sample_vs_pos_control):


        # Groupby on data_frame with sample data only for replicates.
        gb = self.data_frame_samples.groupby(replicate_defining_column)

        # Define aggregation methods
        agg = {}

        # Aggregate normalized values.
        agg[data_tag_normalized_readout] = {data_tag_normalized_readout+'_mean': np.mean, data_tag_normalized_readout+'_std': np.std}

        # Aggregate pvalues.
        def fishers_method(pvalues):
            # Aggregate pvalues using Fisher's method: https://en.wikipedia.org/wiki/Fisher's_method
            statistic, pval = scipy.stats.combine_pvalues(pvalues)
            return pval

        agg[data_tag_pvalue_sample_vs_neg_control] = {data_tag_pvalue_sample_vs_neg_control: fishers_method}
        agg[data_tag_pvalue_sample_vs_pos_control] = {data_tag_pvalue_sample_vs_pos_control: fishers_method}

        # Add data from all other columns
        columns = self.data_frame_samples.columns.values
        columns_retain = [i for i in columns if i not in [data_tag_normalized_readout, data_tag_pvalue_sample_vs_neg_control, data_tag_pvalue_sample_vs_pos_control, replicate_defining_column]]
        # Todo: generalize this column exclusion:
        columns_retain = [i for i in columns_retain if i not in ["net_fret", "fret_1", "fret_2", "realtime-glo_1", "realtime-glo_2"]]
        for column in columns_retain:
            agg[column] = {column: lambda x: x.iloc[0]}

        # Calculate for every group.
        gb2 = gb.agg(agg)
        gb2.columns = gb2.columns.droplevel(0)

        return gb, gb2


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

