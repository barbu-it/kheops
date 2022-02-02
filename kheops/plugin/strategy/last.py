"""Last strategy Plugin"""

import logging
from kheops.plugin2.common import StrategyPlugin

log = logging.getLogger(__name__)

#class Plugin(PluginStrategyClass):

class Plugin(StrategyPlugin):
    """Last strategy plugin"""

    _plugin_name = "last"
    _schema_props_new = None

    selector = 'last'

    def merge_results(self, candidates: list, rule: dict, query) -> (list, dict):
        """Return results"""

        key = query.key
        result = None

        for cand in reversed(candidates):
            #try:
            data = cand.data
            
            if key is None:
                result = data
            else:
                if isinstance(data, dict):
                    try:
                        result = data[key]
                        break
                    except KeyError:
                        pass
                    
            #else:
            #    raise Exception(f"Data must be a dict, not something else ... {data}")
                

        return result
