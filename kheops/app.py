#!/usr/bin/env python3

# import sys
# sys.path.append("/home/jez/prj/bell/training/tiger-ansible/ext/ansible-tree")


import sys
import yaml
import anyconfig
from pprint import pprint

from kheops.query import Query
from kheops.utils import schema_validate
import anyconfig

# from box import Box
from pathlib import Path

import logging

log = logging.getLogger(__name__)


class App:

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
                                #"default": {},
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
                                        ]
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
                                        ]
                                    },
                                  }
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
            log.error(f"Can't find namespace '{namespace}' in config '{config}'")
            sys.exit(1)

        # Get application paths
        # =====================
        # Fetch app root
        if conf2["config"]["app"]["root"]:
            path_root = Path(conf2["config"]["app"]["root"])
            log.debug ("Root path is hard coded.")
        else:
            path_root = Path(config).parent
            log.debug ("Root path guessed from conf file.")

        #path_prefix = conf2["config"]["app"]["prefix"]
        #if not path_prefix:
        #    path_prefix = ''
        #p = Path(path_prefix)
        #if not p.is_absolute():
        #    p = path_root / p
        #    try:
        #        p = p.resolve().relative_to(Path.cwd().resolve())
        #    except ValueError:
        #        pass

        # Save paths
        path_cwd = str(Path.cwd().resolve())
        path_root = str(path_root.resolve())

        self.run['path_cwd'] = path_cwd
        self.run['path_root'] = path_root

        #self.run['path_prefix'] = str(p.resolve())
        log.debug (f"Working directory is {path_root} while cwd is: {path_cwd}")


        #    path_root = path_root.resolve().relative_to(Path.cwd())

        #conf2["config"]["app"]["root"] = str(path_root)

        # Finish
        self.conf2 = dict(conf2)

        log.debug("Loading config: %s", config)
        log.debug("Root directory is: %s", path_root)

    def lookup(self, key=None, policy=None, scope=None, trace=False, explain=False):
        log.debug(f"Lookup key {key} with scope: {scope}")
        q = Query(app=self)
        r = q.exec(key=key, scope=scope, policy=policy, trace=trace, explain=explain)

        return r

        #print("=== Query Result ===")
        print(anyconfig.dumps(r, ac_parser=fmt))
        #print("=== Query Result ===")

    def dump_schema(self):

        import json
        import kheops.plugin as KheopsPlugins
        from kheops.managers import BackendsManager, RulesManager

        r1 = BackendsManager.get_schema(KheopsPlugins, mode='parts')
        r2 = RulesManager.get_schema(KheopsPlugins)
        #pprint (r1)
        print(json.dumps(r1, indent=2))
        return

        d = self.schema
        d["patternProperties"][".*"]["properties"]["tree"]["items"]["properties"] = r1
        d["patternProperties"][".*"]["properties"]["tree"]["items"] = r2

        print(json.dumps(d, indent=2))


    def gen_docs(self):

        import json
        import kheops.plugin as KheopsPlugins
        from kheops.managers import BackendsManager, RulesManager
        print ("WIP")

        #src = {
        #        "app": {
        #            "config_schema": None,
        #            "plugin_managers": {
        #                    'tree': None,
        #                    'rules': None,
        #                }
        #            }
        #        
        #r1 = BackendsManager.get_schema(KheopsPlugins, mode='parts')


        #print (json.dumps(r1, indent=2))

        #ret = {
        #    
        #    }

        #part_config = r1.get('config_schema', None)
        #part_item = r1['items']['core_schema']
        #part_item_plugins = r1['items']['plugin']

        #for kind, plugins in part_item_plugins.items():

        #    for plugin_name, schema in plugins.items():
        #        part_item_




