"""File Backend Code"""

import os
import logging
# from pprint import pprint

import anyconfig
from anyconfig.common.errors import BaseError as AnyConfigBaseError
from kheops.plugin.common import BackendPlugin, BackendCandidate

log = logging.getLogger(__name__)

class Plugin(BackendPlugin):
    """File Backend Plugin

    This backend allows to lookup data into a file hierarchy. All files can be one of the
    cupported by the anyconfig python library.
    """

    plugin_name = "file"
    extensions = {
            ".yml": "yaml",
            ".yaml": "yaml",
            #".toml": "toml",
            #".ini": "ini",
            #".json": "json",
            }

    _schema_config = {
        "backend_file": {
            "title": "File Backend",
            "description": "This backend will look for data inside a file hierarchy.",
            "type": "object",
            "properties": {
                "format": {
                        "title": "File formats",
                        "description": """
                        This object describe which parser is assigned to which extension. 
                        Adding more format will have a performance impact because it will try 
                        to find all of the specified format. It is better to keep this list as small
                        as possible.
                        """,

                        "type": "object",
                        "default": extensions,
                        "additionalProperties": {
                                "title": "Name of the extension with parser",
                                "type": "string"
                            }
                    },
                "path_prefix": {
                        "title": "Prefix string to append to final path",
                        "description": """
                        String to be added at the end of the resolved path. This is useful to change
                        the place of the root hierarchy.
                        """,
                        "type": "string"
                    },
                "path_suffix": {
                        "title": "Suffix string to prepend to final path",
                        "description": """
                        String to be added at the end of the resolved path. This is useful to 
                        provide Hiera or Jerakia support.""",
                        "type": "string",
                        "examples": [
                            { "path_suffix": "/ansible" },
                            ]
                    },
                }
            }
        }


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
                    },
                },
            ]
        },
        "glob": {
            "default": "ansible.yml",
            "anyOf": [
                {
                    "type": "string",
                },
                #                {
                #                    "type": "array",
                #                    "items": {
                #                        "type": "string",
                #                    },
                #                },
            ],
        },
    }

    def _init(self):

        # Build file prefix
        top_path = self.ns.run["path_config"]
        path_prefix = self.config.get("path_prefix", None)
        if path_prefix:
            top_path = os.path.join(top_path, path_prefix)
        self.top_path = top_path

        # Build file sufix
        path_suffix = self.config.get("path_suffix", "")
        if path_suffix == "auto":
            path_suffix = f"/{self.ns.name}"
        self.path_suffix = path_suffix

    def fetch_data(self, config) -> list:

        path = config.get("path")
        if self.path_suffix:
            path = f"{path}{self.path_suffix}"

        raw_data = None
        status = "not_found"
        for ext, parser in self.extensions.items():
            new_path = os.path.join(self.top_path, path + ext)
            log.debug("Looking into %s", new_path)
            if os.path.isfile(new_path):
                status = "found"
                try:
                    raw_data = anyconfig.load(new_path, ac_parser=parser)
                except AnyConfigBaseError as err:
                    status = "broken"
                    raw_data = None
                    log.warning("Could not parse file %s: %s", new_path, err)
                break

        ret = BackendCandidate(
            path=new_path,
            status=status,
            run=config,
            data=raw_data,
        )

        return [ret]
