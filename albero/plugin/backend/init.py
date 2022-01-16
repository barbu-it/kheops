from albero.plugin.common import PluginBackendClass
from pprint import pprint
import logging

log = logging.getLogger(__name__)

import copy


class Plugin(PluginBackendClass):

    _plugin_name = "init"
    _schema_props_new = None

    default_engine = "jerakia"

    def process(self, backends: list, ctx: dict) -> (list, dict):

        new_backends = []
        for index, item in enumerate(backends):
            default = {
                "value": item,
            }

            if not isinstance(item, dict):
                item = default

            item["engine"] = item.get("engine", self.default_engine)
            item["_run"] = copy.deepcopy(ctx)
            item["_run"]["backend"] = {
                "index": index,
            }
            new_backends.append(item)

        return new_backends, ctx
