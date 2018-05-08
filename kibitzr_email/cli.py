import click


@click.argument('email')
def download_emails(email):
    """Save emails to directory"""
    from kibitzr_email.fetcher import download
    download(email)


def bind_commands(cli):
    cli.command()(download_emails)
