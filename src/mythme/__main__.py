"""Find and record programs on MythTV

Arguments:
----------
    $ mythme [options]

Options:
--------
    --host    Server host (default: 0.0.0.0)
    --port    Server port (default: 8000)


Documentation:
--------------
- https://github.com/donaldoakes/mythme#readme

"""

import os
import re
import argparse
import uvicorn

DIR = os.path.normpath(f"{os.path.dirname(__file__)}")
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")


def main() -> None:
    """Find and record programs on MythTV"""

    parser = argparse.ArgumentParser(
        prog="mythme", description="Find and record programs on MythTV"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"mythme: {get_version()}",
        help="Show mythme's version",
    )
    parser.add_argument("--host", help="Server host", default="0.0.0.0")
    parser.add_argument("--port", help="Server port", default=8000)

    args = parser.parse_args()

    uvicorn.run("mythme.api.main:app", host=args.host, port=args.port, app_dir="src")


def get_version():
    init = open(os.path.join(DIR, "__init__.py")).read()
    match = VERSION_RE.search(init)
    return match.group(1) if match else "0"


if __name__ == "__main__":
    main()
