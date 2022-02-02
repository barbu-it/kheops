"""Hierarchy backend plugin"""


import logging

from kheops.plugin.common import ScopePlugin, ScopeExtLoop
from kheops.utils import path_assemble_hier

log = logging.getLogger(__name__)

from pprint import pprint


class Plugin(ScopePlugin, ScopeExtLoop):
    """Hierarchy plugin"""

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
                    "type": "object",
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

    def _process_item(self, data, ctx):

        return path_assemble_hier(
            data,
            sep=ctx["var_split"],
            reverse=ctx["var_reversed"],
            start_index=ctx["var_start"],
        )

    def process_items(self, lookups, conf):

        ctx = {
            "var_split": conf.get("split", "/"),
            "var_reversed": conf.get("reversed", False),
            "var_start": conf.get("start", 0),
        }

        lookups = self.loop_over(
            lookups,
            conf=conf,
            var_name="item_hier",
            callback=self._process_item,
            callback_context=ctx,
        )

        return lookups
