#!/usr/bin/env python3
"""Kheops Query Class"""

import logging
from pprint import pprint
from kheops.managers import BackendsManager, RulesManager

log = logging.getLogger(__name__)


# Query
##########################################


class Query:
    """Kheops Query Class"""

    def __init__(self, app):

        self.app = app

    def exec(self, key=None, scope=None, policy=None, trace=False, explain=False):
        """Execute the query"""

        bmgr = BackendsManager(app=self.app)
        mmgr = RulesManager(app=self.app)

        log.debug("New query created")
        candidates = bmgr.query(key, scope, trace=trace)
        result = mmgr.get_result(candidates, key=key, trace=trace, explain=explain)
        return result

    def dump(self):
        """Dump the query object"""

        ret = {}
        for i in dir(self):
            if not i.startswith("_"):
                ret[i] = getattr(self, i)

        pprint(ret)
