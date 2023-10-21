from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


async def create_indexes(client: AsyncIOMotorClient) -> None:
    nvd_clone_db: AsyncIOMotorDatabase = client.nvd
    cves_collection: AsyncIOMotorCollection = nvd_clone_db.get_collection('cves')
    cpe_match_collection: AsyncIOMotorCollection = nvd_clone_db.get_collection('cpe_matchs')
    cpes_collection: AsyncIOMotorCollection = nvd_clone_db.get_collection('cpes')
    await cves_collection.create_index('id', unique=True)
    await cpe_match_collection.create_index('matchCriteriaId', unique=True)
    await cpes_collection.create_index('cpeNameId', unique=True)
