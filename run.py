import argparse
import os

from app import create_app

app = create_app()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Marketplace Flask app.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind.")
    parser.add_argument(
        "--env",
        choices=["development", "production"],
        help="Set FLASK_ENV for config selection.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode (overrides environment).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.env:
        os.environ["FLASK_ENV"] = args.env

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
