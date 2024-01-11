from flask import Flask, request, jsonify,json
#dalia dwaikat
app = Flask(__name__)
catalog ={}
def update_catalog_item(file_path):
    with open(file_path, 'w') as file:
        # Write header
        file.write("id,title,stock,cost,topic\n")
        # Write data
        for item_number, info in catalog.items():
            file.write(f"{item_number},{info['title']},{info['stock']},{info['cost']},{info['topic']}\n")

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

@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message':'Hello Catalog Server'})
   
@app.route('/query/<int:item_number>', methods=['GET'])
def query(item_number):
    # Code to handle query-by-item
    # This involves returning details for a specific item
    item = catalog.get(item_number)

    if item:
        return jsonify(item)
    else:
        return jsonify({'error': 'Item not found'}), 404

@app.route('/query/<string:topic>', methods=['GET'])
def query_by_subject(topic):
    # Code to handle query-by-subject
    # This involves returning all matching entries for a specific topic
    items = [item for item in catalog.values() if item['topic'] == topic]

    if items:
        return jsonify({'items': items})
    else:
        return jsonify({'error': 'No items found for the specified topic'}), 404

@app.route('/update/<int:item_number>', methods=['PUT'])
def update(item_number):
    # Code to handle updating the cost or stock of an item
    # This involves modifying the catalog data
    item = catalog.get(item_number)

    if item:
        data = request.json
        if 'cost' in data:
            item['cost'] = data['cost']
        if 'stock' in data:
            item['stock'] = data['stock']
        print(catalog)
        update_catalog_item('catalog.txt')
        return jsonify({'message': f'Item {item_number} updated successfully'})
    else:
        return jsonify({'error': 'Item not found'}), 404
    
#to get the catalog to orderServer.py    
@app.route('/get_catalog', methods=['GET'])
def get_catalog():
    return jsonify(catalog)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)