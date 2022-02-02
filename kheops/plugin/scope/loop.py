"""Hierarchy backend plugin"""

import copy
import logging

from kheops.plugin.common import ScopePlugin, ScopeExtLoop
from kheops.utils import path_assemble_hier

log = logging.getLogger(__name__)


class Plugin(ScopePlugin,ScopeExtLoop):
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


    def process_items(self, lookups, conf):

        item_name = conf.get('var', "item_loop")
        item_data = conf.get('data', None)

        lookups = self.loop_over(
            lookups,
            conf=conf,
            var_name='item_loop',
            )

        return lookups
