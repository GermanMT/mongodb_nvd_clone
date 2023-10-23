from requests import get, ConnectTimeout, ConnectionError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from time import sleep
from pymongo import InsertOne


cpe_match_uri: str = 'https://services.nvd.nist.gov/rest/json/cpematch/2.0?startIndex='


async def clone_cpe_matchs(client: AsyncIOMotorClient, delay: float, headers: dict[str, str]):
    cpe_match_collection: AsyncIOMotorCollection = client.nvd.get_collection('cpe_matchs')
    await cpe_match_collection.create_index('matchCriteriaId', unique=True)
    index: int = 0
    while True:
        while True:
            try:
                response = get(cpe_match_uri + str(index), headers=headers).json()
                sleep(delay)
                break
            except (ConnectTimeout, ConnectionError):
                sleep(6)
        actions: list[InsertOne] = []
        for match_string in response['matchStrings']:
            actions.append(InsertOne(match_string['matchString']))
        await cpe_match_collection.bulk_write(actions, ordered=False)
        index += response['resultsPerPage']
        if index == response['totalResults']:
            break
