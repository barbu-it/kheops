
import copy
import json
import textwrap
from prettytable import PrettyTable
from pathlib import Path
# from box import Box
from jsonmerge import Merger
import re
import logging
from pprint import pprint
import collections


from ansible_tree.utils import schema_validate, str_ellipsis
import ansible_tree.plugin as TreePlugins

log = logging.getLogger(__name__)




# DEPRECATED class BackendEngineLoader():
# DEPRECATED 
# DEPRECATED     def get_class(self, item):
# DEPRECATED         engine_name = item.get('engine')
# DEPRECATED         assert (isinstance(engine_name, str)), f"Got: {engine_name} for {item}"
# DEPRECATED 
# DEPRECATED         # Check engine presence
# DEPRECATED         if not hasattr(TreePlugins.engine, engine_name):
# DEPRECATED             raise Exception(f"No plugin {engine_name} found for entry {item}!")
# DEPRECATED 
# DEPRECATED         cls = getattr(TreePlugins.engine, engine_name).Plugin
# DEPRECATED         return cls



# def BackendPluginInit(backends, ctx):
# 
#     for be in backends:
#         be.run = {}
#         be.scope = ctx['scope']
#         be.key = ctx['key']
# 
#     return backends

# def BackendPluginHier(backends, ctx):
# 
#     new_backends = []
#     for cand in backends:
# 
#         # Init
#         plugin_config = cand.config.get("hierarchy", None)
#         hier_data = plugin_config.get("data", None)
#         if not hier_data:
#             new_backends.append(cand)
#             continue
# 
#         # Retrieve config data
#         hier_var = plugin_config.get("var", "item")
#         hier_sep = plugin_config.get("separator", "/")
#         if isinstance(hier_data, str):
#             hier_data = cand.scope.get(hier_data, None)
# 
#         # Build a new list
# 
#         pprint (plugin_config)
#         pprint (hier_data)
# 
#         if isinstance(hier_data, str):
#             r = hier_data.split(hier_sep)
#         assert (isinstance(r, list)), f"Got: {r}"
# 
#         ret1 = []
#         for index, part in enumerate(r):
# 
#             try:
#                 prefix = ret1[index - 1]
#             except IndexError:
#                 prefix = f'{hier_sep}'
#                 prefix = ""
#             item = f"{prefix}{part}{hier_sep}"
#             ret1.append(item)
# 
#         ret2 = []
#         for item in ret1:
#             _cand = copy.deepcopy(cand)
#             run = {
#                     "index": index,
#                     "hier_value": item,
#                     "hier_var": hier_var,
#                     }
#             _cand.run['hier'] = run
#             _cand.scope[hier_var] = item
#             ret2.append(_cand)
#         print ("RESULT")
#         pprint (ret2)
# 
#         new_backends.extend(ret2)
#     return new_backends
# 
# 

#def BackendPluginLoop(backends, ctx):
#
#    new_backends = []
#    for cand in backends:
#
#        # Init
#        loop_config = cand.config.get("loop", None)
#        loop_data = loop_config.get("data", None)
#        if not loop_data:
#            new_backends.append(cand)
#            continue
#
#        # Retrieve config data
#        loop_var = loop_config.get("var", "item")
#        if isinstance(loop_data, str):
#            loop_data = cand.scope.get(loop_data, None)
#        assert (isinstance(loop_data, list)), f"Got: {loop_data}"
#
#        # Build a new list
#        ret = []
#        for idx, item in enumerate(loop_data):
#            _cand = copy.deepcopy(cand)
#            run = {
#                    "loop_index": idx,
#                    "loop_value": item,
#                    "loop_var": loop_var,
#                    }
#            _cand.run['loop'] = run
#            _cand.scope[loop_var] = item
#            ret.append(_cand)
#        
#        new_backends.extend(ret)
#
#    return new_backends


class LoadPlugin():

    def __init__(self, plugins):
        self.plugins = plugins

    def load(self, kind, name):

        assert (isinstance(name, str)), f"Got: {name}"

        # Get plugin kind
        try:
            plugins = getattr(self.plugins, kind)
        except Exception as e:
            raise Exception(f"Unknown module kind '{kind}': {e}")

        # Get plugin class
        try:
            plugin_cls = getattr(plugins, name)
        except Exception as e:
            raise Exception(f"Unknown module '{kind}.{name}': {e}")

        assert (hasattr(plugin_cls, 'Plugin')), f'Plugin {kind}/{name} is not a valid plugin'

        # Return plugin Classe
        return plugin_cls.Plugin



