from __main__ import app
from datetime import date

users = [
    {
        'id': 1,
        'userName': u'RajatGo',
        'password': '12345',
        'firstName': u'Rajat',
        'lastName': u'Goswami',
        'dateOfBirth': date(1994, 4, 18),
        'createdAt': date(2020, 9, 20),
        'updatedAt': date(2020, 9, 22)
    },
        {
        'id': 1,
        'userName': u'RaghavG',
        'password': 'myPass',
        'firstName': u'Raghav',
        'lastName': u'Goswami',
        'dateOfBirth': date(1994, 4, 18),
        'createdAt': date(2020, 9, 10),
        'updatedAt': date(2020, 9, 14)
    },
    {
        'id': 1,
        'userName': u'SibH',
        'password': '12345',
        'firstName': u'Sibgatul',
        'lastName': u'Husnain',
        'dateOfBirth': date(1994, 9, 15),
        'createdAt': date(2020, 8, 8),
        'updatedAt': date(2020, 8, 22)
    }
]

@app.route('/baguette/api/v1.0/users', methods=['GET'])
def get_users():
    return jsonify({'users': users})

@app.route('/baguette/api/v1.0/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = [user for user in users if user['id'] == user_id]
    if len(user) == 0:
        abort(404)
    return jsonify({'user': user[0]})

@app.route('/baguette/api/v1.0/users', methods=['POST'])
def create_user():
    if not request.json or not 'userName' in request.json:
        abort(400)
    user = {
        'id': users[-1]['id'] + 1,
        'userName': request.json['userName'],
        'firstName': request.json['firstName'],
        'lastName': request.json['lastName'],
        'dateOfBirth': date(request.json('dateOfBirth')),
        'createdAt': date.today(),
        'updatedAt': date.today()
    }
    users.append(user)
    return jsonify({'user': user}), 201

@app.route('/baguette/api/v1.0/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = [user for user in users if user['id'] == user_id]
    if len(user) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'userName' in request.json and type(request.json['userName']) is not unicode:
        abort(400)
    if 'firstName' in request.json and type(request.json['firstName']) is not unicode:
        abort(400)
    if 'lastName' in request.json and type(request.json['done']) is not unicode:
        abort(400)
    if 'dateOfBirth' in request.json and type(request.json['dateOfBirth']) is not datetime.date:
        abort(400)
    user[0]['userName'] = request.json.get('userName', user[0]['userName'])
    user[0]['firstName'] = request.json.get('firstName', user[0]['firstName'])
    user[0]['lastName'] = request.json.get('lastName', user[0]['lastName'])
    user[0]['dateOfBirth'] = request.json.get('dateOfBirth', user[0]['dateOfBirth'])
    user[0]['updatedAt'] = date.today()
    return jsonify({'user': user[0]})

@app.route('/baguette/api/v1.0/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = [user for user in users if user['id'] == user_id]
    if len(user) == 0:
        abort(404)
    users.remove(user[0])
    return jsonify({'result': True})