

import copy
from pathlib import Path
from albero.utils import render_template
from albero.plugin.common import PluginBackendClass
from pprint import pprint

import logging
import anyconfig
import textwrap


class Plugin(PluginBackendClass):

    _plugin_name = "loop"
    _schema_props_new = {
        "loop": {
            "default": None,
            "optional": True,
            "oneOf": [
                {
                    "type": "null",        
                },
                {
                    "type": "string",        
                },
                {
                    "type": "object",        
                    "additionalProperties": True,        
                    "default": {},
                    "properties": {    
                        "data": {    
                            "default": None,
                            "optional": False,    
                            "anyOf":[
                                    {"type": "null"},
                                    {"type": "string"},
                                    {"type": "array"},
                                ]
                        },    
                        "var": {    
                            "type": "string",    
                            "default": "loop_item",    
                            "optional": True,    
                        },    
                    }, 
                },
            ]
        }
    }    


    def process(self, backends: list, ctx: dict) -> (list, dict):


        new_backends = []
        for cand in backends:
            cand = dict(cand)

            # Init
            loop_config = cand.get("loop", {})
            loop_data = loop_config.get("data", None)
            if not loop_data:
                new_backends.append(cand)
                continue

            # Retrieve config data
            loop_var = loop_config.get("var", "item")
            if isinstance(loop_data, str):
                loop_data = cand['_run']['scope'].get(loop_data, None)
            assert (isinstance(loop_data, list)), f"Got: {loop_data}"

            # Build a new list
            ret = []
            for idx, item in enumerate(loop_data):
                _cand = copy.deepcopy(cand)
                run = {
                        "loop_index": idx,
                        "loop_value": item,
                        "loop_var": loop_var,
                        }
                _cand['_run']['loop'] = run
                _cand['_run']['scope'][loop_var] = item
                #_cand.scope[loop_var] = item
                ret.append(_cand)
            
            new_backends.extend(ret)

        return new_backends, ctx



