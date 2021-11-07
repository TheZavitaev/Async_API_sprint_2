import os
import time

from elasticsearch import Elasticsearch

timeout = time.time() + 60 * 5  # 5 minutes from now
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))
es = Elasticsearch(hosts=[f"{ELASTIC_HOST}:{ELASTIC_PORT}"])

while not es.ping():
    print("ELASTIC not ready")
    time.sleep(10)
    if time.time() > timeout:
        break
