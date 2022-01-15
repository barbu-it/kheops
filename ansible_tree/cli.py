#!/usr/bin/env python3

# Run like this:
#   python3 python_cli.py -vvvv demo
# Author: mrjk

import os
import anyconfig
import sys
import logging
import argparse
from pprint import pprint

import sys

# Devel tmp
sys.path.append("/home/jez/prj/bell/training/tiger-ansible/ext/ansible-tree")

import ansible_tree.app as Albero

class CmdApp:
    """Main CmdApp"""

    def __init__(self):
        """Start new App"""

        self.get_args()
        self.get_logger(verbose=self.args.verbose, logger_name="ansible_tree")
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
        format2 = "%(asctime)s.%(msecs)03d|%(name)-16s%(levelname)8s: %(message)s"
        format3 = (
            "%(asctime)s.%(msecs)03d"
            + " (%(process)d/%(thread)d) "
            + "%(pathname)s:%(lineno)d:%(funcName)s"
            + ": "
            + "%(levelname)s: %(message)s"
        )
        tformat1 = "%H:%M:%S"
        tformat2 = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(format1, tformat1)

        # Create console handler for logger.
        ch = logging.StreamHandler()
        ch.setLevel(level=logging.DEBUG)
        ch.setFormatter(formatter)
        log.addHandler(ch)

        # Create file handler for logger.
        if isinstance(create_file, str):
            fh = logging.FileHandler(create_file)
            fh.setLevel(level=logging.DEBUG)
            fh.setFormatter(formatter)
            log.addHandler(fh)

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
                self.log.error(f"Subcommand {self.args.command} does not exists.")
        else:
            self.log.error("Missing sub command")
            self.parser.print_help()

    def get_args(self):
        """Prepare command line"""

        # Manage main parser
        parser = argparse.ArgumentParser(description="Albero, to lookup hierarchical data")
        parser.add_argument(
            "-v", "--verbose", action="count", default=0, help="Increase verbosity"
        )
        parser.add_argument("help", action="count", default=0, help="Show usage")
        subparsers = parser.add_subparsers(
            title="subcommands", description="valid subcommands", dest="command"
        )

        # Manage command: demo
        add_p = subparsers.add_parser("lookup")
        add_p.add_argument("-n", "--namespace", help="Namespace name", default='default')
        add_p.add_argument("-f", "--file", help="File with params as dict. Can be stdin - .")
        add_p.add_argument("-e", "--scope", dest="scope_param", action="append", default=[])
        add_p.add_argument("-p", "--policy")
        add_p.add_argument("-t", "--trace", action="store_true")
        add_p.add_argument("-x", "--explain", action="store_true")
        add_p.add_argument("key", default=None,  nargs="*")

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
        self.log.debug(f"Command line vars: {vars(self.args)}")

    def cli_lookup(self):
        """Display how to use logging"""

        config = '/home/jez/prj/bell/training/tiger-ansible/tree.yml'

#        self.log.debug(f"Command line vars: {vars(self.args)}")
        keys = self.args.key or [None] 

        # Parse payload from enf file:
        new_params = {}
        if self.args.file:
            new_params = anyconfig.load(self.args.file, ac_parser="yaml")

        # Parse cli params
        for i in self.args.scope_param:
            r = i.split('=')
            if len(r) != 2:
                raise Exception("Malformed params")
            new_params[r[0]] = r[1]

        self.log.info(f"CLI: {keys} with env: {new_params}")

        app = Albero.App(config=config, namespace=self.args.namespace)
        for key in keys:
            app.lookup(key=key,
                    scope=new_params,
                    trace=self.args.trace,
                    explain=self.args.explain
                    )


if __name__ == "__main__":
    app = CmdApp()
