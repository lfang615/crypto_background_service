import redis.asyncio as redis
import config
from logger import AsyncLogger

class AsyncRedisService:
    _instance = None
    _connection = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AsyncRedisService, cls).__new__(cls)
            cls._logger = AsyncLogger().get_logger()            
        return cls._instance

    async def get_connection(self):
        try:
            if not self._connection:
                self._connection = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
        except Exception as e:
            self._logger.error("Error while connecting to Redis: {}".format(e))
        return self._connection

    async def close(self):
        try:
            if self._connection:
                await self._connection.close()
                self._connection = None
        except Exception as e:
            self._logger.error("Error while closing Redis connection: {}".format(e))

    async def get_value(self, key: str):
        try:
            conn = await self.get_connection()
            return await conn.get(key)
        except Exception as e:
            self._logger.error("Error while retrieving value in Redis: {}".format(e))
            raise e  

    async def set_value(self, key: str, value: str):
        try:
            conn = await self.get_connection()
            await conn.set(key, value)
        except Exception as e:
            self._logger.error("Error while setting value in Redis: {}".format(e))
            raise e        