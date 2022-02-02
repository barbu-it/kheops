"""Common libraries for plugins"""

import copy
import logging
from kheops.utils import schema_validate
from pprint import pprint

log = logging.getLogger(__name__)


# Vocabulary:
# Key Rules
# ConfPlugin[1]
# StrategyPlugin[1]
# OutPlugin[N]
# Lookup Hierarchy
# ConfPlugin[1]
# ScopePlugin[N]
# BackendPlugin[1]


# Generic classes
class KheopsPlugin:
    plugin_name = None
    plugin_type = None
    plugin_kind = None

    def __init__(self):
        self._init()

    def _init(self):
        """Place holder to init plugins"""
        pass


class KheopsListPlugin(KheopsPlugin):
    plugin_type = "list"

    def process_list(self, item_list) -> list:
        pass


class KheopsItemPlugin(KheopsPlugin):
    plugin_type = "item"

    def process_item(self, item) -> list:
        pass


# Other classes
class BackendCandidate:
    def __init__(self, path=None, data=None, run=None, status=None):
        assert isinstance(run, dict)
        self.path = path
        self.status = status or "unparsed"
        self.run = run or {}
        self.data = data or None

    def __repr__(self):
        return f"Status: {self.status}, Path: {self.path} => {self.data}"


# Specific classes
class ConfPlugin(KheopsListPlugin):
    plugin_kind = "conf"
    schema_prop = {
        "include": {},  # Direct config, DICT
    }

    def process_list(self, item_list) -> list:
        pass


class ScopePlugin(KheopsListPlugin):
    plugin_kind = "scope"

    schema_prop = {
        "_scope": [],  # List of scope modification to apply
        "init": {},
        "loop_N": {},
        "hier_N": {},
    }

    def process_item(self, item_list) -> list:

        pass

    def __init__(self, namespace):
        self.ns = namespace
        super().__init__()


class ScopeExtLoop:
    """This Scope Extension allow to loop over a lookup"""

    schema_props = {
        "properties": {
            "data": {
                "default": None,
                "anyOf": [
                    {"type": "null"},
                    {"type": "string"},
                    {"type": "array"},
                ],
            },
            "var": {
                "type": "string",
                "default": "item",
                "optional": True,
            },
        },
    }

    def loop_over(
        self, lookups, conf, module_name, var_name="item", callback_context=None, callback=None
    ):


        var_name = conf.get("var", var_name)
        var_data_ref = conf.get("data", None)

        if not var_data_ref:
            log.debug("No data to loop over for: %s", var_data_ref)
            return lookups

        ret = []
        for index, lookup in enumerate(lookups):

            var_data = var_data_ref
            if isinstance(var_data_ref, str):
                try:
                    var_data = lookup["_run"]["scope"][var_data]
                except KeyError:
                    log.debug("Ignoring missing '%s' from scope", var_data)
                    continue

            # Run callback
            if callback:
                var_data = callback(var_data, callback_context)

            # Validate generated
            if not isinstance(var_data, list):
                log.warning("Loop data must be a list, got: %s", var_data)
                continue

            # Create new object
            for index, var_value in enumerate(var_data):

                if not module_name in lookup["_run"]:
                    lookup["_run"][module_name] = []

                ctx = {
                    "data_ref": var_data_ref,
                    "index": index,
                    "value": var_value,
                    "variable": var_name,
                }

                new_item = copy.deepcopy(lookup)
                new_item["_run"]["scope"][var_name] = var_value
                new_item["_run"][module_name].append(ctx)

                ret.append(new_item)

        return ret


class BackendPlugin(KheopsItemPlugin):
    plugin_kind = "backend"

    schema_prop = {
        "backend": {},  # GENERIC, String
        "file": {},
        "glob": {},
        "http": {},
        "consul": {},
        "vault": {},
    }

    def fetch_data(self, lookups) -> list:
        raise Exception("Not implemented")

    def __init__(self, namespace):
        self.ns = namespace
        super().__init__()


class StrategyPlugin(KheopsItemPlugin):
    plugin_kind = "strategy"
    schema_prop = {
        "_strategy": {},  # GENERIC, String
        "merge": {},
        "first": {},
        "last": {},
        "smart": {},
        "schema": {},
    }

    def merge_results(self, candidates, rule) -> list:
        pass

    def __init__(self, namespace):
        self.ns = namespace
        super().__init__()


