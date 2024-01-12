
from flask import Flask, jsonify,request
import requests

app = Flask(__name__)
# replication for catalog Server
catalog_server_url = ["http://localhost:5002", "http://localhost:5003"]
backend_replicas = [catalog_server_url[0], catalog_server_url[1]]
# replication for catalog Server
rCat_index = 0  # Round-robin Algorthim

def round_robin():
    global rCat_index
    rCat_index = (rCat_index + 1) % len(backend_replicas)
    print(f"(((((((((((((((((((((catalog number {backend_replicas[rCat_index]}))))))))))))))))))))))")
    return backend_replicas[rCat_index]

# lists to
orders = {}
catalog = {}

with open('orders_replica.txt', 'r') as file:
    lines = file.readlines()
    for line in lines[1:]:
        columns = line.strip().split(',')
        item_number = int(columns[0])
        title = columns[1]
        sold = int(columns[2])
       
        orders[item_number] = {
            'title': title,
            'sold': sold,
          
        }
print(orders) 


@app.route('/Updateorder_replica_RE/<int:item_number>', methods=['GET'])
def update_orderRR(item_number):
     orders[item_number]['sold']+=1
     update_order_item('orders_replica.txt')


@app.route('/Updateorder_replica/<int:item_number>', methods=['GET'])
def update_order(item_number):
     orders[item_number]['sold']+=1
     
     response = requests.get(f"http://localhost:5004/UpdateorderFORORDER/{item_number}")

#    response = requests.put(f"{CATALOG_SERVER_URL}/update/{item_number}", json=updated_info)
     if response.status_code == 200:
            print(f"ORDER   updated successfully for Item {item_number}")
     else:
            print(f"Failed to update ORDER  for Item {item_number}")
     update_order_item('orders_replica.txt')

def update_order_item(file_path):
    with open(file_path, 'w') as file:
        # Write header
        file.write("id,title,sold\n")
        # Write data
        for item_number, info in orders.items():
            file.write(f"{item_number},{info['title']},{info['sold']}\n")
       


def update_catalog(item_number, updated_info):
    backend_server = round_robin()
    if backend_server=="http://localhost:5002":
        print("Catalog")
        response = requests.put(f"{backend_server}/update/{item_number}", json=updated_info)
    else:
        print("Replica Catalog")
        response = requests.put(f"{backend_server}/update_replica/{item_number}", json=updated_info)

#    response = requests.put(f"{CATALOG_SERVER_URL}/update/{item_number}", json=updated_info)
    if response.status_code == 200:
        print(f"Catalog updated successfully for Item {item_number}")
    else:
        print(f"Failed to update catalog for Item {item_number}")

def get_catalog():
    backend_server = round_robin()
    if backend_server=="http://localhost:5002":
        response = requests.get(f"{backend_server}/get_catalog")
    else:
        response = requests.get(f"{backend_server}/get_catalog_replica")

    if response.status_code == 200:
        print("Data geted succesfully")
        print(response.json())
        return response.json()
    else:
        return None

catalog = get_catalog()
#print(catalog['1'])
@app.route('/', methods=['GET'])
def heelo():
    return jsonify({'message': 'Hello Order Server!'}) 
# Endpoint for purchase
@app.route('/purchase_replica/<int:item_number>', methods=['POST'])
def purchase(item_number):
    # Code to handle the purchase of an item
    # This involves querying the catalog server to verify the item is in stock
    # and decrementing the stock if available
    # ...
    #print(item_number)
    #print(catalog)
    catalog = get_catalog()
    item = catalog[str(item_number)]

    if item is not None:
        
        #item = catalog[item_number]
        if item['stock'] > 0:
            item['stock'] -= 1
            update_order(item_number)
            
            print(orders)
            #orders.append(item)
            updated_info = {"stock":item['stock'] }  # Update stock to 1 after purchase
            update_catalog(item_number, updated_info)
         
            return jsonify({'message': f'Item purchased successfully'})
        else:
            return jsonify({'error': 'Item is out of stock'}), 400
    else:
        return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=5005)