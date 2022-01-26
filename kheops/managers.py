import dpath.util

import logging
from pprint import pprint


from kheops.utils import schema_validate
import kheops.plugin as KheopsPlugins

log = logging.getLogger(__name__)


class LoadPlugin:
    def __init__(self, plugins):
        self.plugins = plugins

    def load(self, kind, name):

        assert isinstance(name, str), f"Got: {name}"

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

        assert hasattr(
            plugin_cls, "Plugin"
        ), f"Plugin {kind}/{name} is not a valid plugin"

        # Return plugin Classe
        return plugin_cls.Plugin


class Manager:
    """Generic manager class"""

    _app_kind = 'core'
    plugins_kind = []
    _schema_props_default = None
    _schema_props_new = None
    _props_position = None

    @classmethod
    def get_schema(cls, plugins_db, mode='full'):
        """Retrieve configuration schema"""

        # Properties
        ret = {
                "core_schema": {},
                "plugin": {},
                }
        ret3 = {}
        for kind in cls.plugins_kind:
            ret['plugin'][kind] = {}
            plugin_kind = getattr(plugins_db, kind)

            for plugin_name in [i for i in dir(plugin_kind) if not i.startswith("_")]:
                plugin = getattr(plugin_kind, plugin_name)
                plugin_cls = getattr(plugin, "Plugin", None)
                if plugin_cls:
                    schema_props = getattr(
                        plugin_cls, "_schema_props_new", "MISSING ITEM"
                    )
                    if schema_props:
                        ret['plugin'][kind][plugin_name + '_schema' ] = schema_props
                        ret3.update(schema_props)
        ret3.update(cls._schema_props_new)

        # Injection
        ret1 = cls._schema_props_default
        position = cls._props_position
        dpath.util.set(ret1, position, ret3)
        ret['core_schema'] = cls._schema_props_new

        if mode == 'full':
            return ret1

        ret4 = {
                "config_schema": {},
                "items": ret,
                }

        return ret4


class BackendsManager(Manager):
    """Backend Manager"""

    _app_kind = 'manager'
    plugins_kind = ["engine", "backend"]

    _schema_props_new = {
        "engine": {
            "type": "string",
            "default": "jerakia",
            "optional": False,
        },
        "value": {
            "default": "UNSET",
            "optional": False,
        },
    }

    _props_position = "oneOf/0/properties"
    _schema_props_default = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "default": "",
        # This does not work :(
        # "$def": {
        #    "props": {},
        #    },
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": True,
                "default": {},
                "title": "object",
                "properties": {},
                "description": "Object to configure a bacjend item",
            },
            {
                "type": "string",
                "default": "BLAAAAHHH",
                "title": "string",
                "description": "Enter a simple string configuration value for default engine",
            },
        ],
    }

    def _validate_item(self, item):
        """Private method to validate sub class"""
        if isinstance(item, str):
            item = {
                "engine": self.config_main.default_engine,
                "value": item,
            }
        item = schema_validate(item, self._schema_props_default)
        assert isinstance(item, dict)
        return item

    def __init__(self, app):
        self.app = app

        self.config_app = app.conf2["config"]["app"]
        self.config_main = app.conf2["config"]["tree"]
        self.config_items = list(app.conf2["tree"])
        # THIS MAKE A BUG !!!! self.plugin_loader = LoadPlugin(KheopsPlugins)

        self.plugins = [
            "init",
            "loop",
            "hier",
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
        plugin_loader = LoadPlugin(KheopsPlugins)
        _run = {
            "key": key,
            "scope": scope,
        }

        # Preprocess backends plugins
        backends = self.config_items
        log.debug(f"Backend preprocessing of {len(backends)} elements")
        for plugin in self.plugins:
            # backend_cls = plugin_loader.load('backend', plugin)
            plugin = plugin_loader.load("backend", plugin)()

            log.debug(f"Run {plugin}")
            new_backend, _run = plugin.process(backends, _run)

            assert isinstance(new_backend, list), f"Got: {new_backend}"
            assert isinstance(_run, dict), f"Got: {_run}"
            backends = new_backend

        # pprint (backends)
        for i in backends:
            assert i.get("engine"), f"Got: {i}"

        log.debug(f"Backend preprocessing made {len(backends)} elements")
        return backends

    def get_results(self, backends, trace=False):

        # Prepare plugins
        plugin_loader = LoadPlugin(KheopsPlugins)

        new_results = []
        for backend in backends:
            # result_cls = result_loader.load('result', result)
            # print ("BACKKENNDNNDNDNDND")
            # pprint(backend)

            engine = plugin_loader.load("engine", backend["engine"])(
                backend, parent=self, app=self.app
            )

            log.debug(f"Run engine: {engine}")
            new_result = engine.process()

            assert isinstance(new_result, list), f"Got: {new_result}"
            new_results.extend(new_result)

        # Filter out? Not here !new_results = [i for i in new_results if i['found'] ]
        # pprint (new_results)
        # print ("OKKKKKKKKKKKKKKKKKKKKKKKKK SO FAR")
        return new_results


class RulesManager(Manager):

    _app_kind = 'rules'
    plugins_kind = ["strategy"]

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

    _props_position = "oneOf/1/properties"
    _schema_props_default = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "default": "",
        "$def": {
            "items": {},
        },
        "oneOf": [
            {"type": "string", "default": "BLAAAAHHH"},
            {
                "type": "object",
                "additionalProperties": True,
                "default": {},
                "properties": {"$ref": "#/$defs/name"},
            },
        ],
    }

    OLD_rule_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
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
                        "properties": {"$ref": "#/$defs/name"},
                    },
                ],
            },
        },
    }

    def __init__(self, app):
        self.app = app

        self.config_app = app.conf2["config"]["app"]
        self.config_main = app.conf2["config"]["rules"]
        self.config_items = list(app.conf2["rules"])

    def get_result(self, candidates, key=None, scope=None, trace=False, explain=False):
        # trace=False

        rules = self.config_items
        key = key or ""

        # Filter out invalid candidates
        matched_candidates = [i for i in candidates if i["found"] == True]
        if len(matched_candidates) == 0:
            log.debug("No matched candidates")
            return None

        # Look for matching key in rules defiunitions
        regex_support = False
        matched_rule = {}
        if regex_support:
            raise Exception("Not Implemented")

        rule = [i for i in rules if i.get("rule") == key]
        if len(rule) == 0:
            log.debug(f"No matched rule for %s, applying defaults", key)
        else:
            matched_rule = rule[0]
            log.debug(f"Matcher rule for {key}: {matched_rule}")

        matched_rule["trace"] = trace
        matched_rule["explain"] = explain
        schema_validate(matched_rule, self._schema_props_default)

        # Prepare plugins
        assert isinstance(matched_candidates, list), f"Got: {matched_candidates}"
        assert isinstance(matched_rule, dict), f"Got: {matched_rule}"
        strategy = matched_rule.get("strategy", "schema")
        log.debug(f"Key '{key}' matched rule '{rule}' with '{strategy}' strategy")

        # Load plugin
        log.debug(f"Run strategy: {strategy}")
        plugin_loader = LoadPlugin(KheopsPlugins)
        strategy = plugin_loader.load(
            "strategy",
            strategy,
        )(parent=self, app=self.app)
        new_result = strategy.process(matched_candidates, matched_rule)

        return new_result
