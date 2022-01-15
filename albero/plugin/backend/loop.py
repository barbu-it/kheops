

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
    _schema_props_files = {
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

    sssss_schema_props_default = {        
            "$schema": 'http://json-schema.org/draft-04/schema#',        
            "default": "",
            "oneOf": [
                {
                    "type": "string",        
                    "default": "BLAAAAHHH"
                },
                {
                    "type": "object",        
                    "additionalProperties": True,        
                    "default": {},
                    "properties": {    
                        "engine": {    
                            "type": "string",    
                            "default": "jerakia",    
                            "optional": False,    
                        },    
                        "value": {    
                            "default": 'UNSET',
                            "optional": False,    
                        },    
                    }, 
                },
            ]
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



