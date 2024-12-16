from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class Mongo:
    def __init__(self, uri: str, database: str):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client[database]

    def test(self) -> bool:
        """
        A function that pings the server to check if the connection is active
        :return: A boolean value indicating the connection status
        """
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(e)
            return False
