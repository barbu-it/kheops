#!/usr/bin/env python3
"""Kheops CLI interface"""

# Run like this:
#   python3 python_cli.py -vvvv demo
# Author: mrjk

import os
import sys
import logging
import argparse
import anyconfig
import kheops.app as Kheops

# Devel tmp
sys.path.append("/home/jez/prj/bell/training/tiger-ansible/ext/ansible-tree")


class CmdApp:
    """Main CmdApp"""

    def __init__(self):
        """Start new App"""

        self.get_args()
        self.get_logger(verbose=self.args.verbose + 1, logger_name="kheops")
        self.cli()

    def get_logger(self, logger_name=None, create_file=False, verbose=0):
        """Create CmdApp logger"""

        # Take default app name
        if not logger_name:
            logger_name = __name__

        # Manage logging level
        try:
            loglevel = {
                0: logging.ERROR,
                1: logging.WARN,
                2: logging.INFO,
                3: logging.DEBUG,
            }[verbose]
        except KeyError:
            loglevel = logging.DEBUG

        # Create logger for prd_ci
        log = logging.getLogger(logger_name)
        log.setLevel(level=loglevel)

        # Formatters
        format1 = "%(levelname)8s: %(message)s"
        # format2 = "%(asctime)s.%(msecs)03d|%(name)-16s%(levelname)8s: %(message)s"
        # format3 = (
        #    "%(asctime)s.%(msecs)03d"
        #    + " (%(process)d/%(thread)d) "
        #    + "%(pathname)s:%(lineno)d:%(funcName)s"
        #    + ": "
        #    + "%(levelname)s: %(message)s"
        # )
        tformat1 = "%H:%M:%S"
        # tformat2 = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(format1, tformat1)

        # Create console handler for logger.
        stream = logging.StreamHandler()
        stream.setLevel(level=logging.DEBUG)
        stream.setFormatter(formatter)
        log.addHandler(stream)

        # Create file handler for logger.
        if isinstance(create_file, str):
            handler = logging.FileHandler(create_file)
            handler.setLevel(level=logging.DEBUG)
            handler.setFormatter(formatter)
            log.addHandler(handler)

        # Return objects
        self.log = log
        self.loglevel = loglevel

    def cli(self):
        """Main cli command"""

        # Dispatch sub commands
        if self.args.command:
            method = "cli_" + str(self.args.command)
            if hasattr(self, method):
                getattr(self, method)()
            else:
                self.log.error("Subcommand %s does not exists.", self.args.command)
        else:
            self.log.error("Missing sub command")
            self.parser.print_help()

    def get_args(self):
        """Prepare command line"""

        # Manage main parser
        parser = argparse.ArgumentParser(
            description="Kheops, hierarchical data lookup tool",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=int(os.environ.get("KHEOPS_VERBOSE", "0")),
            help="Increase verbosity (KHEOPS_VERBOSE)",
        )
        parser.add_argument(
            "-c",
            "--config",
            default=os.environ.get("KHEOPS_CONFIG", "kheops.yml"),
            help="Kheops configuration file (KHEOPS_CONFIG)",
        )
        # parser.add_argument("help", help="Show usage")
        subparsers = parser.add_subparsers(
            title="subcommands", description="valid subcommands", dest="command"
        )
        # Manage command: schema
        add_p = subparsers.add_parser("schema")
        add_p = subparsers.add_parser("gen_doc")

        # Manage command: lookup2
        add_p = subparsers.add_parser("lookup")
        add_p.add_argument(
            "-n",
            "--namespace",
            help="Namespace name (KHEOPS_NAMESPACE)",
            default=os.environ.get("KHEOPS_NAMESPACE", "default"),
        )
        add_p.add_argument(
            "-f", "--file", help="File with params as dict. Can be stdin - ."
        )
        add_p.add_argument(
            "-e", "--scope", dest="scope_param", action="append", default=[]
        )
        add_p.add_argument("-p", "--policy")
        add_p.add_argument("-t", "--trace", action="store_true")
        add_p.add_argument("-x", "--explain", action="store_true")
        add_p.add_argument(
            "-o",
            "--format",
            choices=["yaml", "json", "xml", "ini", "toml"],
            default="yaml",
            help="Output format",
        )
        add_p.add_argument("keys", default=None, nargs="*")

        # Manage command: demo
        add_p = subparsers.add_parser("demo")
        add_p.add_argument("--env", default=os.environ.get("APP_SETTING", "Unset"))
        add_p.add_argument("--choice", choices=["choice1", "choice2"], type=str)
        add_p.add_argument("-s", "--store", action="store_true")
        add_p.add_argument("-a", "--append", dest="appended", action="append")
        # add_p.add_argument("--short", default=True, required=True)
        # add_p.add_argument("argument1")
        # add_p.add_argument("double_args", nargs=2)
        add_p.add_argument("nargs", nargs="*")

        # Manage command: subcommand2
        upg_p = subparsers.add_parser("subcommand2")
        upg_p.add_argument("name")

        # Register objects
        self.parser = parser
        self.args = parser.parse_args()

    def cli_demo(self):
        """Display how to use logging"""

        self.log.error("Test Critical message")
        self.log.warning("Test Warning message")
        self.log.info("Test Info message")
        self.log.debug("Command line vars: %s", vars(self.args))

    def cli_lookup(self):
        """Lookup database"""

        keys = self.args.keys or [None]

        new_params = {}
        if self.args.file:
            new_params = anyconfig.load(self.args.file, ac_parser="yaml")

        # Parse cli params
        for i in self.args.scope_param:
            ret = i.split("=")
            if len(ret) != 2:
                raise Exception("Malformed params")
            new_params[ret[0]] = ret[1]

        self.log.info("CLI: %s with env: %s", keys, new_params)

        app = Kheops.Kheops(config=self.args.config, namespace=self.args.namespace)
        ret = app.lookup2(
            namespace=self.args.namespace,
            keys=keys,
            scope=new_params,
            trace=self.args.trace,
            explain=self.args.explain,
            validate_schema=True,
        )
        print(anyconfig.dumps(ret, ac_parser=self.args.format))

    def cli_lookup_OLD(self):
        """Display how to use logging"""

        #        self.log.debug(f"Command line vars: {vars(self.args)}")
        keys = self.args.key or [None]

        # Parse payload from enf file:
        new_params = {}
        if self.args.file:
            new_params = anyconfig.load(self.args.file, ac_parser="yaml")

        # Parse cli params
        for i in self.args.scope_param:
            ret = i.split("=")
            if len(ret) != 2:
                raise Exception("Malformed params")
            new_params[ret[0]] = ret[1]

        self.log.info("CLI: %s with env: %s", keys, new_params)

        app = Kheops.App(config=self.args.config, namespace=self.args.namespace)
        # for key in keys:
        ret = app.lookup(
            keys=keys,
            scope=new_params,
            trace=self.args.trace,
            explain=self.args.explain,
            validate_schema=True,
        )
        print(anyconfig.dumps(ret, ac_parser=self.args.format))

    def cli_schema(self):
        """Display configuration schema"""

        app = Kheops.App(config=self.args.config)  # , namespace=self.args.namespace)
        app.dump_schema()

    def cli_gen_doc(self):
        """Generate documentation"""

        app = Kheops.App(config=self.args.config)  # , namespace=self.args.namespace)
        app.gen_docs()


if __name__ == "__main__":
    CmdApp()
