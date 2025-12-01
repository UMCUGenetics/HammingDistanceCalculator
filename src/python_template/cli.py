import typer


def get_hello_msg(name: str = "World"):
    """
    Returns a greeting message.

    Args:
        name (str): The name to greet. Defaults to "World".

    Returns:
        str: A greeting message.
    """
    msg = f"Hello {name}!"

    return msg


cli = typer.Typer()


@cli.command()
def hello(name: str):
    """Prints a greeting message."""
    msg = get_hello_msg(name)
    print(msg)


if __name__ == "__main__":
    cli()
