from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.background import BackgroundScheduler
from click import command, argument, option, group
from asyncio import run
from src import (
    clone_cves,
    clone_cpe_matchs,
    clone_cpes,
    nvd_updater
)


@command()
@argument('mongodb_uri')
@option('--nvd_api', default='')
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


@command()
@argument('mongodb_uri')
@option('--nvd_api', default='')
async def synchronise_job(mongodb_uri, nvd_api):
    headers = {
        'apiKey': nvd_api
    }

    client = AsyncIOMotorClient(mongodb_uri)

    if nvd_api:
        delay = 1.
    else:
        delay = 6.

    scheduler = BackgroundScheduler()
    scheduler.add_job(nvd_updater, 'interval', args=[client, headers, delay], seconds=7200)
    scheduler.start()


@group()
async def cli():
    pass

cli.add_command(clone)
cli.add_command(synchronise_job)

if __name__ == '__main__':
    run(cli())
