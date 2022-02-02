"""File Backend Code"""

import os
import logging
from pathlib import Path

import anyconfig

from kheops.utils import render_template, glob_files, render_template_python
from kheops.plugin2.common import BackendPlugin, BackendCandidate

from pprint import pprint
log = logging.getLogger(__name__)


# class FileCandidate(Candidate):
#    path = None
#
#    def _report_data(self):
#        data = {
#            # "rule": self.config,
#            "value": self.engine._plugin_value,
#            "data": self.data,
#            "path": str(self.path.relative_to(Path.cwd())),
#        }
#        data = dict(self.config)
#        return super()._report_data(data)


#class Plugin(PluginEngineClass, PluginFileGlob):
class Plugin(BackendPlugin):
    """Generic Plugin Class"""

    _plugin_name = "file"

    _plugin_engine = "file"
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

    extensions = {
                '.yml': 'yaml', 
                '.yaml': 'yaml'
                }

    def _init(self):


        # Guess top path
        top_path = self.ns.run['path_config']
        path_prefix = self.ns.config['config'].get('file_path_prefix', None)
        if path_prefix:
            top_path = os.path.join(top_path, path_prefix)
        self.top_path = top_path

        # Fetch module config
        path_suffix = self.ns.config['config'].get('file_path_suffix', "auto")
        if path_suffix == 'auto':
            path_suffix = f"/{self.ns.name}"
        self.path_suffix = path_suffix

    def fetch_data(self, config) -> list:

        path = config.get('path')
        if self.path_suffix:
            path = f"{path}{self.path_suffix}"


        raw_data = None
        status = 'not_found'
        for ext, parser in self.extensions.items():
            new_path = os.path.join(self.top_path, path + ext )

            if os.path.isfile(new_path):
                status = 'found'
                try:
                    raw_data = anyconfig.load(new_path, ac_parser=parser)
                except Exception:
                    status = 'broken'
                    raw_data = None
                break

        ret = BackendCandidate(
            path=new_path,
            status=status,
            run=config,
            data= raw_data,
            )

        return [ret]

