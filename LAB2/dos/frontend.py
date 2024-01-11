
from flask import Flask, jsonify, request
import requests
from cachetools import LRUCache
import time

app = Flask(__name__)

# replicas for each server 
#catalog : normal server with post 5002 , replica :5003
catalog_server_url = ["http://localhost:5002", "http://localhost:5003"]
#order server : normal port :5004 , replica :5005
order_server_url = ["http://localhost:5004", "http://localhost:5005"]

# In-memory cache using LRU (Least Recently Used) 
# to store the responsed for each requist 
cache = LRUCache(maxsize=1000)

# List of backend replicas for catalog server 
backend_replicas = [catalog_server_url[0], catalog_server_url[1]]

# List of backend replicas for order server 
backend_replicas_order = [order_server_url[0], order_server_url[1]]
# replication for catalog Server
rCatalog_index = 0  # Round-robin index

#roound robin algorithm for catalog server , to choose between normal and replica
def round_robin():
    global rCatalog_index
    rCatalog_index = (rCatalog_index + 1) % len(backend_replicas)
    print(f"(((((((((((((((((((((catalog number {backend_replicas[rCatalog_index]}))))))))))))))))))))))")
    return backend_replicas[rCatalog_index]

# replication for order server
oOrder_index = 0  # Round-robin index

def round_robin_order():
    global oOrder_index
    oOrder_index = (oOrder_index + 1) % len(backend_replicas_order)
    print(f"{{{{{{{{order number {backend_replicas_order[oOrder_index]}}}}}}}}}")
    return backend_replicas_order[oOrder_index]

#to add element in the cache 
def add_to_cache(key, value):
    cache[key] = value
    for k, v in cache.items():
        print(f"Key: '{k}', Data: {v}")

#check the element in the cache or not 
def cache_hit(key):

#this list to add the keys that data updated 
#to get the new values from original database
    keys_to_delete = []

    for k, v in cache.items():
        if k == key:
            value = v

            if value is not None:
#here if the data is changed ,
# so when the data chnaged the value for it will changed  in cache "Item purchased successfully"
                if value == '{"message": "Item purchased successfully"}':
                    keys_to_delete.append(k)

    # Delete keys outside the loop to avoid modifying the dictionary during iteration
    for k in keys_to_delete:
        #delete the uncorrect data 
        del cache[k]

    for k in keys_to_delete:
        backend_server = round_robin()
        #to get the new values from database file 
        if backend_server == "http://localhost:5002":
            response = requests.get(f"{backend_server}/query/{k}")
        else:
            response = requests.get(f"{backend_server}/query_replica/{k}")
        
        # Update cache with the result, add the updated values
        add_to_cache(k, response.json())
    return cache.get(key, None)

# to print elements inside the cache 
def print_cache():
    for key, value in cache.items():
        print(f"Key: '{key}', Data: {value}")

#this to update the cache , the catalog server when changed the values 
        #catalog server will tell the cache that the values is changed , so it has a incorrect values and it must changed 
@app.route('/updateCache/<int:key>', methods=['POST'])
def update_cache(key):
    for keyy, value in cache.items():
        if keyy == key:
            
            # Update the existing value in the cache
            #so when there is a new requist to get these data 
            # the cache will know that the data is changed and it is incorrect values 
            cache[key] = '{"message": "Item purchased successfully"}'
    return jsonify({"message": "Done tell cached"}), 200


@app.route('/search/<int:topic>', methods=['GET'])
def search(topic):
    # Measure response time for cache hit
    if topic in cache:
        start_time = time.time()
        cache_hit(topic)
        end_time = time.time()
        response_time = end_time - start_time
        #print the time 
        print(f"Search : Response time for cache hit (item in cache): {response_time} seconds")
        return jsonify(cache_hit(topic))
    else:
        # Measure response time for cache miss
        start_time = time.time()
        backend_server = round_robin()
        # response = requests.get(f"{backend_server}/query/{topic}")
        if backend_server == "http://localhost:5002":
            response = requests.get(f"{backend_server}/query/{topic}")
        else:
            response = requests.get(f"{backend_server}/query_replica/{topic}")
        end_time = time.time()
        response_time = end_time - start_time
        print(f"Search : Response time for cache miss(if not in cache): {response_time} seconds")

        # Update cache with the result
        #if the element is not in the cache 
        add_to_cache(topic, response.json())

        return jsonify(response.json())


