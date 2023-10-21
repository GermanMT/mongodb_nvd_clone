from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.background import BackgroundScheduler
from asyncclick import command, argument, option, group
from asyncio import run
from src import clone_cves, clone_cpe_matchs, clone_cpes, nvd_updater


@command()
@argument('mongodb_uri')
@option('--nvd_api', default='')
async def clone(mongodb_uri, nvd_api):
    headers = {'apiKey': nvd_api}

    client = AsyncIOMotorClient(mongodb_uri)

    dbs = await client.list_databases()
    while dbs.alive:
        db = await dbs.next()
        if db['name'] == 'nvd':
            raise Exception("Database have been ready cloned. Delete it or run updater command.")

    if nvd_api:
        delay = 1
    else:
        delay = 6

    await clone_cves(client, delay, headers)

    await clone_cpe_matchs(client, delay, headers)

    await clone_cpes(client, delay, headers)


@command()
@argument('mongodb_uri')
@option('--nvd_api', default='')
async def synchronise(mongodb_uri, nvd_api):
    headers = {'apiKey': nvd_api}

    client = AsyncIOMotorClient(mongodb_uri)

    if nvd_api:
        delay = 1.0
    else:
        delay = 6.0

    scheduler = BackgroundScheduler()
    scheduler.add_job(nvd_updater, 'interval', args=[client, headers, delay], seconds=7200)
    scheduler.start()
    print(print(scheduler.get_jobs()))


@group()
async def cli():
    pass


cli.add_command(clone)
cli.add_command(synchronise)

if __name__ == '__main__':
    run(cli())
