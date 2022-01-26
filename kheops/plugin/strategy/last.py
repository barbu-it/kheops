"""Simple last strategy"""

import logging
from kheops.plugin.common import PluginStrategyClass

log = logging.getLogger(__name__)

class Plugin(PluginStrategyClass):
    """Last strategy plugin"""

    _plugin_name = "last"
    _schema_props_new = None

    def process(self, candidates: list, rule=None) -> (list, dict):
        """Return results"""

        return candidates[-1]
