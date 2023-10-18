from requests import get, ConnectTimeout, ConnectionError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from time import sleep
from pymongo import InsertOne


cve_uri: str = 'https://services.nvd.nist.gov/rest/json/cves/2.0?startIndex='


async def clone_cves(client: AsyncIOMotorClient, delay: float, headers: dict[str, str]):
    nvd_clone_db: AsyncIOMotorDatabase = client.nvd
    cves_collection: AsyncIOMotorCollection = nvd_clone_db.get_collection('cves')
    index: int = 0
    while True:
        actions: list[InsertOne] = []
        while True:
            try:
                response = get(cve_uri + str(index), headers=headers).json()
                sleep(delay)
                break
            except (ConnectTimeout, ConnectionError):
                sleep(6)
        for vulnerability in response['vulnerabilities']:
            actions.append(InsertOne(vulnerability['cve']))
        index+=response['resultsPerPage']
        await cves_collection.bulk_write(actions, ordered=False)
        if index == response['totalResults']:
            break
