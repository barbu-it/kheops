"""Last strategy Plugin"""

import logging
from mergedeep import merge, Strategy

from kheops.plugin.common import StrategyPlugin

from pprint import pprint


log = logging.getLogger(__name__)


class Plugin(StrategyPlugin):
    """Last strategy plugin"""

    _plugin_name = "merge_deep"
    _schema_props_new = None

    selector = "matched"

    def _init(self):

        # Fetch module config
        # See documentation: https://github.com/clarketm/mergedeep
        algo = self.ns.config["config"].get("merge_deep_algo", "replace").upper()
        strategy = getattr(Strategy, algo, None)
        if strategy is None:
            strategies = [i.lower() for i in dir(Strategy) if i.isupper()]
            raise Exception(
                f"Unknown algorithm: {algo}, please choose one of: {strategies}"
            )
        self.strategy = strategy

    def merge_results(self, candidates: list, rule: dict, query) -> (list, dict):
        """Return results"""

        key = query.key
        results = []

        for cand in candidates:

            data = cand.data

            if key is None:
                result = results.append(cand.data)
            else:
                if isinstance(data, dict):
                    try:
                        result = results.append(cand.data[key])
                    except KeyError:
                        pass

            # else:
            #    raise Exception(f"Data must be a dict, not something else ... {data}")

        log.debug("Merging %s results", len(results))
        result = None
        if len(results) > 0:
            result = merge(*results, strategy=self.strategy)

        return result
