from pathlib import Path
from jinja2 import Template
import yaml
import json
import glob

from jsonschema import validate, Draft7Validator, validators, exceptions
import collections


import logging

log = logging.getLogger(__name__)

# Utils Methods
# =====================

def glob_files(path, pattern):
    log.debug(f"Search glob '{pattern}' in '{path}'")
    p = Path(path)
    ret = p.glob(pattern)
    return [str(i) for i in ret]


def path_assemble_hier(path, sep='/'):
    """Append the previous 

    """

    if isinstance(path, str):
        list_data = path.split(sep)
    elif isinstance(path, list):
        list_data = []
    else:
        raise Exception (f"This function only accepts string or lists, got: {path}")


    assert isinstance(list_data, list), f'Got: {list_data}'
    ret = []    
    for index, part in enumerate(list_data):    
        try:    
            prefix = ret[index - 1]    
        except IndexError:    
            prefix = f"{sep}"    
            prefix = ""    
        item = f"{prefix}{part}{sep}"    
        ret.append(item)    
    return ret



def render_template(path, params):
    """Render template for a given string"""
    assert isinstance(params, dict), f"Got: {params}"
    t = Template(path)
    return t.render(**params)

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
                validator,
                properties,
                instance,
                schema,
            ):
                continue
        except Exception as e:
            print("CATCHED2222 ", e)

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


def schema_validate(config, schema):

    # Validate the schema
    DefaultValidatingDraft7Validator = _extend_with_default(Draft7Validator)
    try:
        DefaultValidatingDraft7Validator(schema).validate(config)
    except Exception as e:
        print(e)
        p = list(collections.deque(e.schema_path))
        p = "/".join([str(i) for i in p])
        p = f"schema/{p}"
        raise Exception(
            f"Failed validating {p} for resource with content: {config} with !!!!!! schema: {schema}"
        )
    return config


def str_ellipsis(txt, length=120):
    txt = str(txt)
    ret = []
    for string in txt.splitlines():
        string = (string[: length - 4] + " ...") if len(string) > length else string
        ret.append(string)
    ret = "\n".join(ret)
    return ret