class OutPlugin(KheopsItemPlugin):
    plugin_kind = "out"
    schema_prop = {
        "_out": {},  # GENERIC, List of dict
        "toml": {},
        "validate": {},
    }

    def process_item(self, item) -> list:
        pass


# # Candidate Classes
# # =============================
# # class Candidate:
# #     engine = None
# #     found = False
# #     data = None
# #     run = None
# #     scope = None
# #     key = None
# #
# #     def __init__(self, run):
# #         self.run = copy.deepcopy(run)
# #
# #     def __repr__(self):
# #         return f"{self.__dict__}"
# #
# #     def _report_data(self, data=None):
# #         default_data = {
# #             # "rule": self.config,
# #             "value": self.engine._plugin_value,
# #             "data": self.data,
# #         }
# #         data = data or default_data
# #         data = json.dumps(data, indent=2)  # , sort_keys=True, )
# #         return data


# # Generic Classes
# # =============================
# class PluginClass:
#     """Generic plugin class"""

#     _plugin_type = "none"
#     _plugin_value = None

#     _schema_props_new = "UNSET PLUGIN PROPRIETIES"

#     _schema_props_plugin = {
#         "engine": {
#             "type": "string",
#             "default": "jerakia",
#         },
#         "value": {},
#     }

#     def __repr__(self):
#         kind = self._plugin_type
#         name = self._plugin_name
#         value = getattr(self, "value", "NO VALUE")
#         return f"{kind}.{name}:{value}"

#     def __init__(self, config=None, parent=None, app=None, validate_schema=False):
#         # assert (isinstance(config, dict)), f"Got: {config}"
#         self.parent = parent
#         self.app = app
#         self.config = config or {}

#         self._init()
#         if validate_schema:
#             self._validate()

#     def _init(self):
#         pass

#     def _validate(self):
#         pass


# class PluginBackendClass(PluginClass):
#     """Backend plugin class"""

#     _plugin_type = "backend"

#     def _init(self):
#         pass


# class PluginStrategyClass(PluginClass):
#     """Strategy plugin class"""

#     _plugin_type = "strategy"

#     def _init(self):
#         pass


# class PluginEngineClass(PluginClass):
#     """Engine plugin class"""

#     _plugin_type = "engine"

#     _schema_props_default = {
#         "engine": {
#             "default": "UNSET",
#         },
#         "value": {
#             "default": "UNSET",
#         },
#     }

#     # Default plugin API Methods
#     # =====================
#     def _init(self):
#         assert isinstance(self.config, dict), f"Got: {self.config}"

#     def _validate(self):

#         # Build schema
#         schema_keys = [a for a in dir(self) if a.startswith("_schema_props_")]
#         props = {}
#         for key in schema_keys:
#             schema = getattr(self, key)
#             props.update(schema)
#         self.schema = {
#             "$schema": "http://json-schema.org/draft-07/schema#",
#             "type": "object",
#             "additionalProperties": True,
#             "properties": props,
#         }

#         # log.debug (f"Validate {self.config} against {self.schema}")
#         self.config = schema_validate(self.config, self.schema)
#         return True

#     # Public Methods
#     # =====================
#     def dump(self) -> dict:
#         """Dump plugin configuration"""

#         ret = {
#             "config": self.config,
#         }
#         return ret

#     def lookup_candidates(self, key=None, scope=None) -> list:
#         """Placeholder to return candidates"""
#         raise Exception("Module does not implement this method :(")
#         # It must always return a list of `Candidate` instances

#     # def _example(self):
#     #     print(f"Module does not implement this method :(")
#     #     return None


# # File plugins Extensions
# # =============================


# class PluginFileGlob:
#     """Provide glob functionnality"""

#     _schema_props_glob = {
#         "glob": {
#             "additionalProperties": False,
#             "default": {
#                 "file": "ansible.yaml",
#             },
#             "properties": {
#                 "file": {
#                     "type": "string",
#                     "default": "ansible",
#                     "optional": True,
#                 },
#                 "ext": {
#                     "type": "array",
#                     "default": ["yml", "yaml"],
#                     "optional": True,
#                 },
#             },
#         }
#     }
