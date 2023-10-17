from requests import get

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from time import sleep

from pymongo import InsertOne

cpe_uri: str = 'https://services.nvd.nist.gov/rest/json/cpes/2.0?startIndex='

async def clone_cpes(client, delay, headers):
    nvd_clone_db: AsyncIOMotorDatabase = client.nvd
    cpes_collection: AsyncIOMotorCollection = nvd_clone_db.get_collection('cpes')
    index: int = 0
    while True:
        actions: list[InsertOne] = []
        while True:
            try:
                response = get(cpe_uri + str(index), headers=headers).json()
                sleep(delay)
                break
            except:
                sleep(6)
        for product in response['products']:
            actions.append(InsertOne(product['cpe']))
        index+=response['resultsPerPage']
        await cpes_collection.bulk_write(actions, ordered=False)
        if index == response['totalResults']:
            break
