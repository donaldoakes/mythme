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

import argparse
import uvicorn


def main() -> None:
    """Find and record programs on MythTV"""

    parser = argparse.ArgumentParser(
        prog="mythme", description="Find and record programs on MythTV"
    )
    parser.add_argument("--host", help="Server host", default="0.0.0.0")
    parser.add_argument("--port", help="Server port", default=8000)

    args = parser.parse_args()

    uvicorn.run("mythme.api.main:app", host=args.host, port=args.port, app_dir="src")


if __name__ == "__main__":
    main()
