import pymongo
from django.conf import settings

class MongoDBClient:
    def __init__(self):
        # Correct connection string format for Back4App
        connection_string = (
            "mongodb://K6lQVSqx3B7BU5ePJ1SvdhtXQN7h8S9OMEdOOuNj:"
            "cLxvBXdulLXGklKbBi9Lbhj6Q07CXvVDskWFTZ8K@"
            "mongodb.back4app.com:27017/"
            "africa_disease_surveillance?authSource=admin&ssl=false"
        )
        
        try:
            self.client = pymongo.MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                retryWrites=True
            )
            # Test the connection
            self.client.admin.command('ismaster')
            self.db = self.client['africa_disease_surveillance']
            print("MongoDB connection successful")
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"MongoDB connection failed: {e}")
            raise
        except pymongo.errors.OperationFailure as e:
            print(f"MongoDB authentication failed: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        return self.db[collection_name]
    
    def close_connection(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()

# Create a global instance
mongo_client = MongoDBClient()