import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/drs"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    import asyncio
    loop = asyncio.new_event_loop()
    async def create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    loop.run_until_complete(create())
    yield
    async def drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    loop.run_until_complete(drop())
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def _transaction():
    """Wrap each test in a DB transaction that rolls back at the end."""
    async with engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)

        async def override_get_db():
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

        app.dependency_overrides[get_db] = override_get_db

        yield session

        await conn.rollback()


@pytest_asyncio.fixture
async def db_session(_transaction: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    yield _transaction


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def user(client: AsyncClient) -> dict:
    uid = uuid.uuid4().hex[:8]
    resp = await client.post("/users/", json={"full_name": f"Alice-{uid}", "email": f"alice-{uid}@example.com"})
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def merchant(client: AsyncClient) -> dict:
    resp = await client.post("/merchants/", json={"business_name": "Acme Corp"})
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def dispute(client: AsyncClient, user: dict, merchant: dict) -> dict:
    resp = await client.post("/disputes/", json={
        "transaction_id": "TXN-DISPUTE-FIXTURE",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "5000.00",
        "currency": "INR",
        "reason_code": "ITEM_NOT_RECEIVED",
    })
    assert resp.status_code == 201
    return resp.json()
