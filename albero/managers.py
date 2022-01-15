
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


from albero.utils import schema_validate, str_ellipsis
import albero.plugin as AlberoPlugins

log = logging.getLogger(__name__)


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

class Manager():

    plugins_kind = []

    _schema_props_default = {}
    _schema_props_default = {}

    @classmethod
    def get_schema(cls, plugins_db):
        pprint (cls.plugins_kind)

        ret = {}
        ret3 = []

        for kind in cls.plugins_kind:
            ret[kind] = {}
            plugin_kind = getattr(plugins_db, kind)

            for plugin_name in [i for i in dir(plugin_kind) if not i.startswith('_')]:
                plugin = getattr(plugin_kind, plugin_name)
                print (plugin.Plugin)
                #pprint (dir(plugin))
                plugin_cls = getattr(plugin, 'Plugin', None)
                if plugin_cls:
                    schema_props = getattr(plugin_cls, '_schema_props_new', 'MISSING ITEM')
                    if schema_props:
                        ret[kind][plugin_name] = schema_props
                        print (plugin_name)
                        ret3.append( schema_props )

        ret3.append( cls._schema_props_new )

        ret1 = cls._schema_props_default
        ret1["$def"]["items"] = ret3
        return ret1


class BackendsManager(Manager):

    plugins_kind = ['engine', 'backend']

    _schema_props_new = {
                        "engine": {    
                            "type": "string",    
                            "default": "jerakia",    
                            "optional": False,    
                        },    
                        "value": {    
                            "default": 'UNSET',
                            "optional": False,    
                        },    
                        #### INSERT HERE SUBSCHEMA !!!!!
                    }

    _schema_props_default = {        
            "$schema": 'http://json-schema.org/draft-04/schema#',        
            "default": "",
            "$def": {
                "items": {},
                },
            "oneOf": [
                {
                    "type": "string",        
                    "default": "BLAAAAHHH"
                },
                {
                    "type": "object",        
                    "additionalProperties": True,        
                    "default": {},
                    "properties":  { "$ref": "#/$defs/name" },   
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
        # THIS MAKE A BUG !!!! self.plugin_loader = LoadPlugin(AlberoPlugins)


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
        plugin_loader = LoadPlugin(AlberoPlugins)
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
        plugin_loader = LoadPlugin(AlberoPlugins)

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



class RulesManager(Manager):

    plugins_kind = ['strategy']

    _schema_props_new = {
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
            "strategy": {
                "type": "string",
                "default": "schema",
                # "default": "last",
                "optional": True,
                # "enum": ["first", "last", "merge"],
                },

            "trace": {
                "type": "boolean",
                "default": False,
                },
            "explain": {
                "type": "boolean",
                "default": False,
                },
            }

    _schema_props_default = {        
            "$schema": 'http://json-schema.org/draft-04/schema#',        
            "default": "",
            "$def": {
                "items": {},
                },
            "oneOf": [
                {
                    "type": "string",        
                    "default": "BLAAAAHHH"
                },
                {
                    "type": "object",        
                    "additionalProperties": True,        
                    "default": {},
                    "properties":  { "$ref": "#/$defs/name" },   
                },
            ]
        }    

    OLD_rule_schema = {
        "$schema": 'http://json-schema.org/draft-04/schema#',
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema": {
                "type": "object",
                "default": None,
                "optional": True,
                "oneOf": [
                    {
                        "type": "null",
                        },
                    {
                        "type": "string",        
                        },
                    {
                        "type": "object",        
                        "additionalProperties": True,        
                        "default": {},
                        "properties":  { "$ref": "#/$defs/name" },   
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
        schema_validate(matched_rule, self._schema_props_default)



        # Prepare plugins
        assert(isinstance(matched_candidates, list)), f"Got: {matched_candidates}"
        assert(isinstance(matched_rule, dict)), f"Got: {matched_rule}"
        strategy = matched_rule.get('strategy', 'schema')
        log.debug(f"Key '{key}' matched rule '{rule}' with '{strategy}' strategy")

        # Load plugin
        log.debug(f"Run strategy: {strategy}")
        plugin_loader = LoadPlugin(AlberoPlugins)
        strategy = plugin_loader.load('strategy',
                strategy,
                )(parent=self, app=self.app)
        new_result = strategy.process(matched_candidates, matched_rule)

        return new_result
