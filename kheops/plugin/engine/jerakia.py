"""Jerakia Engine Code"""

import logging
from pathlib import Path

import anyconfig

from kheops.utils import render_template, glob_files
from kheops.plugin.common import PluginEngineClass, PluginFileGlob  # , Candidate


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


class Plugin(PluginEngineClass, PluginFileGlob):
    """Generic Plugin Class"""

    _plugin_name = "jerakia"

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

        paths = self.config.get("path", self.config.get("value"))
        if isinstance(paths, str):
            paths = [paths]
        elif isinstance(paths, list):
            pass
        else:
            raise Exception(
                f"Unsupported path value, expected str or dict, got: {paths} in {self.config}"
            )

        self.paths = paths
        self.value = paths

    def _paths_template(self, scope):

        # Manage loops
        paths = self.paths

        # Manage var substr
        ret = []
        for path in paths:
            path = render_template(path, scope)
            ret.append(path)

        log.debug("Render pattern: %s", ret)

        return ret

    def _show_paths(self, path_top, scope):

        parsed = self._paths_template(scope)
        log.debug("Expanded paths to: %s", parsed)

        # Look for files (NOT BE HERE !!!)
        ret3 = []
        for item in parsed:
            globbed = glob_files(path_top / item, "ansible.yaml")
            ret3.extend(globbed)
        log.debug("Matched globs: %s", ret3)

        return ret3

    def process(self):
        """return results"""

        # Detect path root and path prefix
        path_root = self.app.run["path_root"]
        path_prefix = self.app.conf2["config"]["tree"]["prefix"]

        if path_prefix:
            path_prefix = Path(path_prefix)
            if path_prefix.is_absolute():
                path_top = path_prefix
            else:
                path_top = Path(path_root) / path_prefix
        else:
            path_top = path_root

        log.debug("Path Top: %s", path_top)

        scope = self.config["_run"]["scope"]
        key = self.config["_run"]["key"]
        assert isinstance(scope, dict), f"Got: {scope}"
        assert isinstance(key, (str, type(None))), f"Got: {key}"

        # t = self._show_paths(path_top, scope)

        ret = []
        for index, path in enumerate(self._show_paths(path_top, scope)):
            log.debug("Reading file: %s", path)
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

            # Assemble relative path
            try:
                rel_path = Path(path).resolve().relative_to(Path.cwd())
            except ValueError:
                rel_path = Path(path).resolve()

            # Build result object
            result = {}
            result["run"] = {
                "index": index,
                "path": path,
                "rel_path": str(rel_path),
            }
            result["parent"] = self.config
            result["data"] = data
            result["found"] = found

            ret.append(result)

        return ret
