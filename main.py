import os
import json
import asyncio
from fastapi import FastAPI
import ccxt.async_support as ccxt
from redisservice import AsyncRedisService
from logger import AsyncLogger
from exchanges import MexcExchange
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import config

app = FastAPI()

async def update_mexc_symbol_details():
    while True:        
        try:
            exchange_credentials = await get_exchange_credentials()
            exchange = MexcExchange(exchange_credentials["api_key"], exchange_credentials["api_secret"])
            update_successful = await exchange.get_symbols_details()
            if update_successful:
                AsyncLogger().get_logger().info("Successfully updated symbols details")
                await asyncio.sleep(24 * 60 * 60)  # Sleep for 24 hours
            else:
                await asyncio.sleep(60)
            
        except Exception as e:
            AsyncLogger().get_logger().error("Error while fetching symbols details: {}".format(e))
            raise e
        
async def get_exchange_credentials():
    try:
        db = AsyncIOMotorClient(config.MONGODB_URI)
        db = db[config.MONGODB_DB]
        db = db["exchange_credentials"]
        exchange_credentials = await db.find_one({"name": "mexc"})
        return exchange_credentials
    except Exception as e:
        AsyncLogger().get_logger().error("Error while fetching exchange credentials: {}".format(e))
        raise e

class AppState:
    def __init__(self) -> None:
        self.update_mexc_symbol_details_task = None

@app.on_event("startup")
async def startup_event():
    AsyncLogger()
    AsyncLogger().get_logger().info("Starting up the application...")
    await AsyncRedisService().get_connection()
    app.state.update_mexc_symbol_details_task = asyncio.create_task(update_mexc_symbol_details())
       
@app.on_event("shutdown")
async def shutdown_event():
    AsyncLogger().get_logger().info("Shutting down the application...")
    await AsyncRedisService.close()    