from __main__ import app
from datetime import date

content_uploads = [
    {
        'id': 1,
        'contentUrl': u'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'createdAt': date(2020, 9, 26),
        'updatedAtAt': date(2020, 9, 27)
    }
]

@app.route('/baguette/api/v1.0/content/<int:content_id>', methods=['GET'])
def get_content(content_id):
    content = [content for content in content_uploads if content_uploads['id'] == content_id]
    if len(content) == 0:
        abort(404)
    return jsonify({'content': content[0]})

@app.route('/baguette/api/v1.0/content', methods=['POST'])
def create_content():
    if not request.json or not 'contentUrl' in request.json:
        abort(400)
    content = {
        'id': users[-1]['id'] + 1,
        'contentUrl': request.json['contentUrl'],
        'createdAt': date.today(),
        'updatedAt': date.today()
    }
    content_uploads.append(content)
    return jsonify({'content': content_uploads}), 201

@app.route('/baguette/api/v1.0/content/<int:content_id>', methods=['PUT'])
def update_content(content_id):
    content = [content for content in content_uploads if content['id'] == content_id]
    if len(content) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'contentUrl' in request.json and type(request.json['contentUrl']) is not unicode:
        abort(400)
    content[0]['contentUrl'] = request.json.get('contentUrl', content[0]['contentUrl'])
    content[0]['updatedAt'] = date.today()
    return jsonify({'content': content[0]})

@app.route('/baguette/api/v1.0/content/<int:content_id>', methods=['DELETE'])
def delete_content(content_id):
    content = [content for content in content_uploads if content['id'] == content_id]
    if len(content) == 0:
        abort(404)
    content_uploads.remove(content[0])
    return jsonify({'result': True})