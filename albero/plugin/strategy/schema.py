import logging
from albero.plugin.common import PluginStrategyClass
from albero.utils import schema_validate, str_ellipsis

log = logging.getLogger(__name__)

import json
from pprint import pprint
from jsonmerge import Merger
from prettytable import PrettyTable


class Plugin(PluginStrategyClass):

    _plugin_name = "schema"
    _schema_props_new = {
        "schema": {
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
                    "type": "array",
                },
                {
                    "type": "object",
                    "additionalProperties": True,
                    "default": {},
                    "properties": {
                        "data": {
                            "default": None,
                            "optional": False,
                            "anyOf": [
                                {"type": "null"},
                                {"type": "string"},
                                {"type": "array"},
                            ],
                        },
                        "var": {
                            "type": "string",
                            "default": "loop_item",
                            "optional": True,
                        },
                    },
                },
            ],
        }
    }

    default_merge_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "oneOf": [
            {
                "type": "array",
                "mergeStrategy": "append",
                #                    "mergeStrategy": "arrayMergeById",
            },
            {
                "type": "object",
                "mergeStrategy": "objectMerge",
            },
            {
                "type": "boolean",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "string",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "integer",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "number",
                "mergeStrategy": "overwrite",
            },
            {
                "type": "null",
                "mergeStrategy": "overwrite",
            },
        ],
    }

    def process(self, candidates: list, rule=None) -> (list, dict):

        trace = rule["trace"]
        explain = rule["explain"]
        schema = rule.get("schema", None) or self.default_merge_schema
        merger = Merger(schema)
        t = PrettyTable()
        t1 = PrettyTable()

        new_candidate = None
        for index, item in enumerate(candidates):
            new_value = item["data"]
            result = merger.merge(new_candidate, new_value)

            backend_info = dict(item["parent"])
            backend_run = backend_info.pop("_run")
            if explain:
                t1.add_row(
                    [
                        index,
                        "\nBackendRun: "
                        + str_ellipsis(
                            json.dumps(
                                backend_run,
                                default=lambda o: "<not serializable>",
                                indent=2,
                            ),
                            70,
                        ),
                        "\nRuleRun: "
                        + str_ellipsis(
                            json.dumps(
                                item["run"],
                                default=lambda o: "<not serializable>",
                                indent=2,
                            ),
                            70,
                        ),
                        "---\nResult: "
                        + str_ellipsis(
                            json.dumps(
                                result, default=lambda o: "<not serializable>", indent=2
                            ),
                            70,
                        ),
                    ]
                )

            if trace:
                t.add_row(
                    [
                        index,
                        "---\nBackendConfig: "
                        + str_ellipsis(
                            json.dumps(
                                backend_info,
                                default=lambda o: "<not serializable>",
                                indent=2,
                            ),
                            70,
                        )
                        + "\nBackendRun: "
                        + str_ellipsis(
                            json.dumps(
                                backend_run,
                                default=lambda o: "<not serializable>",
                                indent=2,
                            ),
                            70,
                        ),
                        "---\nRuleConfig: "
                        + str_ellipsis(
                            json.dumps(
                                rule, default=lambda o: "<not serializable>", indent=2
                            ),
                            70,
                        )
                        + "\nRuleRun: "
                        + str_ellipsis(
                            json.dumps(
                                item["run"],
                                default=lambda o: "<not serializable>",
                                indent=2,
                            ),
                            70,
                        )
                        +
                        #'\nSource: ' + str_ellipsis(json.dumps(
                        #        new_candidate,
                        #        default=lambda o: '<not serializable>', indent=2), 70) +
                        "\nNew data: "
                        + str_ellipsis(
                            json.dumps(
                                new_value,
                                default=lambda o: "<not serializable>",
                                indent=2,
                            ),
                            70,
                        ),
                        "---\nResult: "
                        + str_ellipsis(
                            json.dumps(
                                result, default=lambda o: "<not serializable>", indent=2
                            ),
                            70,
                        ),
                    ]
                )
            new_candidate = result

        if trace:
            t.field_names = ["Index", "Backend", "Rule", "Data"]
            t.align = "l"
            print(t)
        if explain:
            t1.field_names = ["Index", "Backend", "Rule", "Data"]
            t1.align = "l"
            print("Explain:\n" + repr(t1))

        return new_candidate