@app.route('/info/<int:item_number>', methods=['GET'])
def info(item_number):
    # Measure response time for cache hit
    if item_number in cache:
        start_time = time.time()
        response_data = cache_hit(item_number)
        end_time = time.time()
        response_time = end_time - start_time
        print(f"Info : Response time for cache hit(in cache ): {response_time} seconds")
        return jsonify(response_data)

    # Measure response time for cache miss
    start_time = time.time()
    backend_server = round_robin()
    if backend_server == "http://localhost:5002":
        response = requests.get(f"{backend_server}/query/{item_number}")
    else:
        response = requests.get(f"{backend_server}/query_replica/{item_number}")
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Info : Response time for cache miss(not in cache): {response_time} seconds")

    # Update cache with the result
    add_to_cache(item_number, response.json())

    return jsonify(response.json())


@app.route('/purchase/<int:item_number>', methods=['POST'])
def purchase(item_number):
    # Measure response time for cache hit
    backend_server_order = round_robin_order()
    start_time = time.time()
    if backend_server_order == "http://localhost:5004":
        purchase_response = requests.post(f"{backend_server_order}/purchase/{item_number}")
    else:
        purchase_response = requests.post(f"{backend_server_order}/purchase_replica/{item_number}")
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Purchase : Response time for Purchase element  {response_time} seconds")

    print_cache()  # Print cache data
    return jsonify(purchase_response.json())

if __name__ == '__main__':
    app.run(port=5000)



