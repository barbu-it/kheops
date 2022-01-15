
from pathlib import Path
from jinja2 import Template
import yaml
import json
import glob

from jsonschema import validate, Draft7Validator, validators, exceptions
import collections


import logging
log = logging.getLogger(__name__)


#   # File parsers
#   # =====================
#   
#   class FileParserClass():    
#       
#       def __init__(self, path):    
#           self.path = path    
#   
#       def from_file(self, file):
#           raise Exception ("Not implemented")
#   
#       def from_string(self, data):
#           raise Exception ("Not implemented")
#       
#       def from_dict(self, data):
#           raise Exception ("Not implemented")
#   
#   class FilesYAMLParser(FileParserClass):    
#       def get_data(self):    
#           with open(self.path, "r") as stream:    
#               try:    
#                   return yaml.safe_load(stream)    
#               except yaml.YAMLError as exc:    
#                   raise Exception(exc)    
#                   print(exc)    
#       
#   
#   class FilesJSONParser(FileParserClass):    
#       pass
#   class FilesRawParser(FileParserClass):    
#       pass
#   class FilesTOMLParser(FileParserClass):    
#       pass
#   class FilesCSVParser(FileParserClass):    
#       pass
#   class FilesINIParser(FileParserClass):    
#       pass
#   
#   format_db = {
#       ".raw": FilesRawParser,
#       ".yml": FilesYAMLParser,
#       ".yaml": FilesYAMLParser,  
#       ".json": FilesJSONParser,
#           }


# Utils Methods
# =====================

def render_template(path, params):
    """Render template for a given string"""
    assert (isinstance(params, dict)), f"Got: {params}"
    t = Template(path)
    return t.render(**params)

#def read_file(file):
#    with open(file, 'r') as f:
#        data = f.read().replace('\n', '')
#    return data
#
#
#def parse_file(file, fmt='auto'):
#    print ("DEPRECATED")
#    raise Exception ("parse_file is deprecated")
#
#    data = read_file(file)
#
#    # Autodetect format from file name
#    if fmt == 'auto':
#        p = Path(file)
#        fmt = p.suffix
#    else:
#        fmt = f".{fmt}"
#
#    # Retrieve parser
#    if fmt is None:
#        raise Exception ("No available driver to read file: %s" % p )
#    fmt_cls = format_db.get(fmt, None)
#
#    # Parse content
#    o = fmt_cls(str(p))
#    return o.get_data()

# Schema Methods
# =====================

def _extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):

        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        try:
            for error in validate_properties(
                validator, properties, instance, schema,
            ):
                continue
        except Exception as e:
            print ("CATCHED2222 ", e)

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )


def schema_validate(config, schema):

        # Validate the schema
        DefaultValidatingDraft7Validator = _extend_with_default(Draft7Validator)
        try:
            DefaultValidatingDraft7Validator(schema).validate(config)
        except Exception as e:
            print (e)
            p = list(collections.deque(e.schema_path))
            p = '/'.join([ str(i) for i in p ])
            p = f"schema/{p}"
            raise Exception(
                    f"Failed validating {p} for resource with content: {config} with !!!!!! schema: {schema}"
                    )
        return config

def str_ellipsis(txt, length=120):
    txt = str(txt)
    ret = []
    for string in txt.splitlines():
        string = (string[:length - 4 ] + ' ...') if len(string) > length else string
        ret.append(string)
    ret = '\n'.join(ret)
    return ret
