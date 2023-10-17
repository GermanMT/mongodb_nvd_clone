from motor.motor_asyncio import AsyncIOMotorClient
from src import clone_cves, clone_cpe_matchs, clone_cpes

import click

import asyncio

@click.command()
@click.argument('mongodb_uri')
@click.option('--nvd_api', default='')
async def main(mongodb_uri, nvd_api):
    headers = {
        'apiKey': nvd_api
    }

    client = AsyncIOMotorClient(mongodb_uri)

    if nvd_api:
        delay = 1
    else:
        delay = 6

    await clone_cves(client, headers, delay)
    
    await clone_cpe_matchs(client, headers, delay)

    await clone_cpes(client, headers, delay)

if __name__ == '__main__':
    asyncio.run(main())
