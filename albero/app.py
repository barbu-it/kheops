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



#class Query():
#
#    #matcher_merge_schema = {
#    #    "$schema": 'http://json-schema.org/draft-04/schema#',
#    #    "oneOf": [
#    #        {
#    #            "type": "array",
#    #            "mergeStrategy": "append",
##   #                 "mergeStrategy": "arrayMergeById",
#    #        },
#    #        {
#    #            "type": "object",
#    #            "mergeStrategy": "objectMerge",
#    #        },
#    #        {
#    #            "type": "string",
#    #            "mergeStrategy": "overwrite",
#    #        },
#    #        {
#    #            "type": "number",
#    #            "mergeStrategy": "overwrite",
#    #        },
#    #        {
#    #            "type": "null",
#    #            "mergeStrategy": "overwrite",
#    #        },
#    #    ],
#    #}
#
#    def __init__(self, app):
#
#        self.app = app
#
#
#        #self.matcher_schema = {
#        #    "$schema": 'http://json-schema.org/draft-04/schema#',
#        #    "type": "object",
#        #    "additionalProperties": False,
#        #    "properties": {
#        #        "rule": {
#        #            "type": "string",
#        #            "default": ".*",
#        #            "optional": True,
#        #            },
#        #        "strategy": {
#        #            "type": "string",
#        #            "default": "merge",
#        #            "optional": True,
#        #            "enum": ["first", "last", "merge"],
#        #            },
#        #        "schema": {
#        #            "type": "object",
#        #            "default": self.matcher_merge_schema,
#        #            #"default": {},
#        #            "optional": True,
#        #            },
#        #        }
#        #    }
#
#
#
#    def exec(self, key=None, scope=None, policy=None, trace=False, explain=False):
#
#        bm = BackendsManager(app=self.app)
#        mm = RulesManager(app=self.app)
#
#        log.debug(f"New query created")
#        candidates = bm.query(key, scope, trace=trace)
#        result = mm.get_result(candidates, key=key, trace=trace, explain=explain)
#        return result
#
#    def dump(self):
#
#        ret = {}
#        for i in dir(self):
#            if not i.startswith('_'):
#                ret[i] = getattr(self, i)
#
#        pprint (ret)
#


class App():

    schema = {
        "$schema": 'http://json-schema.org/draft-04/schema#',
        "type": "object",
        "additionalProperties": False,
        "default": {},
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
                        },
                    "rules": {
                            "type": "array",
                            "default": [],
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


