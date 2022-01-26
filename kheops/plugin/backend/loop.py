import copy
from pathlib import Path
from kheops.utils import render_template
from kheops.plugin.common import PluginBackendClass
from pprint import pprint

import logging
import anyconfig
import textwrap

log = logging.getLogger(__name__)

class Plugin(PluginBackendClass):

    _plugin_name = "loop"
    _plugin_help = (
        """
    This module helps to loop over a backend
    """,
    )
    _schema_props_new = {
        "loop": {
            "description": _plugin_help,
            "default": None,
            "optional": True,
            "examples": [
                {
                    "value": "site/{{ loop_env }}/config/{{ os }}",
                    "loop": {
                        "var": "loop_env",
                        "data": [
                            "dev",
                            "preprod",
                            "prod",
                        ],
                    },
                    "comment": "The module will loop three time over the value, and the variable `loop_env` will consecutely have `dev`, `preprod` and `prod` as value",
                },
                {
                    "value": "site/{{ loop_env2 }}/config/{{ os }}",
                    "loop": {
                        "var": "loop_env2",
                        "data": "my_scope_var",
                    },
                    "comment": "Like the previous example, but it will fetch the list from any scope variables",
                },
                {
                    "loop": None,
                    "comment": "Disable this module, no loop will operate",
                },
                #    "loop": {
                #            "var": "my_var",
                #        },
                #    },
                #    "loop": {
                #            "var": "my_var",
                #        },
                #    "example": "",
                #    },
                #    "loop": {
                #            "var": "my_var",
                #        },
                #    "example": "",
                #    },
            ],
            "oneOf": [
                {
                    "type": "object",
                    "additionalProperties": False,
                    "default": {},
                    "title": "Complete config",
                    "description": "",
                    "properties": {
                        "data": {
                            "default": None,
                            "optional": False,
                            "title": "Module configuration",
                            "description": "Data list used for iterations. It only accept lists as type. It disable the module if set to `null`.",
                            "anyOf": [
                                {
                                    "type": "null",
                                    "title": "Disable Module",
                                    "description": "Disable the module",
                                },
                                {
                                    "type": "string",
                                    "title": "Scope variable",
                                    "description": "Will look the value of the loop list from the scope. TOFIX: What if variablle does not exists?",
                                },
                                {
                                    "type": "array",
                                    "title": "Hardcoded list",
                                    "description": "Simply enter the list of value to be iterated to.",
                                },
                            ],
                        },
                        "var": {
                            "type": "string",
                            "default": "loop_item",
                            "optional": True,
                            "title": "Module configuration",
                            "description": "Name of the variable to be used in templating language",
                        },
                    },
                },
                {
                    "type": "string",
                    "title": "Short config",
                    "description": "If set to string, it will define the name of the variable to lookup into the scope.",
                },
                {
                    "type": "null",
                    "title": "Disable",
                    "description": "If set to null, it disable the module",
                },
            ],
        }
    }

    def process(self, backends: list, ctx: dict) -> (list, dict):

        new_backends = []
        for cand in backends:
            cand = dict(cand)

            # Init
            loop_config = cand.get("loop", {})
            loop_data = loop_config.get("data", None)
            if not loop_data:
                new_backends.append(cand)
                continue

            # Retrieve config data
            loop_var = loop_config.get("var", "item")
            if isinstance(loop_data, str):
                loop_data = cand["_run"]["scope"].get(loop_data, None)
            if not isinstance(loop_data, list):
                log.debug("Got an empty list for loop for var %s, skipping this entry: %s", cand, loop_data)
                continue

            # Build a new list
            ret = []
            for idx, item in enumerate(loop_data):
                _cand = copy.deepcopy(cand)
                run = {
                    "loop_index": idx,
                    "loop_value": item,
                    "loop_var": loop_var,
                }
                _cand["_run"]["loop"] = run
                _cand["_run"]["scope"][loop_var] = item
                # _cand.scope[loop_var] = item
                ret.append(_cand)

            new_backends.extend(ret)

        return new_backends, ctx
