from requests import get, ConnectTimeout, ConnectionError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from time import sleep
from pymongo import InsertOne


cpe_uri: str = 'https://services.nvd.nist.gov/rest/json/cpes/2.0?startIndex='


async def clone_cpes(client: AsyncIOMotorClient, delay: float, headers: dict[str, str]):
    cpes_collection: AsyncIOMotorCollection = client.nvd.get_collection('cpes')
    await cpes_collection.create_index('cpeNameId', unique=True)
    index: int = 0
    while True:
        while True:
            try:
                response = get(cpe_uri + str(index), headers=headers).json()
                sleep(delay)
                break
            except (ConnectTimeout, ConnectionError):
                sleep(6)
        actions: list[InsertOne] = []
        for product in response['products']:
            actions.append(InsertOne(product['cpe']))
        await cpes_collection.bulk_write(actions, ordered=False)
        index += response['resultsPerPage']
        if index == response['totalResults']:
            break
