from __main__ import app
from datetime import date

posts = [
    {
        'id': 1,
        'parentId': 1,
        'contentId': 1, 
        'userId': 1,
        'createdAt': date(2020, 9, 25),
        'updatedAt': date(2020, 9, 25)
    }
]

@app.route('/baguette/api/v1.0/posts', methods=['GET'])
def get_posts():
    return jsonify({'posts': posts})

@app.route('/baguette/api/v1.0/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = [post for post in posts if post['id'] == post_id]
    if len(user) == 0:
        abort(404)
    return jsonify({'post': post[0]})

@app.route('/baguette/api/v1.0/posts', methods=['POST'])
def create_posts():
    if not request.json or not 'contentId' in request.json:
        abort(400)
    post = {
        'id': users[-1]['id'] + 1,
        'parentId': request.json['parentId'],
        'contentId': request.json['contentId'],
        'userId': request.json['userId'],
        'createdAt': date.today(),
        'updatedAt': date.today()
    }
    posts.append(post)
    return jsonify({'post': post}), 201

@app.route('/baguette/api/v1.0/post/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = [post for post in posts if post['id'] == post_id]
    if len(post) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'contentId' in request.json and type(request.json['contentId']) is not int:
        abort(400)
    post[0]['contentId'] = request.json.get('contentId', post[0]['contentId'])
    post[0]['updatedAt'] = date.today()
    return jsonify({'post': post[0]})

@app.route('/baguette/api/v1.0/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = [post for post in posts if post['id'] == post_id]
    if len(post) == 0:
        abort(404)
    posts.remove(post[0])
    return jsonify({'result': True})