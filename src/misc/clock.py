"""
    ### The clock module    
    This module simulates clock that checks some conditions
    each unit of time.

    Works asyncrous
    
    IMPORTANT: SYNCHRONIZATION IS CRUCIAL; 
"""
# External modules
import asyncio

# Internal module
from src.data_manipulation import database


async def clock() -> None:
    while True:
        print("Negr")
        await asyncio.sleep(5)


async def initialize_clock(loop: asyncio.AbstractEventLoop) -> None:
    """Initializes clock using `AbstractEventLoop` from main file"""
    clockProcess = asyncio.create_task(clock())
