import click
import uvloop
import asyncio

from src.settings import *


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@click.group()
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = kwargs
    return ctx


@cli.command()
@click.pass_context
def recoder(ctx, **kwargs):
    from src.workers import RecodeWorker
    loop = asyncio.get_event_loop()
    recode_worker = RecodeWorker(RECODE_WORKER_OPTION)
    loop.run_until_complete(recode_worker())


@cli.command()
@click.pass_context
def loader(ctx, **kwargs):
    from src.workers import LoadWorker
    loop = asyncio.get_event_loop()
    load_worker = LoadWorker(LOAD_WORKER_OPTION)
    loop.run_until_complete(load_worker())


@cli.command()
@click.pass_context
def extractor(ctx, **kwargs):
    from src.workers import ExtractWorker
    loop = asyncio.get_event_loop()
    EXTRACT_WORKER_OPTION.loop = loop
    extract_worker = ExtractWorker(EXTRACT_WORKER_OPTION)
    loop.run_until_complete(extract_worker())


@cli.command()
@click.pass_context
def writer(ctx, **kwargs):
    from src.workers import WriteWorker
    loop = asyncio.get_event_loop()
    write_worker = WriteWorker(WRITE_WORKER_OPTION)
    loop.run_until_complete(write_worker())


@cli.command()
@click.pass_context
def paper(ctx, **kwargs):
    from src.workers import PaperWorker
    loop = asyncio.get_event_loop()
    PAPER_WORKER_OPTION.loop = loop
    paper_worker = PaperWorker(PAPER_WORKER_OPTION)
    loop.run_until_complete(paper_worker())


def main():
    cli()
