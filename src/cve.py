from requests import get, ConnectTimeout, ConnectionError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from time import sleep
from pymongo import InsertOne


cve_uri: str = 'https://services.nvd.nist.gov/rest/json/cves/2.0?startIndex='


async def clone_cves(client: AsyncIOMotorClient, delay: float, headers: dict[str, str]):
    cves_collection: AsyncIOMotorCollection = client.nvd.get_collection('cves')
    await cves_collection.create_index('id', unique=True)
    index: int = 0
    while True:
        while True:
            try:
                response = get(cve_uri + str(index), headers=headers).json()
                sleep(delay)
                break
            except (ConnectTimeout, ConnectionError):
                sleep(6)
        actions: list[InsertOne] = []
        for vulnerability in response['vulnerabilities']:
            actions.append(InsertOne(vulnerability['cve']))
        await cves_collection.bulk_write(actions, ordered=False)
        index += response['resultsPerPage']
        if index == response['totalResults']:
            break