"""


from flask import Flask, jsonify, request
import requests
from cachetools import LRUCache
import time

app = Flask(__name__)
#this is the two different servers for catalog and order 
catalog_server_url = ["http://localhost:5002", "http://localhost:5003"]
order_server_url = ["http://localhost:5004", "http://localhost:5005"]

# In-memory cache using LRU (Least Recently Used) eviction policy
cache = LRUCache(maxsize=1000)

# List of backend replicas
backend_replicas = [catalog_server_url[0], catalog_server_url[1]]
backend_replicas_order = [order_server_url[0], order_server_url[1]]
# replication for catalog Server
rr_index = 0  # Round-robin index

def round_robin():
    global rr_index
    rr_index = (rr_index + 1) % len(backend_replicas)
    print(f"(((((((((((((((((((((catalog number {backend_replicas[rr_index]}))))))))))))))))))))))")
    return backend_replicas[rr_index]

# replication for order server
oo_index = 0  # Round-robin index

def round_robin_order():
    global oo_index
    oo_index = (oo_index + 1) % len(backend_replicas_order)
    print(f"{{{{{{{{order number {backend_replicas_order[oo_index]}}}}}}}}}")
    return backend_replicas_order[oo_index]

def add_to_cache(key, value):
    #print("ADD TO CACHE_______________________________________________________")
    cache[key] = value
    #print(f"Added to cache - Key: '{key}', Data: {value}")
    #print("Current Cache Data:")
    for k, v in cache.items():
        print(f"Key: '{k}', Data: {v}")
    #print("Done ADD TO CACHE_____________________________________________________")


def cache_hit(key):
    #print(f"Cache hit for key '{key}': {cache[key]}")
    keys_to_delete = []

    for k, v in cache.items():
        if k == key:
            #print("YES EQUALED********************")
            value = v

            if value is not None:
                #print(f"Cache hit for key '{key}': {value}")

                # Check if the value matches a specific message
                if value == '{"message": "Item purchased successfully"}':
                    #print(f"Cache value matches specific message for key '{key}'")
                    keys_to_delete.append(k)

    # Delete keys outside the loop to avoid modifying the dictionary during iteration
    for k in keys_to_delete:
        del cache[k]

    for k in keys_to_delete:
        backend_server = round_robin()

        # Measure response time for cache miss
        start_time = time.time()
        # Forward the request to the selected backend replica
        #response = requests.get(f"{backend_server}/query/{k}")

        if backend_server == "http://localhost:5002":
            response = requests.get(f"{backend_server}/query/{k}")
        else :
            response = requests.get(f"{backend_server}/query_replica/{k}")
        end_time = time.time()

        # Update cache with the result
        add_to_cache(k, response.json())

        # Measure response time
        response_time = end_time - start_time
        #print(f"Response time for cache miss: {response_time} seconds")

    #print_cache()
    #print("Done hit ********************************************")
    return cache.get(key, None)


def print_cache():
    #print("Current Cache Data:")
    for key, value in cache.items():
        print(f"Key: '{key}', Data: {value}")


@app.route('/updateCache/<int:key>', methods=['POST'])
def update_cache(key):
    #print("Start Update---------------------------------")
    for keyy, value in cache.items():
        #print(f"Key: '{keyy}', Data: {value}")
        if keyy == key:
            # Update the existing value in the cache
            cache[key] = '{"message": "Item purchased successfully"}'
            #print(f"Updated cache - Key: '{key}', New Data: message: Item purchased successfully")
    #print_cache()
    #print("Done Update---------------------------------")
    return jsonify({"message":"Done tell cached"}),200


@app.route('/search/<int:topic>', methods=['GET'])
def search(topic):
    # Measure response time for cache hit
    if topic in cache:
        start_time = time.time()
        #print_cache()  # Print cache data
        cache_hit(topic)
        end_time = time.time()
        response_time = end_time - start_time
        #print(f"Response time for cache hit: {response_time} seconds")
        return jsonify(cache_hit(topic))

    # Measure response time for cache miss
    start_time = time.time()
    backend_server = round_robin()
    #response = requests.get(f"{backend_server}/query/{topic}")
    if backend_server == "http://localhost:5002":
        response = requests.get(f"{backend_server}/query/{topic}")
    else :
        response = requests.get(f"{backend_server}/query_replica/{topic}")
    end_time = time.time()
    response_time = end_time - start_time
    #print(f"Response time for cache miss: {response_time} seconds")

    # Update cache with the result
    add_to_cache(topic, response.json())

    #print_cache()  # Print cache data

    return jsonify(response.json())

@app.route('/info/<int:item_number>', methods=['GET'])
def info(item_number):
    # Measure response time for cache hit
    if item_number in cache:
        start_time = time.time()
        return jsonify(cache_hit(item_number))
        end_time = time.time()
        response_time = end_time - start_time
        print(f"Response time for cache hit: {response_time} seconds")

    # Measure response time for cache miss
    start_time = time.time()
    backend_server = round_robin()
    #response = requests.get(f"{backend_server}/query/{item_number}")
    if backend_server == "http://localhost:5002":
        response = requests.get(f"{backend_server}/query/{item_number}")
    else :
        response = requests.get(f"{backend_server}/query_replica/{item_number}")
    end_time = time.time()
    response_time = end_time - start_time
    #print(f"Response time for cache miss: {response_time} seconds")

    # Update cache with the result
    add_to_cache(item_number, response.json())
    #print_cache()  # Print cache data

    return jsonify(response.json())

@app.route('/purchase/<int:item_number>', methods=['POST'])
def purchase(item_number):
    # Measure response time for cache hit
    backend_server_order = round_robin_order()
 #   purchase_response = requests.post(f"{backend_server_order}/purchase/{item_number}")

    #if purchase_response.status_code == 200:
    start_time = time.time()
    #purchase_response = requests.post(f"{backend_server_order}/purchase/{item_number}")
    if backend_server_order == "http://localhost:5004":
        print("Order")
        purchase_response = requests.post(f"{backend_server_order}/purchase/{item_number}")
    else:
        print("Replica")
        purchase_response = requests.post(f"{backend_server_order}/purchase_replica/{item_number}")
        # Update the cache with the new value
        #update_cache(item_number, purchase_response.json())
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Response time for cache hit: {response_time} seconds")
        
    print_cache()  # Print cache data

    return jsonify(purchase_response.json())
#else:
    #return jsonify(purchase_response.json()), 404

if __name__ == '__main__':
    app.run(port=5000)

"""