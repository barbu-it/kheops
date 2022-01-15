#!/usr/bin/env python3

# import sys
# sys.path.append("/home/jez/prj/bell/training/tiger-ansible/ext/ansible-tree")


import sys
import yaml
import anyconfig
from pprint import pprint

from albero.managers import BackendsManager, RulesManager
from albero.utils import schema_validate
import anyconfig
# from box import Box
from pathlib import Path

import logging
log = logging.getLogger(__name__)



# Query
##########################################

class Query():

    def __init__(self, app):

        self.app = app

    def exec(self, key=None, scope=None, policy=None, trace=False, explain=False):

        bm = BackendsManager(app=self.app)
        mm = RulesManager(app=self.app)

        log.debug(f"New query created")
        candidates = bm.query(key, scope, trace=trace)
        result = mm.get_result(candidates, key=key, trace=trace, explain=explain)
        return result

    def dump(self):

        ret = {}
        for i in dir(self):
            if not i.startswith('_'):
                ret[i] = getattr(self, i)

        pprint (ret)


