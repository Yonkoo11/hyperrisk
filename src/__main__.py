"""Allow running as: python -m src BTC 0.30"""
from src.cli import main
import asyncio

asyncio.run(main())
