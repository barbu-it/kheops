

from ansible_tree.plugin.common import PluginBackendClass
from pprint import pprint
import logging
log = logging.getLogger(__name__)

import copy

class Plugin(PluginBackendClass):

    _plugin_name = "init"
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

    default_engine = 'jerakia'


    def process(self, backends: list, ctx: dict) -> (list, dict):

        new_backends = []
        for index, item in enumerate(backends):
            default = {
                        "value": item,
                        }

            if not isinstance(item, dict):
                item = default

            item['engine'] = item.get('engine', self.default_engine )
            item['_run'] =  copy.deepcopy(ctx)
            item['_run']['backend'] = {
                    "index": index,
                    }
            new_backends.append(item)

        return new_backends, ctx


