from typing import Any

from requests import get

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from time import sleep

from pymongo import InsertOne

cve_uri: str = 'https://services.nvd.nist.gov/rest/json/cves/2.0?startIndex='

async def get_products(cve: dict[str, Any]) -> list[str]:
    products: list[str] = []
    if 'configurations' in cve:
        for configuration in cve['configurations']:
            for node in configuration['nodes']:
                if 'cpeMatch' in node:
                    for cpe_match in node['cpeMatch']:
                        product = cpe_match['criteria'].split(':')[4]
                        if product not in products:
                            products.append(product)
    return products

async def clone_cves(client, delay, headers):
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
            except:
                sleep(6)
        for match_string in response['vulnerabilities']:
            cve = match_string['cve']
            cve['products'] = await get_products(cve)
            actions.append(InsertOne(cve))
        index+=response['resultsPerPage']
        await cves_collection.bulk_write(actions, ordered=False)
        if index == response['totalResults']:
            break
