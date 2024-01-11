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


with open('catalog.txt', 'r') as file:
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

#to get the data from database file by id 
@app.route('/query/<int:item_number>', methods=['GET'])
def query(item_number):
    item = catalog.get(item_number)

    if item:
        return jsonify(item)
    else:
        return jsonify({'error': 'Item not found'}), 404
    
#to get the data from database file by string
@app.route('/query/<string:topic>', methods=['GET'])
def query_by_subject(topic):
    items = [item for item in catalog.values() if item['topic'] == topic]

    if items:
        return jsonify({'items': items})
    else:
        return jsonify({'error': 'No items found for the specified topic'}), 404

#to update the database file , 
    #will tell to the cache that values is changed 
    #also will tell the catalog replica that the value is updated 
@app.route('/update/<int:item_number>', methods=['PUT'])
def update(item_number):
    item = catalog.get(item_number)

    if item:
        data = request.json
        if 'cost' in data:
            item['cost'] = data['cost']
        if 'stock' in data:
            item['stock'] = data['stock']
        print(catalog)
        update_catalog_item('catalog.txt')
        #tell cache 
        response = requests.post(f"{FRONTEND_SERVER_URL}/updateCache/{item_number}")
        if response.status_code == 200:
            print(f"[||||||| Cache now know that the data is changed |||||||]")
        else:
            print(f"!!!!!!!!Failed ,Cache not know that the data is changed !!!!!!!!")
        #tell replica to change the values inside the database replica
        response = requests.put(f"http://localhost:5003/update_replica_Catalog/{item_number}", json=data)

        if response.status_code == 200:
            print(f"Catalog replica  updated successfully for Item {item_number}")
        else:
            print(f"Failed to update catalog replica for Item {item_number}")

        return jsonify({'message': f'For catalog Item {item_number} updated successfully'})
    else:
        return jsonify({'error': 'Item not found'}), 404

#this catalog server replica will use it to tell this catlog server to changed his database file 
@app.route('/update_catFR/<int:item_number>', methods=['PUT'])
def updateC(item_number):
    item = catalog.get(item_number)

    if item:
        data = request.json
        if 'cost' in data:
            item['cost'] = data['cost']
        if 'stock' in data:
            item['stock'] = data['stock']
        print(catalog)
        update_catalog_item('catalog.txt')

        return jsonify({'message': f'For catalog Item {item_number} updated successfully'})
    else:
        return jsonify({'error': 'Item not found'}), 404
    
#to get the catalog to orderServer.py    
@app.route('/get_catalog', methods=['GET'])
def get_catalog():
    
    return jsonify(catalog)

if __name__ == '__main__':
    app.run(host='localhost', port=5002)