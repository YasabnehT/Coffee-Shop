from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['GET'])
def get_drinks_short():
    try:
        drinks = Drink.query.all()
        drink_short = [drink.short() for drink in drinks]
        return jsonify({'success':True, 'drinks': drink_short}, 200)
    except:
        abort(422)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail_auth():
    drinks = Drink.query.all()
    drink_detail = [drink.long() for drink in drinks]
    try:
        return jsonify({'success':True, 'drinks':drink_detail},200)
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def add_drinks_detail():
    request_body = request.get_json()
    new_drink_title = request_body['title']
    new_drink_recipe = request_body['recipe']
    if new_drink_title and new_drink_recipe not in request_body:
        abort(404)
    try:
        new_drink = Drink(title = new_drink_title, recipe = new_drink_recipe)
        new_drink.insert()
        return jsonify({'success':True, 'drinks':new_drink.long()},200)
    except:
        abort(404)
        
        
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('drinks/<id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(id):
    request_body = request.get_json()
    drink_to_be_Updated = Drink.query.get(id)
    if drink_to_be_Updated is None:
        abort(404)
    try:
        drink_to_be_Updated.title = request_body['title']
        drink_to_be_Updated.recipe = request_body['recipe']
        drink_to_be_Updated.update()
        return jsonify({'success':True, 'drinks':[drink_to_be_Updated.long()]}, 200)
    except:
        abort(422)
    

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('drinks/<id>', methods = 'DELETE')
@requires_auth('delete:drinks')
def delete_drink(id):
    request_body = request.get_json()
    drink_to_be_deleted = Drink.query.filter(Drink.id == id)
    if drink_to_be_deleted is None:
        abort(404)
    try:
        drink_to_be_deleted.delete()
        return jsonify({'success':True, 'drinks': id}, 200)
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def notfound_error(error):
    return jsonify({"success": False,"error": 404,"message": "resource not found"}), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(auth_error):
    return jsonify({"success": False,"error": auth_error.status_code,"message": auth_error.error})
