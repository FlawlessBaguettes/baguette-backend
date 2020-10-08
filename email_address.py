from app import app, db
from datetime import date

addresses = [
    {
        'id': 1,
        'emailAddress': u'rajatgoswami.dev@gmail.com',
        'userId': 1, 
        'createdAt': date(2020, 9, 20),
        'updatedAt': date(2020, 9, 20)
    }
]

@app.route('/baguette/api/v1.0/email/<int:user_id>', methods=['GET'])
def get_email(user_id):
    address = [address for address in addresses if address['userId'] == user_id]
    if len(address) == 0:
        abort(404)
    return jsonify({'email': address[0]})

@app.route('/baguette/api/v1.0/email', methods=['POST'])
def create_email():
    if not request.json or not 'emailAddress' in request.json:
        abort(400)
    email = {
        'id': addresses[-1]['id'] + 1,
        'emailAddress': request.json['emailAddress'],
        'userId': request.json.get('userId'),
        'createdAt': date.today(),
        'updatedAt': date.today()
    }
    addresses.append(email)
    return jsonify({'email': email}), 201

@app.route('/baguette/api/v1.0/email/<int:user_id>', methods=['PUT'])
def update_email(user_id):
    address = [address for address in addresses if address['userId'] == user_id]
    if len(address) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'emailAddress' in request.json and type(request.json['emailAddress']) != unicode:
        abort(400)
    address[0]['emailAddress'] = request.json.get('emailAddress', address[0]['emailAddress'])
    address[0]['updatedAt'] = date.today()
    return jsonify({'email': address[0]})

@app.route('/baguette/api/v1.0/email/<int:email_id>', methods=['DELETE'])
def delete_email(email_id):
    address = [address for address in addresses if address['id'] == email_id]
    if len(address) == 0:
        abort(404)
    addresses.remove(address[0])
    return jsonify({'result': True})