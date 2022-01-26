
from albero.plugin.common import PluginBackendClass
from albero.utils import path_assemble_hier
from pprint import pprint
import logging
import copy

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
                                {"type": "null"},
                                {"type": "string"},
                                {"type": "array"},
                            ],
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
            ],
        }
    }

    def process(self, backends: list, ctx: dict) -> (list, dict):

        new_backends = []

        for cand in backends:

            # Fetch backend data
            plugin_config = cand.get("hier", {})
            hier_data = plugin_config.get("data", None)
            if not hier_data:
                new_backends.append(cand)
                continue

            hier_var = plugin_config.get("var", "item")
            hier_sep = plugin_config.get("separator", "/")

            # Retrieve data to loop over
            if isinstance(hier_data, str):
                # If it's a string, fetch value from scope
                hier_data = cand["_run"]["scope"].get(hier_data, None)

            # Do the hierarchical replacement
            if isinstance(hier_data, (str, list)):
                hier_data = path_assemble_hier(hier_data, hier_sep)

            if not isinstance(hier_data, list):
                log.debug(f"Hier module can't loop over non list data, got: {hier_data} for {cand}")
                continue

            # Build result list
            ret1 = hier_data
            log.debug (f"Hier plugin will loop over: {ret1}")
            ret2 = []
            for index, item in enumerate(ret1):
                _cand = copy.deepcopy(cand)
                run = {
                    "index": index,
                    "hier_value": item,
                    "hier_var": hier_var,
                }
                _cand["_run"]["hier"] = run
                _cand["_run"]["scope"][hier_var] = item
                ret2.append(_cand)

            new_backends.extend(ret2)
        return new_backends, ctx
