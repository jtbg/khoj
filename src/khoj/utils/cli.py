# Standard Packages
import argparse
import pathlib
from importlib.metadata import version

# Internal Packages
from khoj.utils.helpers import resolve_absolute_path
from khoj.utils.yaml import load_config_from_file, parse_config_from_file, save_config_to_file


def cli(args=None):
    # Setup Argument Parser for the Commandline Interface
    parser = argparse.ArgumentParser(description="Start Khoj; An AI personal assistant for your Digital Brain")
    parser.add_argument(
        "--config-file", "-c", default="~/.khoj/khoj.yml", type=pathlib.Path, help="YAML file to configure Khoj"
    )
    parser.add_argument("--gui", action="store_true", default=False, help="Show native desktop GUI. Default: false")
    parser.add_argument(
        "--regenerate",
        action="store_true",
        default=False,
        help="Regenerate model embeddings from source files. Default: false",
    )
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Show verbose conversion logs. Default: 0")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address of the server. Default: 127.0.0.1")
    parser.add_argument("--port", "-p", type=int, default=42110, help="Port of the server. Default: 42110")
    parser.add_argument(
        "--socket",
        type=pathlib.Path,
        help="Path to UNIX socket for server. Use to run server behind reverse proxy. Default: /tmp/uvicorn.sock",
    )
    parser.add_argument("--version", "-V", action="store_true", help="Print the installed Khoj version and exit")
    parser.add_argument("--demo", action="store_true", default=False, help="Run Khoj in demo mode")

    args = parser.parse_args(args)

    args.version_no = version("khoj-assistant")
    if args.version:
        # Show version of khoj installed and exit
        print(args.version_no)
        exit(0)

    # Normalize config_file path to absolute path
    args.config_file = resolve_absolute_path(args.config_file)

    if not args.config_file.exists():
        args.config = None
    else:
        args = migrate_config(args)
        args.config = parse_config_from_file(args.config_file)

    return args


def migrate_config(args):
    raw_config = load_config_from_file(args.config_file)

    # Add version to khoj config schema
    if "version" not in raw_config:
        raw_config["version"] = args.version_no
        save_config_to_file(raw_config, args.config_file)

        # regenerate khoj index on first start of this version
        # this should refresh index and apply index corruption fixes from #325
        args.regenerate = True

    return args
