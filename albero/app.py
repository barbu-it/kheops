#!/usr/bin/env python3

# import sys
# sys.path.append("/home/jez/prj/bell/training/tiger-ansible/ext/ansible-tree")


import sys
import yaml
import anyconfig
from pprint import pprint

from albero.query import Query
from albero.utils import schema_validate
import anyconfig
# from box import Box
from pathlib import Path

import logging
log = logging.getLogger(__name__)


class App():

    schema = {
        "$schema": 'http://json-schema.org/draft-07/schema#',
        "type": "object",
        "additionalProperties": False,
        "default": {},
        "$def" :{
            'backends_items': {},
            'backends_config': {},
            'rules_items': {},
            'rules_config': {},
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
                                        "default": {},
                                        "additionalProperties": False,
                                        "properties": {
                                            "root": {
                                                "type": "string",
                                                "default": None,
                                            },
                                        },
                                    },

                                "tree": {
                                        #"additionalProperties": False,
                                        "type": "object",
                                        "default": {},
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
                                "properties": { "$ref": "#/$defs/backends_items" },
                                },
                        },
                    "rules": {
                            "type": "array",
                            "default": [],
                            # "arrayItem":  { "$ref": "#/$defs/rules_items" },
                        },
                    },
                },
            }
        }

    def __init__(self, config="albero.yml", namespace='default'):
        conf2 = anyconfig.load(config)

        # Validate configuration
        schema_validate(conf2, self.schema)
        try:
            conf2 = conf2[namespace]
        except KeyError:
            log.error (f"Can't find namespace '{namespace}' in config '{config}'")
            sys.exit(1)

        # Init
        if not conf2['config']['app']['root']:
            conf2['config']['app']['root'] = Path(config).parent
        else:
            conf2['config']['app']['root'] = Path(conf2['config']['app']['root'])

        # Finish
        self.conf2 = dict(conf2)

    def lookup(self, key=None, policy=None, scope=None, trace=False, explain=False):
        log.debug(f"Lookup key {key} with scope: {scope}")
        q = Query(app = self)
        r = q.exec(key=key, scope=scope , policy=policy, trace=trace, explain=explain)

        print ("=== Query Result ===")
        print(anyconfig.dumps(r, ac_parser='yaml'))
        print ("=== Query Result ===")


    def dump_schema(self):

        import json
        import albero.plugin as AlberoPlugins
        from albero.managers import BackendsManager, RulesManager

        r1 = BackendsManager.get_schema(AlberoPlugins)
        r2 = RulesManager.get_schema(AlberoPlugins)

        d = self.schema
        d['patternProperties']['.*']['properties'] ['tree']['items']['properties'] = r1
        d['patternProperties']['.*']['properties'] ['tree']['items'] = r2

        print(json.dumps(d, indent=2))



