
import json
import logging
#from pprint import pprint

from pathlib import Path
from prettytable import PrettyTable

import kheops.plugin as KheopsPlugins
from kheops.utils import render_template, render_template_python, str_ellipsis

log = logging.getLogger(__name__)
tracer = logging.getLogger(f'{__name__}.explain')


class LoadPlugin:
    """Generic class to load plugins"""

    def __init__(self, plugins):
        self.plugins = plugins

    def load(self, kind, name):

        assert isinstance(name, str), f"Got: {name}"

        # Get plugin kind
        try:
            plugins = getattr(self.plugins, kind)
        except Exception as err:
            raise Exception(f"Unknown module kind '{kind}': {err}")

        # Get plugin class
        try:
            plugin_cls = getattr(plugins, name)
        except Exception as err:
            raise Exception(f"Unknown module '{kind}.{name}': {err}")

        assert hasattr(
            plugin_cls, "Plugin"
        ), f"Plugin {kind}/{name} is not a valid plugin"

        # Return plugin Classe
        return plugin_cls.Plugin


plugin_loader = LoadPlugin(KheopsPlugins)



class Query():

    key = None
    scope = None

    def __init__(self, key, scope):
        self.key = key or None
        self.scope = scope or {}

        self.rule = None


# class QueryController():


    #def exec(self, key=None, scope=None):
    #    query = Query(key, scope)
    #    result = self.processor.exec(query)
    #    return result


