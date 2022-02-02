"""Utils class"""

import collections
import logging
from pathlib import Path

from jinja2 import Template
from jsonschema import Draft7Validator, validators


log = logging.getLogger(__name__)

# Utils Methods
# =====================


def glob_files(path, pattern):
    """Return a list of path that match a glob"""
    log.debug("Search glob '%s' in '%s'", pattern, path)
    path = Path(path)
    ret = path.glob(pattern)
    return [str(i) for i in ret]


def path_assemble_hier(path, sep="/", reverse=False, start_index=0):
    """Append the previous"""

    if isinstance(path, str):
        list_data = path.split(sep)
    elif isinstance(path, list):
        list_data = []
    else:
        raise Exception(f"This function only accepts string or lists, got: {path}")

    if reverse:
        list_data = list_data[::-1]

    if start_index > 0:
        fixed_part = list_data[:start_index]
        if reverse:
            fixed_part = fixed_part[::-1]
        fixed_part = sep.join(fixed_part)

        hier_part = list_data[start_index:]

        new_data = [fixed_part]
        new_data.extend(hier_part)
        list_data = new_data

    assert isinstance(list_data, list), f"Got: {list_data}"
    ret = []
    for index, part in enumerate(list_data):
        prefix = ""
        try:
            prefix = ret[index - 1]
            prefix = f"{prefix}/"
        except IndexError:
            pass
        item = f"{prefix}{part}"
        ret.append(item)
    return ret


def render_template(text, params):
    """Render template for a given string"""
    assert isinstance(params, dict), f"Got: {params}"
    tpl = Template(text)
    return tpl.render(**params)


class Default(dict):
    def __missing__(self, key):
        return ""


def render_template_python(text, params, ignore_missing=True):
    """Render template for a given string"""
    assert isinstance(params, dict), f"Got: {params}"

    if ignore_missing:
        return text.format_map(Default(params))

    try:
        return text.format_map(params)
    except Exception:
        return None


# Schema Methods
# =====================


def _extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):

        for prop, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(prop, subschema["default"])

        try:
            for error in validate_properties(
                validator,
                properties,
                instance,
                schema,
            ):
                continue
        except Exception as err:
            print("CATCHED2222 ", err)

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


def schema_validate(config, schema):
    """Validate a config against a jsonschema"""

    # Validate the schema
    DefaultValidatingDraft7Validator = _extend_with_default(Draft7Validator)
    try:
        DefaultValidatingDraft7Validator(schema).validate(config)
    except Exception as err:
        print(err)
        path = list(collections.deque(err.schema_path))
        path = "/".join([str(i) for i in path])
        path = f"schema/{path}"
        raise Exception(f"Failed validating {path} for resource with content: {config}")
    return config


def str_ellipsis(txt, length=60):
    """Truncate with ellipsis too wide texts"""
    txt = str(txt)
    ret = []
    for string in txt.splitlines():
        string = (string[: length - 4] + " ...") if len(string) > length else string
        ret.append(string)
    ret = "\n".join(ret)
    return ret
