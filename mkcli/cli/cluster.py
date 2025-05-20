import typer

HELP: str = "Cli auth context"

app = typer.Typer(no_args_is_help=True, help=HELP)


@app.command()
def create():
    ...


@app.command()
def update():
    ...


@app.command()
def delete():
    ...


@app.command(name='list')
def _list():
    ...


@app.command()
def show():
    ...

