#!/usr/bin/env python3
"""Kheops CLI interface"""

# Run like this:
#   python3 python_cli.py -vvvv demo
# Author: mrjk

import typer
import os
import sys
import logging

import anyconfig
import kheops.app as Kheops
from pathlib import Path


# Devel tmp
sys.path.append("/home/jez/prj/bell/training/tiger-ansible/ext/kheops")





def get_logger(logger_name=None, create_file=False, verbose=0):
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
    return log, loglevel







from enum import Enum
from typing import List, Optional

app = typer.Typer(help="Khéops, hierarchical key/value store")



log, log_level = get_logger(verbose=1, logger_name="kheops")


class OutputFormat(str, Enum):
    yaml = "yaml"
    json = "json"
    toml = "toml"

@app.command()
def lookup(
    ctx: typer.Context,
    

    namespace: str = typer.Option("default", "-n",
        help="Name of the namespace",
        envvar="KHEOPS_NAMESPACE"),
    keys: List[str] = typer.Argument(None,
        help="Key(s) to query" ), 
    scope_param: Optional[List[str]] = typer.Option([], "-e",
        help="Scope variables, var=value",
        ),
    file: Path = typer.Option(None, "-f",
        help="Scope file" ),



    format: OutputFormat = typer.Option("yaml",
        help="Output format",
        ),
    trace: bool = typer.Option(False),
    explain: bool = typer.Option(False, "-X",
        help="Explain the queries"),
    ):
    """Lookup database"""

    keys = keys or [None]
    config = str(ctx.obj["kheops"]["config"])

    new_params = {}
    if file:
        new_params = anyconfig.load(file, ac_parser="yaml")

    # Parse cli params
    for i in scope_param:
        ret = i.split("=")
        if len(ret) != 2:
            raise Exception("Malformed params")
        new_params[ret[0]] = ret[1]

    log.info("CLI: %s with env: %s", keys, new_params)    

    app = Kheops.Kheops(config=config, namespace=namespace)
    ret = app.lookup(
        keys=keys,
        scope=new_params,
        trace=trace,
        explain=explain,
        validate_schema=True,
    )
    typer.echo(anyconfig.dumps(ret, ac_parser=format))


@app.command()
def config():
    typer.echo("Not implemented yet.")

@app.callback()
def main(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),

    config: Path = typer.Option("kheops.yml", "-c",
        help="Last name of person to greet.", 
        envvar="KHEOPS_CONFIG"),

    ):
    """
    Manage users in the awesome CLI app.
    """
    #typer.echo(f"About to execute command: {ctx.invoked_subcommand}")

    log.setLevel(level=verbose)
    ctx.obj = {
        "kheops": {
            "config": config,
        }
    }



if __name__ == "__main__":
    
    #typer.run(CmdApp)
    app()