class BackendsManager():

    _schema_props_default = {        
            "$schema": 'http://json-schema.org/draft-04/schema#',        
            "default": "",
            "oneOf": [
                {
                    "type": "string",        
                    "default": "BLAAAAHHH"
                },
                {
                    "type": "object",        
                    "additionalProperties": True,        
                    "default": {},
                    "properties": {    
                        "engine": {    
                            "type": "string",    
                            "default": "jerakia",    
                            "optional": False,    
                        },    
                        "value": {    
                            "default": 'UNSET',
                            "optional": False,    
                        },    
                    }, 
                },
            ]
        }    

    def _validate_item(self, item):
        if isinstance(item, str):
            item = {
                    "engine": self.config_main.default_engine,
                    "value": item,
                    }
        item = schema_validate(item, self._schema_props_default)
        assert (isinstance(item, dict))
        return item

    def __init__(self, app):
        self.app = app

        self.config_app = app.conf2['config']['app']
        self.config_main = app.conf2['config']['tree']
        self.config_items = list(app.conf2['tree'])
        # THIS MAKE A BUG !!!! self.plugin_loader = LoadPlugin(TreePlugins)


        self.plugins = [
                'init',
                'loop',
                'hier',
                ]

        # Auto init
        self.backends = self.config_items


    def query(self, key=None, scope=None, trace=False):
        backends = self.get_backends(key=key, scope=scope, trace=trace)
        ret = self.get_results(backends, trace=trace)
        return ret

    def get_backends(self, key=None, scope=None, trace=False):
        log.debug(f"Look for candidates for key '{key}' in backend: {self.backends}")

        # Prepare plugins
        plugin_loader = LoadPlugin(TreePlugins)
        _run = {
                "key": key,
                "scope": scope,
                }

        # Preprocess backends plugins
        backends = self.config_items
        log.debug(f"Backend preprocessing of {len(backends)} elements")
        for plugin in self.plugins:
            #backend_cls = plugin_loader.load('backend', plugin)
            plugin = plugin_loader.load(
                    'backend', plugin
                    )()

            log.debug(f"Run {plugin}")
            new_backend, _run = plugin.process(backends, _run)

            assert(isinstance(new_backend, list)), f"Got: {new_backend}"
            assert(isinstance(_run, dict)), f"Got: {_run}"
            backends = new_backend

        # pprint (backends)
        for i in backends:
            assert (i.get('engine')), f"Got: {i}"

        log.debug(f"Backend preprocessing made {len(backends)} elements")
        return backends


    def get_results(self, backends, trace=False):

        # Prepare plugins
        plugin_loader = LoadPlugin(TreePlugins)

        new_results = []
        for backend in backends:
            #result_cls = result_loader.load('result', result)
            # print ("BACKKENNDNNDNDNDND")
            # pprint(backend)

            engine = plugin_loader.load(
                    'engine', backend['engine']
                    )(
                    backend,
                    parent=self, app=self.app)

            log.debug(f"Run engine: {engine}")
            new_result = engine.process()

            assert(isinstance(new_result, list)), f"Got: {new_result}"
            new_results.extend(new_result)

        # Filter out? Not here !new_results = [i for i in new_results if i['found'] ]
        # pprint (new_results)
        # print ("OKKKKKKKKKKKKKKKKKKKKKKKKK SO FAR")
        return new_results



class RulesManager():

    default_merge_schema = {
        "$schema": 'http://json-schema.org/draft-04/schema#',
        "oneOf": [
            {
                "type": "array",
                "mergeStrategy": "append",
#                    "mergeStrategy": "arrayMergeById",
            },
            {
                "type": "object",
                "mergeStrategy": "objectMerge",
            },
            {
                "type": "boolean",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "string",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "integer",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "number",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "null",
                "mergeStrategy": "overwrite",
            },
        ],
    }

    rule_schema = {
        "$schema": 'http://json-schema.org/draft-04/schema#',
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "rule": {
                "default": ".*",
                "optional": True,
                "oneOf": [
                    {
                    "type": "string",
                        },
                    {
                    "type": "null",
                        },
                    ],
                },
            "trace": {
                "type": "boolean",
                "default": False,
                },
            "explain": {
                "type": "boolean",
                "default": False,
                },
            "strategy": {
                "type": "string",
                "default": "schema",
                # "default": "last",
                "optional": True,
                # "enum": ["first", "last", "merge"],
                },
            "schema": {
                "type": "object",
                "default": None,
                "optional": True,
                "oneOf": [
                    {
                    "type": "string",
                        },
                    {
                    "type": "null",
                        },
                    {
                    "type": "object",
                        },
                    ],
                },
            }
        }


    def __init__(self, app):
        self.app = app

        self.config_app = app.conf2['config']['app']
        self.config_main = app.conf2['config']['rules']
        self.config_items = list(app.conf2['rules'])

    def get_result(self, candidates, key=None, scope=None, trace=False, explain=False):
        #trace=False

        rules = self.config_items
        key = key or ''

        # Filter out invalid candidates
        matched_candidates = [i for i in candidates if i['found'] == True]
        if len(matched_candidates) == 0:
            log.debug("No matched candidates")
            return None


        # Look for matching key in rules defiunitions
        regex_support = False
        matched_rule = {}
        if regex_support:
            raise Exception("Not Implemented")
        else:
            rule = [ i for i in rules if i.get('rule') == key ]
            if len(rule) == 0:
                log.debug(f"No matched rule for {key}, applying defaults")
            else:
                matched_rule = rule[0]
                log.debug(f"Matcher rule for {key}: {matched_rule}")
        
        matched_rule['trace'] = trace
        matched_rule['explain'] = explain
        schema_validate(matched_rule, self.rule_schema)



        # Prepare plugins
        assert(isinstance(matched_candidates, list)), f"Got: {matched_candidates}"
        assert(isinstance(matched_rule, dict)), f"Got: {matched_rule}"
        strategy = matched_rule.get('strategy', 'first')
        log.debug(f"Key '{key}' matched rule '{rule}' with '{strategy}' strategy")

        # Load plugin
        log.debug(f"Run strategy: {strategy}")
        plugin_loader = LoadPlugin(TreePlugins)
        strategy = plugin_loader.load('strategy',
                strategy,
                )(parent=self, app=self.app)
        new_result = strategy.process(matched_candidates, matched_rule)

        return new_result
