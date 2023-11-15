
from flask import Flask, jsonify,request
import requests

app = Flask(__name__)
CATALOG_SERVER_URL = "http://127.0.0.1:5002"

# Mock data for order server (you would typically use a database)
orders = {}
catalog = {}

with open('orders.txt', 'r') as file:
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



def update_order(item_number):
     orders[item_number]['sold']+=1
     update_order_item('orders.txt')
def update_order_item(file_path):
    with open(file_path, 'w') as file:
        # Write header
        file.write("id,title,sold\n")
        # Write data
        for item_number, info in orders.items():
            file.write(f"{item_number},{info['title']},{info['sold']}\n")


def update_catalog(item_number, updated_info):
    response = requests.put(f"{CATALOG_SERVER_URL}/update/{item_number}", json=updated_info)
    if response.status_code == 200:
        print(f"Catalog updated successfully for Item {item_number}")
    else:
        print(f"Failed to update catalog for Item {item_number}")

def get_catalog():
    response = requests.get(f"{CATALOG_SERVER_URL}/get_catalog")
    
    if response.status_code == 200:
        print("Data geted succesfully")
        return response.json()
    else:
        return None

catalog = get_catalog()
#print(catalog['1'])
'''
if catalog:
    print("Catalog Data:")
    for item_number, item_info in catalog.items():
        print(f"Item {item_number}: {item_info}")
else:
    print("Failed to retrieve catalog data.")
'''

# Endpoint for purchase
@app.route('/purchase/<int:item_number>', methods=['POST'])
def purchase(item_number):
    # Code to handle the purchase of an item
    # This involves querying the catalog server to verify the item is in stock
    # and decrementing the stock if available
    # ...
    #print(item_number)
    #print(catalog)
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
         
            return jsonify({'message': f'Item {item_number} purchased successfully'})
        else:
            return jsonify({'error': 'Item is out of stock'}), 400
    else:
        return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(port=5003)

'''
# order.py

import requests

CATALOG_SERVER_URL = "http://127.0.0.1:5002"

def get_catalog():
    response = requests.get(f"{CATALOG_SERVER_URL}/get_catalog")
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Example usage
catalog_data = get_catalog()

if catalog_data:
    print("Catalog Data:")
    for item_number, item_info in catalog_data.items():
        print(f"Item {item_number}: {item_info}")
else:
    print("Failed to retrieve catalog data.")
'''