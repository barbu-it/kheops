#!/usr/bin/env python3
"""Kheops App interface"""

import cProfile

import sys
import logging
import json
from pathlib import Path

import anyconfig
from diskcache import Cache

import kheops.plugin as KheopsPlugins
from kheops.controllers import QueryProcessor
from kheops.utils import schema_validate


log = logging.getLogger(__name__)

CONF_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": False,
    "default": {},
    "required": ["config"],
    #"$def": {
    #    "backends_items": {},
    #    "backends_config": {},
    #    "rules_items": {},
    #    "rules_config": {},
    #},
    "properties": {
        "lookups": {
            "type": "array",
            "default": [],
            "items": {
                "type": "object",
                #"properties": {"$ref": "#/$defs/backends_items"},
            },
        },
        "rules": {
            "type": "array",
            "default": [],
            # "arrayItem":  { "$ref": "#/$defs/rules_items" },
        },

        "config": {
            "type": "object",
            "default": {},
            "additionalProperties": True,
            #"required": ["app"],
            "properties": {
                "app": {
                    "type": "object",
                    "default": {},
                    "additionalProperties": False,
                },
                "lookups": {
                    # "additionalProperties": False,
                    "type": "object",
                    "default": {},
                    "properties": {
                        "prefix": {
                            "default": None,
                            "oneOf": [
                                {
                                    "type": "null",
                                    "description": "Disable prefix, all files are lookup up from the app root dir.",
                                },
                                {
                                    "type": "string",
                                    "description": "Add a path prefix before all paths. This is quite useful to store your YAML data in a dedicated tree.",
                                },
                            ],
                        },
                    },
                },
                "rules": {
                    "type": "object",
                    "default": {},
                },
            },
        },
    },
}


class GenericInstance:
    """
    GenericInstance class

    :var name: Name of the instace.
    :vartype name: str or None

    :var run: Json compatible dict for instance runtime data.
    :vartype run: dict


    """

    name = None
    run = {}


class KheopsNamespace(GenericInstance, QueryProcessor):
    """
    Kheops Namespace Class

    """
    def __init__(self, app, name, config=None):
        """
        Kheops Namespace Instance

        :param app: Parent Kheops Application. 
        :type app: Kheops

        :param name: Namespace name. 
        :type config: str

        :param config: Namespace configuration. 
        :type config: Any
        """

        config = schema_validate(config, CONF_SCHEMA)
        super().__init__(config)

        self.name = name
        self.app = app
        self.run = dict(app.run)

        # Validate configuration
        self.run["path_ns"] = str(Path(app.run["config_src"]).parent.resolve())


class Kheops(GenericInstance):
    """
    Kheops Application Class

    """

    def __init__(self, config="kheops.yml", namespace="default"):
        """
        Kheops Application Instance

        :param config: Kheops configuration. If it's a string, it loads the config from file path. 
        :type config: str or dict
        """

        # Init
        path_cwd = Path.cwd().resolve()

        # Fetch app paths
        self.run = {}
        self.run["path_cwd"] = str(path_cwd)

        self.run["config_src"] = config
        if isinstance(config, str):
            self.run["config_type"] = "file"
            self.run["path_config"] = str(Path(config).parent.resolve())
        elif isinstance(config, dict):
            self.run["config_type"] = "dict"
            self.run["path_config"] = str(path_cwd)
        else:
            raise Exception("Need a valid config")

        self.ns_name = namespace
        self.namespaces = {}
        self.raw_config = self.parse_conf(config)

    def parse_conf(self, config="kheops.yml"):
        """
        Parse Kheops configuration

        :param config: Kheops configuration, can either be a file path or a dict.
        :type config: dict or str or None
        
        :return: The parsed configuration.
        :rtype: dict

        """

        # Load config
        if isinstance(config, str):
            try:
                dict_conf = anyconfig.load(config)
            except Exception as err:
                raise Exception ("Can't load kheops configuration, got: %s", err)
            source = f"file:{config}"
        elif isinstance(config, dict):
            dict_conf = config
            source = "dict"
        return dict_conf

    def lookup(
        self,
        keys=None,
        policy=None,
        scope=None,
        trace=False,
        explain=False,
        validate_schema=False,
        namespace=None,
        namespace_prefix=False,
    ):
        """
        Lookup a key in hierarchy

        For a given lookup:
        * keys= [<namespace>:<key>]

        :param keys: List of keys to query.
        :type keys: list[str]

        :param scope: Scope key.
        :type scope: dict
        """

        ret = {}
        # Loop over keys
        for key_def in keys:

            key_def = key_def or ""

            # Identify namespace and key
            parts = key_def.split("/")
            ns_name = namespace or self.ns_name
            if len(parts) > 1:
                ns_name = parts[0]
                key_name = parts[1]
            else:
                key_name = parts[0]

            # Load namespace
            if ns_name in self.namespaces:
                ns_config = self.namespaces[ns_name]
            else:
                try:
                    ns_config = self.raw_config[ns_name]
                except KeyError as err:
                    raise Exception(f"Unknown kheops namespace: {ns_name}")

            ns = KheopsNamespace(self, ns_name, ns_config)

            # Get result
            result = ns.query(key=key_name, scope=scope, explain=explain)

            # Prepare output
            _key = key_name
            if namespace_prefix == True:
                _key = key_def
            ret[_key] = result

            # TODO: This may lead to inconsistant output format :/
            # Return result
            #if len(keys) > 1:
            #    log.debug("Append '%s' to results", key_name)
            #else:
            #    log.debug("Return '%s' result", key_name)
            #    return result

        return ret








# To clean/implement

    # def DEPRECATED_dump_schema(self):
    #     """Dump configuration schema"""

    #     ret1 = BackendsManager.get_schema(KheopsPlugins, mode="parts")
    #     ret2 = RulesManager.get_schema(KheopsPlugins)
    #     print(json.dumps(ret1, indent=2))
    #     return

    #     # ret = self.schema
    #     # ret["patternProperties"][".*"]["properties"]["tree"]["items"]["properties"] = ret1
    #     # ret["patternProperties"][".*"]["properties"]["tree"]["items"] = ret2

    #     # print(json.dumps(ret, indent=2))

    # def DEPRECATED_gen_docs(self):
    #     """Generate documentation"""

    #     print("WIP")
    #     return None

    #     # src = {
    #     #        "app": {
    #     #            "config_schema": None,
    #     #            "plugin_managers": {
    #     #                    'tree': None,
    #     #                    'rules': None,
    #     #                }
    #     #            }
    #     #
    #     # r1 = BackendsManager.get_schema(KheopsPlugins, mode='parts')

    #     # print (json.dumps(r1, indent=2))

    #     # ret = {
    #     #
    #     #    }

    #     # part_config = r1.get('config_schema', None)
    #     # part_item = r1['items']['core_schema']
    #     # part_item_plugins = r1['items']['plugin']

    #     # for kind, plugins in part_item_plugins.items():

    #     #    for plugin_name, schema in plugins.items():
    #     #        part_item_
