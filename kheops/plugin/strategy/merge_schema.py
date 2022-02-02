"""Merge Deep strategy Plugin"""

import logging
from jsonmerge import Merger

from kheops.plugin.common import StrategyPlugin

from pprint import pprint


log = logging.getLogger(__name__)


class Plugin(StrategyPlugin):
    """Last strategy plugin"""


    _plugin_name = "merge_schema"
    _schema_props_new = None

    selector = "matched"

    default_merge_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "oneOf": [
            {
                "type": "array",
                "mergeStrategy": "append",
                #                    "mergeStrategy": "arrayMergeById",
            },
            {
                "type": "object",
                "mergeStrategy": "objectMerge",
            },
            {
                "type": "boolean",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "string",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "integer",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "number",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "null",
                "mergeStrategy": "overwrite",
            },
        ],
    }


    #def _init(self):

        # Fetch module config
        # See documentation: https://github.com/clarketm/mergedeep
        #algo = self.ns.config["config"].get("merge_schema_algo", "replace").upper()
        #strategy = getattr(Strategy, algo, None)
        #if strategy is None:
        #    strategies = [i.lower() for i in dir(Strategy) if i.isupper()]
        #    raise Exception(
        #        f"Unknown algorithm: {algo}, please choose one of: {strategies}"
        #    )
        #self.strategy = strategy

    def merge_results(self, candidates: list, rule: dict, query) -> (list, dict):
        """Return results"""

        key = query.key
        results = []


        schema = rule.get("schema", None) or self.default_merge_schema
        merger = Merger(schema)


        result = None
        for index, item in enumerate(candidates):
            new_value = item.data
            try:
                new_value = new_value[key]
            except :
                #print (f"Missing key: {key}")
                continue

            result = merger.merge(result, new_value)



        return result