class QueryProcessor():
    """QueryProcessor class provides all the methods to be able to make queries"""

    default_match_rule = {
            "key": None,
            "continue": False,
            "strategy": "merge_deep",
            }


    default_lookup_item = {
            "path": None,
            "backend": "file",
            "continue": True,
            }

    #def __init__(self, app):
    #    self.app = app

        #self.config = app.conf2['config'] or {}
        #self.lookups = app.conf2['lookups'] or []
        #self.rules = app.conf2['rules'] or []

    def CHILDREN_INIT(self, config):
        self.config = config
        pass


    #def exec(self, key=None, scope=None):
    def query(self, key=None, scope=None, explain=False):

        if explain:
            tracer.setLevel(logging.DEBUG)

        query = Query(key, scope)

        # Match the KeyRule in keys (RULE CACHE)
            # Get the matching keys
            # Assemble if more than one and merge when continue.
        # Got the Matched rule (RULE CACHE)
            # We'll need strategy, and it's selector field: matched/first/last/all
        #key_rule = self._get_key_rule(key) or {}
        #key_strategy = key_rule.get('strategy', None)
        key_rule = self._exec_get_rule(query)
        log.info("Matched rule for key '%s': %s", query.key, key_rule)


        # Build the lookups [] => []
            # Fetch static config from app (for include and NS:includes ...)
            # Loop over lookups and process each lookup with ScopePlugins
        lookups = self.config.get("lookups", {}).copy()
        parsed_lookups = self._exec_assemble_lookups(lookups, query)

        # Generate explain report
        if explain:
            self._explain_lookups(parsed_lookups)

        # FEtch the module
            # Retrieve the module instance
            # Get it's match policy
            # TODO
        plugin_name = key_rule.get('strategy', None)
        strategy_plugin = plugin_loader.load('strategy', plugin_name)(self)


        # Get the data (strategy.selector)
            # For each entry, ask the backend to return the data: file, http, consul ...
            # Return zero, one or more results depending the strategy.selector
        #result = get_backends_results(strategy, lookups)
        candidates = self._exec_backend_plugins(parsed_lookups, selector=strategy_plugin.selector)


        # Generate explain report
        if explain:
            self._explain_candidates(candidates, query)


        # Apply the merge strategy, recall strategy 
        result = strategy_plugin.merge_results(candidates, key_rule, query)


        # TODO: Apply output plugins
        # result = self._exec_output_plugins(result)

        return result


    def _explain_lookups(self, parsed_lookups):
        """Explain list of lookups"""

        table = PrettyTable()
        for item in parsed_lookups:
            col1 = json.dumps({ k:v for k, v in item.items() if k not in ['_run'] }, default=lambda o: "<not serializable>", indent=2)
            col2 = json.dumps(item['_run'], default=lambda o: "<not serializable>", indent=2)
            table.add_row([
                "\nConfig:"+ str_ellipsis(col1, 60),
                "\nRuntime:"+ str_ellipsis(col2, 60),
                ])
        table.field_names = ["Config", "Runtime"]
        table.align = "l"
        tracer.info("Explain lookups:\n" + str(table))


    def _explain_candidates(self, candidates, query):
        """Explain list of candidates"""

        # TOFIX: query is not needed here !

        table = PrettyTable()
        for item_obj in candidates:
            item = item_obj.__dict__
            item["rel_path"] = str(Path(item['path']).relative_to(Path.cwd()))

            col1 = json.dumps({ k:v for k, v in item.items() if k not in ['run', 'data'] }, default=lambda o: "<not serializable>", indent=2)
            col2 = json.dumps(item['run']['_run'], default=lambda o: "<not serializable>", indent=2)
            col3 = item_obj.data.get(query.key, "NOT FOUND") if query.key is not None else item_obj.data
            col3 = json.dumps(col3, default=lambda o: "<not serializable>", indent=2)
            table.add_row([
                "\nStatus:"+ str_ellipsis(col1, 80),
                "\nRuntime:"+ str_ellipsis(col2, 60),
                "\nData:"+ str_ellipsis(col3, 60),
                ])

        table.field_names = ["Status", "Runtime", "Data"]
        table.align = "l"
        tracer.info("Explain candidates:\n" + str(table))


    def _exec_backend_plugins(self, lookups, selector="matched"):
        selector = 'matched'
        assert (selector in ['last', 'first', 'all', 'matched'])
        assert isinstance(lookups, list)
        #lookups = self.config.get("lookups", {}).copy()

        plugins = {}
        ret = []
        for index, lookup_def in enumerate(lookups):

            # Update object
            lookup_def['_run']['backend_index'] = index

            # Load plugin
            plugin_name = lookup_def["backend"]
            if plugin_name in plugins:
                plugin = plugins[plugin_name]
            else:
                plugin = plugin_loader.load('backend', plugin_name)(namespace=self)

            # Get candidates
            candidates = plugin.fetch_data(lookup_def)

            # Apply selector
            for candidate in candidates:
                if candidate.status == 'found' or selector == 'all':
                    ret.append(candidate)

        return ret




    def _exec_assemble_lookups(self, lookups, query):

        
        assert isinstance(lookups, list)
        assert len(lookups) > 0

        # Init the scope list
        new_lookups1 = []
        for index, lookup_def in enumerate(lookups):
            shortform = False

            if isinstance(lookup_def, str):
                shortform = True
                lookup_def = {
                        'path': lookup_def,
                        }
            assert isinstance(lookup_def, dict)

            new_lookup = dict(self.default_lookup_item)
            new_lookup.update(lookup_def)
            new_lookup['_run'] = {
                        'scope': query.scope,
                        'key': query.key,
                        'conf': {
                            'index': index,
                            }
                        # 'shortform': shortform,
                    }
            new_lookups1.append(new_lookup)

        # Apply lookups modules
        new_lookups2 = []
        for index, lookup in enumerate(new_lookups1):
            plugins = lookup.get("scope", [])

            ret = [lookup]
            for plugin_def in plugins:
                plugin_name = plugin_def.get("module", None)
                
                if plugin_name:
                    plugin = plugin_loader.load('scope', plugin_name)(namespace=self)
                    ret = plugin.process_items(ret, plugin_def)

            new_lookups2.extend(ret)


        # Parse the `path` value with scope variables
        new_lookups3 = []
        for lookup in new_lookups2:
            path = lookup['path']
            scope = lookup['_run']['scope']
            new_path = render_template_python(path, scope, ignore_missing=False)
            if new_path:
                lookup['_run']['raw_path'] = path
                lookup['path'] = new_path
                new_lookups3.append(lookup)
            else:
                log.info("Ignore because of missing scope vars: '%s'", path)

        return new_lookups3


    def _exec_get_rule(self, query, mode='match'):

        key = query.key
        rules = self.config['rules'] or {}

        if mode == "match":
            rule = dict(self.default_match_rule)
            rules = [i for i in rules if i.get('key', None) == key ]
            if len(rules) > 0:
                match = rules[0]
                rule.update(match)
            else:
                log.debug("Applying default rule for key '%s'", key)
                rule = self.default_match_rule
        else:
            raise Exception (f"Mode '{mode}' is not implemented")

        return rule
        





