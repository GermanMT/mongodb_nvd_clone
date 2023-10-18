from motor.motor_asyncio import AsyncIOMotorClient
from src import (
    clone_cves,
    clone_cpe_matchs,
    clone_cpes,
    nvd_updater
)

import click

import asyncio

@click.command()
@click.argument('mongodb_uri')
@click.option('--nvd_api', default='')
async def clone(mongodb_uri, nvd_api):
    headers = {
        'apiKey': nvd_api
    }

    client = AsyncIOMotorClient(mongodb_uri)

    if nvd_api:
        delay = 1
    else:
        delay = 6

    await clone_cves(client, delay,  headers)
    
    await clone_cpe_matchs(client, delay, headers)

    await clone_cpes(client, delay, headers)


@click.command()
@click.argument('mongodb_uri')
@click.option('--nvd_api', default='')
async def synchronise_job(mongodb_uri, nvd_api):
    headers = {
        'apiKey': nvd_api
    }

    client = AsyncIOMotorClient(mongodb_uri)

    if nvd_api:
        delay = 1.
    else:
        delay = 6.

    await nvd_updater(client, headers, delay)


@click.group()
async def cli():
    pass

cli.add_command(clone)
cli.add_command(synchronise_job)

if __name__ == '__main__':
    asyncio.run(cli())
