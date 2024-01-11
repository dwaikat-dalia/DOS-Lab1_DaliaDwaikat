from flask import Flask, request, jsonify,json
import requests
#dalia dwaikat
app = Flask(__name__)
FRONTEND_SERVER_URL = "http://localhost:5000"

catalog ={}
def update_catalog_item(file_path):
    with open(file_path, 'w') as file:
        # Write header
        file.write("id,title,stock,cost,topic\n")
        # Write data
        for item_number, info in catalog.items():
            file.write(f"{item_number},{info['title']},{info['stock']},{info['cost']},{info['topic']}\n")
        
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            columns = line.strip().split(',')
            item_number = int(columns[0])
            title = columns[1]
            stock = int(columns[2])
            cost = float(columns[3])
            topic = columns[4]

            catalog[item_number] = {
                'title': title,
                'stock': stock,
                'cost': cost,
                'topic': topic
            }


with open('catalog_replica.txt', 'r') as file:
    lines = file.readlines()
    for line in lines[1:]:
        columns = line.strip().split(',')
        item_number = int(columns[0])
        title = columns[1]
        stock = int(columns[2])
        cost = float(columns[3])
        topic = columns[4]

        catalog[item_number] = {
            'title': title,
            'stock': stock,
            'cost': cost,
            'topic': topic
        }
print(catalog)        

#this to get the data from replica database by id
@app.route('/query_replica/<int:item_number>', methods=['GET'])
def query(item_number):
    
    item = catalog.get(item_number)

    if item:
        return jsonify(item)
    else:
        return jsonify({'error': 'Item not found'}), 404
#to get data from replica database by the string
@app.route('/query_replica/<string:topic>', methods=['GET'])
def query_by_subject(topic):
    items = [item for item in catalog.values() if item['topic'] == topic]
    if items:
        return jsonify({'items': items})
    else:
        return jsonify({'error': 'No items found for the specified topic'}), 404

#update the data inside the replica database , (Replication)
#and will tell the cache that the value is changed ,(Caching)
#also will tell the another database server that the data is updated so the another server will update the value (Consistency)
@app.route('/update_replica/<int:item_number>', methods=['PUT'])
def update(item_number):
    item = catalog.get(item_number)
    if item:
        data = request.json
        if 'cost' in data:
            item['cost'] = data['cost']
        if 'stock' in data:
            item['stock'] = data['stock']
        print(catalog)
        update_catalog_item('catalog_replica.txt')
        #send to cache in the frontend server that the data inside it is changed to new values
        response = requests.post(f"{FRONTEND_SERVER_URL}/updateCache/{item_number}")
        if response.status_code == 200:
            print(f"[||||||| Cache now know that the data is changed |||||||]")
        else:
            print(f"!!!!!!!!Failed ,Cache not know that the data is changed !!!!!!!!")
        #tell catalog server to change the value in database file
        response = requests.put(f"http://localhost:5002/update_catFR/{item_number}", json=data)

        return jsonify({'message': f'Item {item_number} updated successfully'})
    else:
        return jsonify({'error': 'Item not found'}), 404

#this the catalog server will use it 
# to tell this replica that the values is changed
#and to update the database replica with new values
@app.route('/update_replica_Catalog/<int:item_number>', methods=['PUT'])
def updateR(item_number):
    item = catalog.get(item_number)
    if item:
        data = request.json
        if 'cost' in data:
            item['cost'] = data['cost']
        if 'stock' in data:
            item['stock'] = data['stock']
        print(catalog)
        update_catalog_item('catalog_replica.txt')
        
        return jsonify({'message': f'Item {item_number} updated successfully'})
    else:
        return jsonify({'error': 'Item not found'}), 404
    
#to get the catalog to orderServer_Replica.py    
@app.route('/get_catalog_replica', methods=['GET'])
def get_catalog():
    
    return jsonify(catalog)

if __name__ == '__main__':
    app.run(host='localhost', port=5003)