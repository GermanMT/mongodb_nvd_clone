from requests import get

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from time import sleep

from pymongo import InsertOne

cpe_match_uri: str = 'https://services.nvd.nist.gov/rest/json/cpematch/2.0?startIndex='

async def clone_cpe_matchs(client, delay, headers):
    nvd_clone_db: AsyncIOMotorDatabase = client.nvd
    cpe_match_collection: AsyncIOMotorCollection = nvd_clone_db.get_collection('cpe_matchs')
    index: int = 0
    while True:
        actions: list[InsertOne] = []
        while True:
            try:
                response = get(cpe_match_uri + str(index), headers=headers).json()
                sleep(delay)
                break
            except:
                sleep(6)
        for match_string in response['matchStrings']:
            actions.append(InsertOne(match_string['matchString']))
        index += response['resultsPerPage']
        await cpe_match_collection.bulk_write(actions, ordered=False)
        if index == response['totalResults']:
            break
