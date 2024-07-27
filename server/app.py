from flask import Flask, request, make_response, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# GET /messages: returns an array of all messages as JSON, ordered by created_at in ascending order.
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_list = [{'id': msg.id, 'username': msg.username, 'body': msg.body, 'created_at': msg.created_at} for msg in messages]
    return jsonify(messages_list)

# POST /messages: creates a new message with a body and username from params, and returns the newly created post as JSON.
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or 'username' not in data or 'body' not in data:
        abort(400, description="Invalid input")
    
    username = data['username']
    body = data['body']
    
    new_message = Message(username=username, body=body)
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        'id': new_message.id,
        'username': new_message.username,
        'body': new_message.body,
        'created_at': new_message.created_at
    }), 201

# PATCH /messages/<int:id>: updates the body of the message using params, and returns the updated message as JSON.
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json()
    if not data or 'body' not in data:
        abort(400, description="Invalid input")
    
    message = Message.query.get(id)
    if not message:
        abort(404, description="Message not found")
    
    message.body = data['body']
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'username': message.username,
        'body': message.body,
        'created_at': message.created_at
    })

# DELETE /messages/<int:id>: deletes the message from the database.
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        abort(404, description="Message not found")
    
    db.session.delete(message)
    db.session.commit()
    
    return '', 204

if __name__ == '__main__':
    app.run(port=5555)
