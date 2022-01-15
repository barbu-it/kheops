
import logging
from albero.plugin.common import PluginStrategyClass

log = logging.getLogger(__name__)

class Plugin(PluginStrategyClass):

    _plugin_name = "last"

    def process(self, candidates: list, rule=None) -> (list, dict):

        return candidates[-1]

