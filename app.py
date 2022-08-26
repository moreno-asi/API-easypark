
from flask import Flask, jsonify, request, Response

from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.secret_key = 'my_clave_secreta'

"""
#NOT WORK
app.config['MONGO_URI'] = 'mongodb://localhost:27017/easypark'
mongo = PyMongo(app)

"""
mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/easypark")
mongo = mongodb_client


@app.route('/users', methods=['POST'])
def create_user():
    """
    CREATE A USER WITH PARAMETER FROM REQUEST
    """
    #Check if all keys are in request.json
    if 'username' in request.json and 'email' in request.json and 'password' in request.json:
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']
        
        #For the next version check if exist a list of objects vehicles and insert them inside collection
        #vehicle = request.json['vehicle']
        #if 'vehicle' in request.json:
        #   print(request.json['vehicle'])
        #...........

        hashed_password = generate_password_hash(password)
        id = mongo.db.users.insert_one(
            {'username': username, 
            'email': email, 
            'password': hashed_password,
            'vehicle':[]
            })
        
        if id:
            response = jsonify({
                '_id': str(id),
                'username': username,
                'password': hashed_password,
                'email': email
                })
            response.status_code = 201
            return response

    return not_found()


@app.route('/users', methods=['GET'])
def get_users():
    """
    GET ALL USER OF THE COLLECTION
    """
    users = mongo.db.users.find()
    response = json_util.dumps(users)
    return Response(response, mimetype="application/json")


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    """
    GET THE USER WITH ID
    """
    #Check if 'id' is Hexadecimal
    try:
        int(id,16)
    except:
        return jsonify({'message': 'Id: ' + id + ' is not HexValue'}),404

    user = mongo.db.users.find_one({'_id': ObjectId(id), })
    if user:
        response = json_util.dumps(user)
        return Response(response, mimetype="application/json")
    #user not exist in DB
    else:
        return not_found()

@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    """
    DELETE USER BY ID OF THE COLLECTION
    """
    #Check if 'id' is Hexadecimal
    try:
        int(id,16)
    except:
        return jsonify({'message': 'Id: ' + id + ' is not HexValue'}),404

    result = mongo.db.users.delete_one({'_id': ObjectId(id)})

    #User deleted
    if result.deleted_count > 0 :
        response = jsonify({'message': 'User' + id + ' Deleted Successfully'})
        response.status_code = 200
        return response

    #Id user not found
    else:
        return not_found()

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    """
    UPDATE USER WITH ID = id
    """
    #Check if 'id' is Hexadecimal
    try:
        int(id,16)
    except:
        return jsonify({'message': 'Id: ' + id + ' is not HexValue'}),404
        #Check if all keys are in request.json
    if 'username' in request.json and 'email' in request.json and 'password' in request.json:
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']

        hashed_password = generate_password_hash(password)

        result = mongo.db.users.update_one(
            {'_id': ObjectId(id)}, {'$set': {'username': username, 'email': email, 'password': hashed_password}})

        if result.modified_count > 0:
            response = jsonify({'message': 'User' + id + 'Updated Successfuly'})
            response.status_code = 200
            return response
    
    return not_found()


@app.route('/users/<id>/vehicles', methods=['POST'])
def add_vehicle(id):
    """
    ADD A VEHICLE IN THE DOCUMENT OF THE USER
    """
    #Check if 'id' is Hexadecimal
    try:
        int(id,16)
    except:
        return jsonify({'message': 'Id: ' + id + ' is not HexValue'}),404
    
    #Check all keys of request.json 
    if 'vehicle_registration' in request.json and 'model' in request.json and 'label' in request.json:
        vregist = request.json['vehicle_registration']
        vmodel = request.json['model']
        vlabel = request.json['label']
        #Add a vehicle in document where _id is equals to id
        result = mongo.db.users.update_one({"_id": ObjectId(id)},{"$push":{"vehicle":
                                {
                                "vehicle_registration":vregist,
                                'model': vmodel,
                                'label': vlabel}
                                }})
        #Insert vehicle ok                        
        if result.modified_count > 0:
            response = jsonify({'message': vregist + ' added successfully'})
            return response

    return not_found()

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    response = jsonify(message)
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(debug=True, port=3000)
