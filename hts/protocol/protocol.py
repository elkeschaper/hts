# (C) 2015 Elke Schaper

"""
    :synopsis: The Protocol Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import configobj
import logging
import os
import pickle
import re

LOG = logging.getLogger(__name__)
KNOWN_TASK_TYPES = ["preprocessing", "qc", "analysis"]

class Protocol:

    """ ``Protocol`` describes all information connected to the protocol of a
    high throughput screen.

    Attributes:
        file (str): File name of the protocol file.
        name (str): Name of the protocol
        tasks (list of ProtocolTasks): List of Protocol Tasks

    """

    def __init__(self, file, name, tasks, config):

        self.file = file
        self.name = name
        self.tasks = tasks

        # Save config simply as attributes.
        for key, value in config.items():
            if not hasattr(self, key):
                setattr(self, key, value)
        #import pdb; pdb.set_trace()

    @classmethod
    def create(cls, path, format=None):
        """ Create ``Protocol`` instance.

        Create ``Protocol`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input file, at current not specified

        """

        if not os.path.isfile(path):
            raise Exception("The supplied protocol file {} does not exist.".format(path))

        if format == 'config':
            config = configobj.ConfigObj(path, stringify=True)
            path_trunk, file = os.path.split(path)
            if not "name" in config:
                raise Exception("Each protocol should have a name.")
            name = config.pop("name")
            tasks = []
            for config_key in list(config.keys()):
                if isinstance(config[config_key], configobj.Section):
                    tasks.append(ProtocolTask.create(name=config_key, config=config.pop(config_key)))
            return Protocol(file=file, name=name, tasks=tasks, config=config)
        elif format == 'pickle':
            with open(path, 'rb') as fh:
                return pickle.load(fh)
        else:
            raise Exception("Format: {} is not implemented in "
                            "Protocol.create()".format(format))


    def get_tasks_by_tag(self, tag):

        return [task for task in self.tasks if tag in task.tags]


    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``Protocol`` instances.

        Serialize ``Protocol`` instance using the stated ``format``.

        Args:
            format (str):  The output format: Currently only "pickle".
            path (str): Path to output file

        .. todo:: Write checks for ``format`` and ``path``.
        """

        if format == 'pickle':
            with open(path, 'wb') as fh:
                pickle.dump(self, fh)
        else:
            raise Exception('Format is unknown: {}'.format(format))

            # These are code snippets for potential future use:
            if path:
                with open(path, 'w') as fh:
                    fh.write(output)
            if return_string:
                return output



class ProtocolTask:

    """ ``ProtocolTask`` describes all information connected to a task defined in a protocol of a
    high throughput screen.

    Attributes:
        name (str): Name of the task
        tags (list of str): List of all tags of this Task. Necessarily needs to include exactly one of KNOWN_TASK_TYPES
        type (str): One of KNOWN_TASK_TYPES
        method: (str): Name of a method in type.
        config: (configobj.ConfigObj): configobj.ConfigObj

    """

    def __init__(self, name, tags, type, method, config):

        self.name = name
        self.tags = tags
        self.type = type
        self.method = method
        self.config = config


    @classmethod
    def create(cls, name, config):
        """ Create ``ProtocolTask`` instance.

        Create ``ProtocolTask`` instance.

        Args:
            name (str): The arbitrary name of the protocol task
            config (ConfigObj): ConfigObj
        """

        if not isinstance(config, configobj.Section):
            raise Exception("config must be of type configobj.Section, not {}".format(type(config)))

        if not "tags" in config:
            import pdb; pdb.set_trace()
            raise Exception("tags must be defined in config")
        tags = [i.lower() for i in config.pop("tags")]

        type = [i for i in KNOWN_TASK_TYPES if i in tags]
        if not len(type) == 1:
            raise Exception("Exactly one of {} needs to be defined in "
                            "config['tags']: {}".format(KNOWN_TASK_TYPES, tags))
        type = type[0]

        if not "method" in config:
            raise Exception("method must be defined in config")
        method = config.pop("method")

        return ProtocolTask(name=name, tags=tags, type=type, method=method, config=config)