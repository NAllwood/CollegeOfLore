"""Console script for collegeoflore."""
import backend.app
import click


@click.command()
@click.option("--host", default="0.0.0.0", help="Host address to run on")
@click.option("--port", default=8080, help="TCP port to listen on")
def main(host, port):
    backend.app.main(host=host, port=port)


if __name__ == "__main__":
    main()
