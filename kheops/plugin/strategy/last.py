import logging
from kheops.plugin.common import PluginStrategyClass

log = logging.getLogger(__name__)


class Plugin(PluginStrategyClass):

    _plugin_name = "last"
    _schema_props_new = None

    def process(self, candidates: list, rule=None) -> (list, dict):

        return candidates[-1]
