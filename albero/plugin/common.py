# from box import Box
import textwrap
from pprint import pprint
import glob
from pathlib import Path
from jinja2 import Template
import yaml
import json

import logging

log = logging.getLogger(__name__)

from albero.utils import schema_validate
import copy

# Candidate Classes
# =============================
class Candidate:
    engine = None
    found = False
    data = None
    run = None
    scope = None
    key = None

    def __init__(self, run):
        self.run = copy.deepcopy(run)

    def __repr__(self):
        return f"{self.__dict__}"

    def _report_data(self, data=None):
        default_data = {
            # "rule": self.config,
            "value": self.engine._plugin_value,
            "data": self.data,
        }
        data = data or default_data
        d = json.dumps(data, indent=2)  # , sort_keys=True, )
        return d


# Generic Classes
# =============================
class PluginClass:
    _plugin_type = "none"
    _plugin_value = None

    _schema_props_new = "UNSET PLUGIN PROPRIETIES"

    _schema_props_plugin = {
        "engine": {
            "type": "string",
            # TODO: Fix this ug
            "default": "jerakia",
        },
        "value": {},
    }

    def __repr__(self):
        kind = self._plugin_type
        name = self._plugin_name
        value = getattr(self, "value", "NO VALUE")
        return f"{kind}.{name}:{value}"

    def __init__(self, config=None, parent=None, app=None):
        # assert (isinstance(config, dict)), f"Got: {config}"
        self.parent = parent
        self.app = app
        self.config = config or {}

        self._init()
        self._validate()

    def _init(self):
        pass

    def _validate(self):
        pass


class PluginBackendClass(PluginClass):
    _plugin_type = "backend"

    def _init(self):
        pass


class PluginStrategyClass(PluginClass):
    _plugin_type = "strategy"

    def _init(self):
        pass


class PluginEngineClass(PluginClass):
    _plugin_type = "engine"

    _schema_props_default = {
        "engine": {
            "default": "UNSET",
        },
        "value": {
            "default": "UNSET",
        },
    }

    # Default plugin API Methods
    # =====================
    def _init(self):
        assert isinstance(self.config, dict), f"Got: {self.config}"

    def _validate(self):

        # Build schema
        schema_keys = [a for a in dir(self) if a.startswith("_schema_props_")]
        props = {}
        for key in schema_keys:
            schema = getattr(self, key)
            props.update(schema)
        self.schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": props,
        }

        # log.debug (f"Validate {self.config} against {self.schema}")
        self.config = schema_validate(self.config, self.schema)
        return True

    # Public Methods
    # =====================
    def dump(self):
        ret = {
            "config": self.config,
        }
        return ret

    def lookup_candidates(self, key=None, scope=None):
        raise Exception(f"Module does not implement this method :(")
        # It must always return a list of `Candidate` instances
        return []

    def _example(self):
        print(f"Module does not implement this method :(")
        return None


# File plugins Extensions
# =============================


class PluginFileGlob:

    _schema_props_glob = {
        "glob": {
            "additionalProperties": False,
            "default": {
                "file": "ansible.yaml",
            },
            "properties": {
                "file": {
                    "type": "string",
                    "default": "ansible",
                    "optional": True,
                },
                "ext": {
                    "type": "array",
                    "default": ["yml", "yaml"],
                    "optional": True,
                },
            },
        }
    }
