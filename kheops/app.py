#!/usr/bin/env python3
"""Kheops App interface"""

import sys
import logging
import json
from pathlib import Path

import anyconfig

from kheops.utils import schema_validate
from kheops.query import Query
import kheops.plugin as KheopsPlugins
from kheops.managers import BackendsManager, RulesManager

log = logging.getLogger(__name__)

class App:
    """Main Kheops Application Instance"""

    schema = {
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
        "patternProperties": {
            ".*": {
                "type": "object",
                "optional": True,
                "additionalProperties": False,
                "properties": {
                    "config": {
                        "type": "object",
                        "default": {},
                        "additionalProperties": False,
                        "properties": {
                            "app": {
                                "type": "object",
                                # "default": {},
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
                                },
                            },
                            "tree": {
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
                    "rules": {
                        "type": "array",
                        "default": [],
                        # "arrayItem":  { "$ref": "#/$defs/rules_items" },
                    },
                },
            },
        },
    }

    def __init__(self, config="kheops.yml", namespace="default"):
        conf2 = anyconfig.load(config)
        self.run = {}

        # Validate configuration
        schema_validate(conf2, self.schema)
        try:
            conf2 = conf2[namespace]
        except KeyError:
            log.error("Can't find namespace '%s' in config '%s'", namespace, config)
            sys.exit(1)

        # Get application paths
        # =====================
        # Fetch app root
        if conf2["config"]["app"]["root"]:
            path_root = Path(conf2["config"]["app"]["root"])
            log.debug("Root path is hard coded.")
        else:
            path_root = Path(config).parent
            log.debug("Root path guessed from conf file.")

        # path_prefix = conf2["config"]["app"]["prefix"]
        # if not path_prefix:
        #    path_prefix = ''
        # p = Path(path_prefix)
        # if not p.is_absolute():
        #    p = path_root / p
        #    try:
        #        p = p.resolve().relative_to(Path.cwd().resolve())
        #    except ValueError:
        #        pass

        # Save paths
        path_cwd = str(Path.cwd().resolve())
        path_root = str(path_root.resolve())

        self.run["path_cwd"] = path_cwd
        self.run["path_root"] = path_root

        # self.run['path_prefix'] = str(p.resolve())
        log.debug("Working directory is %s, cwd is: %s", path_root, path_cwd)

        #    path_root = path_root.resolve().relative_to(Path.cwd())

        # conf2["config"]["app"]["root"] = str(path_root)

        # Finish
        self.conf2 = dict(conf2)

        log.debug("Loading config: %s", config)
        log.debug("Root directory is: %s", path_root)

    def lookup(self, key=None, policy=None, scope=None, trace=False, explain=False):
        """Lookup a key in hierarchy"""
        log.debug("Lookup key %s with scope: %s", key, scope)
        query = Query(app=self)
        ret = query.exec(key=key, scope=scope, policy=policy, trace=trace, explain=explain)
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
