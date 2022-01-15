

import copy
# from pathlib import Path
# from albero.utils import render_template
# from albero.plugin.common import PluginBackendClass
# from pprint import pprint
# 
# import logging
# import anyconfig
# import textwrap

from albero.plugin.common import PluginBackendClass
from pprint import pprint
import logging
log = logging.getLogger(__name__)

class Plugin(PluginBackendClass):

    _plugin_name = "hier"
    _schema_props_new = {
            "hier": {
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
                        "additionalProperties": True,
                        "properties": {
                            "data": {
                                "default": None,
                                "anyOf": [
                                    { "type": "null" },
                                    { "type": "string" },
                                    { "type": "array" },
                                    ]
                                },
                            "var": {
                                "type": "string",
                                "default": "hier_item",
                                "optional": True,
                                },
                            "separator": {
                                "type": "string",
                                "default": "/",
                                "optional": True,
                                },
                            "reversed": {
                                "type": "boolean",
                                "default": False,
                                "optional": True,
                            },
                        },
                    },
                ]
            }
        }



    def process(self, backends: list, ctx: dict) -> (list, dict):

        new_backends = []
        for cand in backends:

            # Init
            plugin_config = cand.get("hier", {})
            hier_data = plugin_config.get("data", None)
            if not hier_data:
                new_backends.append(cand)
                continue

            # Retrieve config data
            hier_var = plugin_config.get("var", "item")
            hier_sep = plugin_config.get("separator", "/")
            if isinstance(hier_data, str):
                hier_data = cand['_run']['scope'].get(hier_data, None)

            # Build a new list

            if isinstance(hier_data, str):
                r = hier_data.split(hier_sep)
            assert (isinstance(r, list)), f"Got: {r}"

            ret1 = []
            for index, part in enumerate(r):

                try:
                    prefix = ret1[index - 1]
                except IndexError:
                    prefix = f'{hier_sep}'
                    prefix = ""
                item = f"{prefix}{part}{hier_sep}"
                ret1.append(item)

            ret2 = []
            for item in ret1:
                _cand = copy.deepcopy(cand)
                run = {
                        "index": index,
                        "hier_value": item,
                        "hier_var": hier_var,
                        }
                _cand['_run']['hier'] = run
                _cand['_run']['scope'][hier_var] = item
                ret2.append(_cand)

            new_backends.extend(ret2)
        return new_backends, ctx


