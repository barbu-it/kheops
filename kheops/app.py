#!/usr/bin/env python3
"""Kheops App interface"""

import cProfile

import sys
import logging
import json
from pathlib import Path

import anyconfig
from diskcache import Cache

from kheops.controllers import QueryProcessor
from kheops.utils import schema_validate


log = logging.getLogger(__name__)




CONF_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "additionalProperties": False,
        "default": {},
        "$def": {
            "backends_items": {},
            "backends_config": {},
            "rules_items": {},
            "rules_config": {},
        },
        #"patternProperties": {
        #    ".*": {
        #        "type": "object",
        #        "optional": True,
        #        "additionalProperties": False,
                "properties": {
                    "config": {
                        "type": "object",
                        "default": {},
                        "additionalProperties": True,
                        "properties": {
                            "app": {
                                "type": "object",
                                "default": {},
                                "additionalProperties": False,
                                "properties": {
                                    "root": {
                                        "default": None,
                                        "oneOf": [
                                            {
                                                "type": "null",
                                                "description": "Application current working directory is the `kheops.yml` directory",
                                            },
                                            {
                                                "type": "string",
                                                "description": "Application working directory. If a relative path is used, it will be depending on `kheops.yml` directory",
                                            },
                                        ],
                                    },
                                    "cache": {
                                        "default": "kheops_cache",
                                        "oneOf": [
                                            {
                                                "type": "null",
                                                "description": "Disable cache",
                                            },
                                            {
                                                "type": "string",
                                                "description": "Path of the cache directory",
                                            },
                                        ],
                                    },
                                },
                            },

                            # OLD
                            "tree": {
                                # "additionalProperties": False,
                                "type": "object",
                                "default": {},
                                "deprecated": True,
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
                    "tree": {
                        "type": "array",
                        "default": [],
                        "items": {
                            "type": "object",
                            "properties": {"$ref": "#/$defs/backends_items"},
                        },
                    },
                    "lookups": {
                        "type": "array",
                        "default": [],
                        "items": {
                            "type": "object",
                            "properties": {"$ref": "#/$defs/backends_items"},
                        },
                    },
                    "rules": {
                        "type": "array",
                        "default": [],
                        # "arrayItem":  { "$ref": "#/$defs/rules_items" },
                    },
                },
     #       },
     #   },
    }




class GenericInstance():

    name = None
    run = {}




class KheopsNamespace(GenericInstance, QueryProcessor):

    def __init__(self, app, name, config=None):

        self.name = name
        self.config = config or {}
        self.app = app
        self.run = dict(app.run)
        

        # Validate configuration
        self.config = schema_validate(self.config, CONF_SCHEMA)

        self.run["path_ns"] = str(Path(app.run['config_src']).parent.resolve())


      


#    def load_namespace(self, namespace="default"):
#        # Validate configuration
#
#        config = dict(self.raw_config)
#        try:
#            config = config[namespace]
#        except KeyError:
#            log.error("Can't find namespace '%s' in config '%s'", namespace, config)
#            sys.exit(1)
#        config = schema_validate(config, self.schema)
#
#        pprint (config)
#
#        self.run["path_cwd"]
#
#        print ("OKKKKK")
#
#
#        conf2 = config
#        # Get application paths
#        path_root = conf2["config"].get("app", {}).get("root", None)
#        if path_root is None:
#            path_root = Path(config).parent
#            log.debug("Root path guessed from conf file location.")
#        else:
#            path_root = Path(conf2["config"]["app"]["root"])
#            log.debug("Root path is steup in config")
#
#
#
#        path_root = str(path_root.resolve())
#        self.run["path_root"] = path_root
#
#
#        # path_prefix = conf2["config"]["app"]["prefix"]
#        # if not path_prefix:
#        #    path_prefix = ''
#        # p = Path(path_prefix)
#        # if not p.is_absolute():
#        #    p = path_root / p
#        #    try:
#        #        p = p.resolve().relative_to(Path.cwd().resolve())
#        #    except ValueError:
#        #        pass
#
#
#        # Cache paths
#        path_cache = Path(conf2["config"]["app"]["cache"])
#        if not path_cache.is_absolute():
#            path_cache = Path(path_root) / path_cache
#        path_cache = str(path_cache)
#        self.run["path_cache"] = path_cache
#        self.cache = {
#                'files': Cache(path_cache),
#                'queries': Cache(path_cache),
#                }
#
#        # self.run['path_prefix'] = str(p.resolve())
#        log.debug("Working directory is %s, cwd is: %s", path_root, path_cwd)
#
#        return config



    #def query(self, key=None, scope=None):
    #    processor = QueryProcessor(app=self.app)
    #    result = processor.exec(key, scope)
#
#        return result



class Kheops(GenericInstance):
    """Main Kheops Application Instance

    """

    def __init__(self, config="kheops.yml", namespace="default"):
        """
        init function

        :param kind: Optional "kind" of ingredients.
        :type kind: list[str] or None
        :raise lumache.InvalidKindError: If the kind is invalid.
        :return: The ingredients list.
        :rtype: list[str]
        """

        # Init
        path_cwd = Path.cwd().resolve()

        # Fetch app paths
        self.run = {}
        self.run["path_cwd"] = str(path_cwd)

        self.run["config_src"] = config
        if isinstance(config, str):
            self.run["config_type"] = 'file'
            self.run["path_config"] = str(Path(config).parent.resolve())
        elif isinstance(config, dict):
            self.run["config_type"] = 'dict'
            self.run["path_config"] = str(path_cwd)
        else:
            raise Exception("Need a valid config")

        
        self.ns_name = namespace
        self.raw_config = self.parse_conf(config)



    def parse_conf(self, config="kheops.yml"):
        """
        Parse Kheops configuration

        :param config: Kheops configuration, can either be a file path or a dict.
        :type config: dict or str or None
        :param namespace: Configuration namespace to use.
        :type namespace: str
        :return: The parsed configuration.
        :rtype: dict

        """

        # Load config
        if isinstance(config, str):
            dict_conf = anyconfig.load(config)
            source = f'file:{config}'
        elif isinstance(config, dict):
            dict_conf = config
            source = 'dict'
        return dict_conf





    def lookup2(self, keys=None, policy=None, scope=None, 
        trace=False, explain=False, validate_schema=False, 
        namespace='default' ,
        ):
        """Lookup a key in hierarchy"""


        ret = {}
        # Loop over keys
        for key_def in keys:

            key_def = key_def or ''

            # Identify namespace and key
            parts = key_def.split(':')
            ns_name = self.ns_name
            if len(parts) > 1:
                ns_name = parts[0]
                key_name = parts[1]
            else:
                key_name = parts[0]

            # Load namespace
            ns_config = self.raw_config[ns_name]
            ns = KheopsNamespace(self, ns_name, ns_config)

            # Get result
            result = ns.query(key=key_name, scope=scope, explain=explain)

            # TODO: This may lead to inconsistant output format :/
            # Return result
            if len(keys) > 1:
                log.debug("Append '%s' to results", key_name)
                ret[key_name] = result
            else:
                log.debug("Return '%s' result", key_name)
                return result

        return ret























    def lookup(self, keys=None, policy=None, scope=None, trace=False, explain=False, validate_schema=False):
        """Lookup a key in hierarchy"""
        log.debug("Lookup key %s with scope: %s", keys, scope)
        assert isinstance(keys, list), f"Got {keys}"

        query = Query(app=self)
        ret = {}
        for key in keys:
            ret[key] = query.exec(key=key, scope=scope, policy=policy, trace=trace, explain=explain, validate_schema=validate_schema)
        return ret

    def dump_schema(self):
        """Dump configuration schema"""

        ret1 = BackendsManager.get_schema(KheopsPlugins, mode="parts")
        ret2 = RulesManager.get_schema(KheopsPlugins)
        print(json.dumps(ret1, indent=2))
        return

        # ret = self.schema
        # ret["patternProperties"][".*"]["properties"]["tree"]["items"]["properties"] = ret1
        # ret["patternProperties"][".*"]["properties"]["tree"]["items"] = ret2

        # print(json.dumps(ret, indent=2))

    def gen_docs(self):
        """ Generate documentation"""


        print("WIP")
        return None

        # src = {
        #        "app": {
        #            "config_schema": None,
        #            "plugin_managers": {
        #                    'tree': None,
        #                    'rules': None,
        #                }
        #            }
        #
        # r1 = BackendsManager.get_schema(KheopsPlugins, mode='parts')

        # print (json.dumps(r1, indent=2))

        # ret = {
        #
        #    }

        # part_config = r1.get('config_schema', None)
        # part_item = r1['items']['core_schema']
        # part_item_plugins = r1['items']['plugin']

        # for kind, plugins in part_item_plugins.items():

        #    for plugin_name, schema in plugins.items():
        #        part_item_
