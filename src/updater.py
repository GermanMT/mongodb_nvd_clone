from datetime import datetime, timedelta
from time import sleep
from typing import Any
from dateutil.parser import parse
from pymongo import ReplaceOne
from requests import get, ConnectTimeout, ConnectionError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


CLIENT = None
DELAY: float = 0.

async def nvd_updater(client: AsyncIOMotorClient, headers: dict[str, str], delay: float) -> None:
    global CLIENT
    global DELAY
    CLIENT: AsyncIOMotorClient = client
    DELAY: float = delay
    
    now = datetime.now()
    two_hours = timedelta(hours=2)
    start_date = (now - two_hours).isoformat()
    end_date = now.isoformat()
    await update_cves(start_date, end_date, headers)
    await update_cpe_matchs(start_date, end_date, headers)
    await update_cpes(start_date, end_date, headers)


async def update_cves(start_date: str, end_date: str, headers: dict[str, str]) -> None:
    while True:
        try:
            response = get('https://services.nvd.nist.gov/rest/json/cves/2.0?', params={'pubStartDate': str(start_date),'pubEndDate': str(end_date)}, headers=headers).json()
            sleep(DELAY)
            break
        except (ConnectTimeout, ConnectionError):
            sleep(6)
    actions = await sanitize_cves(response)
    await bulk_write_actions(actions, 'cves')
    while True:
        try:
            response = get('https://services.nvd.nist.gov/rest/json/cves/2.0?', params={'lastModStartDate': str(start_date), 'lastModEndDate': str(end_date)}, headers=headers).json()
            sleep(DELAY)
            break
        except (ConnectTimeout, ConnectionError):
            sleep(6)
    actions = await sanitize_cves(response)
    await bulk_write_actions(actions, 'cves')

async def update_cpe_matchs(start_date: str, end_date: str, headers: dict[str, str]) -> None:
    while True:
        try:
            response = get('https://services.nvd.nist.gov/rest/json/cpematch/2.0?startIndex=', params={'lastModStartDate': str(start_date),'lastModEndDate': str(end_date)}, headers=headers).json()
            sleep(DELAY)
            break
        except (ConnectTimeout, ConnectionError):
            sleep(6)
    actions = await sanitize_cpe_matchs(response)
    await bulk_write_actions(actions, 'cpe_matchs')


async def update_cpes(start_date: str, end_date: str, headers: dict[str, str]) -> None:
    while True:
        try:
            response = get('https://services.nvd.nist.gov/rest/json/cpes/2.0?startIndex=', params={'lastModStartDate': str(start_date),'lastModEndDate': str(end_date)}, headers=headers).json()
            sleep(DELAY)
            break
        except (ConnectTimeout, ConnectionError):
            sleep(6)
    actions = await sanitize_cpes(response)
    await bulk_write_actions(actions, 'cpes')


async def sanitize_cves(response: dict[str, Any]) -> list[Any]:
    actions: list[Any] = []
    for cve in response['vulnerabilities']:
        cve = cve['cve']
        cve['published'] = parse(cve['published'])
        cve['lastModified'] = parse(cve['lastModified'])
        actions.append(ReplaceOne({'id': cve['id']}, cve, upsert=True))
    return actions


async def sanitize_cpe_matchs(response: dict[str, Any]) -> list[Any]:
    actions: list[Any] = []
    for cpe_match in response['matchStrings']:
        cpe_match = cpe_match['matchString']
        cpe_match['lastModified'] = parse(cpe_match['lastModified'])
        cpe_match['cpeLastModified'] = parse(cpe_match['cpeLastModified'])
        cpe_match['created'] = parse(cpe_match['created'])
        actions.append(ReplaceOne({'id': cpe_match['id']}, cpe_match, upsert=True))
    return actions


async def sanitize_cpes(response: dict[str, Any]) -> list[Any]:
    actions: list[Any] = []
    for cpe in response['products']:
        cpe = cpe['cpe']
        cpe['lastModified'] = parse(cpe['lastModified'])
        cpe['created'] = parse(cpe['created'])
        actions.append(ReplaceOne({'id': cpe['id']}, cpe, upsert=True))
    return actions

async def bulk_write_actions(actions: list[Any], collection_name: str) -> None:
    nvd_clone_db: AsyncIOMotorDatabase = CLIENT.nvd
    collection: AsyncIOMotorCollection = nvd_clone_db.get_collection(collection_name)
    await collection.bulk_write(actions, ordered=True)