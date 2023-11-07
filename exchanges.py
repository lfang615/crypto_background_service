import ccxt.async_support as ccxt
from abc import ABC, abstractmethod
from logger import AsyncLogger
from redisservice import AsyncRedisService as redis_service
from enum import Enum
import json

class Exchange(str, Enum):
    MEXC = "mexc"

class AbstractExchange(ABC):

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    async def get_symbols_details(self):
        pass

class MexcExchange(AbstractExchange):
    def __init__(self, api_key: str, api_secret: str):
        self._logger = AsyncLogger().get_logger()
        super().__init__(api_key, api_secret)
        self.exchange = ccxt.mexc({
            'apiKey': self.api_key,
            'secret': self.api_secret,
    })
    
    async def get_symbols_details(self):
        try:
            self._logger.info("Fetching symbols details from Mexc BEGIN...")
            market_details = await self.exchange.fetch_swap_markets()
            await self.exchange.close()      
            symbols_details = []
            for s in market_details:
                symbols_details.append({
                    "symbol": s['info']["symbol"],
                    "minLeverage": s['info']["minLeverage"],
                    "maxLeverage": s['info']["maxLeverage"],
                    "maintenanceMarginRate": s['info']["maintenanceMarginRate"],
                    "initialMarginRate": s['info']["initialMarginRate"],
                    "maxSize": s['info']['maxVol']                    
                })
            
            for s in symbols_details:
                await redis_service().set_value(f"{Exchange.MEXC.value}:{s['symbol']}", json.dumps(s))
            self._logger.info("Fetching symbols details from Mexc END...")
        except Exception as e:
            self._logger.error("Error while fetching symbols details from Mexc: {}".format(e))
            raise e

        