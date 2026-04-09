"""FastAPI application for HyperRisk."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.data.client import HyperliquidClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.hl_client = HyperliquidClient()
    yield
    await app.state.hl_client.close()


app = FastAPI(
    title="HyperRisk",
    description="Liquidation cascade simulator for Hyperliquid perpetual futures",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
