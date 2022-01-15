
from pathlib import Path
from albero.utils import render_template
from albero.plugin.common import PluginEngineClass, PluginFileGlob, Candidate
from pprint import pprint

import logging
import anyconfig
import textwrap

log = logging.getLogger(__name__)

class FileCandidate(Candidate):
    path = None

    def _report_data(self):
        data = {
                #"rule": self.config,
                "value": self.engine._plugin_value,
                "data": self.data,
                "path": str(self.path.relative_to(Path.cwd())),
                }
        data = dict(self.config)
        return super()._report_data(data)



class Plugin(PluginEngineClass, PluginFileGlob):

    _plugin_name = 'jerakia'

    ### OLD
    _plugin_engine = "jerakia"
    # _schema_props_files = {
    _schema_props_new = {
            "path": {
                "anyOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "array",
                        "items": {
                            "type": "string",
                            }
                    },
                ]
            }
        }



    def _init(self):

        paths = self.config.get('path', self.config.get('value'))
        if isinstance(paths, str):
            paths = [paths]
        elif isinstance(paths, list):
            pass
        else:
            raise Exception (f"Unsupported path value, expected str or dict, got: {paths} in {self.config}")

        self.paths = paths
        self.value = paths

    def _preprocess(self, scope):

        # Manage loops
        paths = self.paths

        # Manage var substr
        ret = []
        for p in paths:
            p = render_template(p, scope)
            ret.append(p)

        log.debug(f"Render pattern: {ret}")

        return ret


    def _show_paths(self, scope):

        parsed = self._preprocess(scope)
        log.debug(f"Expanded paths to: {parsed}")

        # Look for files (NOT BE HERE !!!)
        ret3 = []
        for p in parsed:
            globbed = self._glob(p)
            ret3.extend(globbed)
        log.debug(f"Matched globs: {ret3}")

        return ret3


    def process(self):


        #scope = self.scope
        # pprint (self.config)
        scope = dict(self.config['_run']['scope'])
        key = self.config['_run']['key']
        assert isinstance(scope, dict), f"Got: {scope}"
        assert isinstance(key, (str, type(None))), f"Got: {key}"

        t = self._show_paths(scope)

        ret = []
        for index, path in enumerate(self._show_paths(scope)):
            log.debug(f"Reading file: {path}")
            # Fetch data
            found = False
            raw_data = anyconfig.load(path, ac_parser="yaml")
            data = None
            if key is None:
                data = raw_data
                found = True
            else:
                try:
                    data = raw_data[key]
                    found = True
                except Exception:
                    pass

            # Build result object
            result = {}
            result['run'] = {
                    'path': path,
                    'rel_path': str(Path(path).relative_to(Path.cwd())),
                    }
            result['parent'] = self.config
            result['data'] = data
            result['found'] = found

            ret.append(result)

        return ret

        ######## OLD

        #    # Read raw file content
        #    data = anyconfig.load(path, ac_parser="yaml")
        #    
        #    ret_obj2 ={
        #            "_run": _run,

        #            }

        #    #### OLD

        #    ret_obj = FileCandidate(self.config)
        #    ret_obj.engine = self
        #    ret_obj.data = None

        #    found = False
        #    if key is None:
        #        ret_obj.data = data
        #        found = True
        #    else:
        #        try:
        #            ret_obj.data = data[key]
        #            found = True
        #        except Exception:
        #            pass

        #    # ret_obj.run['path'] = path
        #    # ret_obj.run['found'] = found
        #    # ret_obj.run['scope'] = scope
        #    # ret_obj.run['key'] = key
        #    be = {
        #            "index": index,
        #            "path": path,
        #            "rel_path": str(Path(path).relative_to(Path.cwd())),
        #            }
        #    #qu = {
        #    #        "scope": scope,
        #    #        "key": key,
        #    #        }
        #    ret_obj.run['backend'] = be
        #    #ret_obj.run['query'] = qu

        #    #log.debug(f"Found value: {ret_obj}")
        #    ret_obj.found = found
        #    ret.append(ret_obj)




