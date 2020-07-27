import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():

    drinks_list = None

    try:
        drinks = Drink.query.all()
        drinks_list = [drink.short() for drink in drinks]
    except Exception as e:
        print(sys.exc_info())
        abort(422)

    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():

    abort_code = None
    drinks_list = None
    try:
        drinks = Drink.query.all()
        drinks_list = [drink.long() for drink in drinks]
    except Exception as e:
        print(sys.exc_info())
        abort(422)

    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks():

    drink = None
    body = request.get_json()
    if 'title' in body and 'recipe' in body:
        title = request.get_json()['title']
        recipe = request.get_json()['recipe']
    else:
        abort(400)

    try:
        d = Drink(title, json.dumps(recipe))
        d.insert()
        drink = [d.long()]
        if drink is None:
            raise Exception('unprocessable')
    except Exception as e:
        print(sys.exc_info())
        abort(422)

    return jsonify({
        'success': True,
        'drinks': drink
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id):

    abort_code, drink = None, None
    body = request.get_json()
    if 'title' not in body and 'recipe' not in body:
        abort(400)

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort_code = 404
            raise Exception('not found')

        title = body['title'] if 'title' in body else drink.title
        recipe = json.dumps(body['recipe']) if 'recipe' in body \
            else drink.recipe

        drink.title = title
        drink.recipe = recipe
        drink.update()

    except Exception as e:
        print(sys.exc_info())
        if abort_code:
            abort(404)
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):

    abort_code = None

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort_code = 404
            raise Exception('not found')

        drink.delete()

    except Exception as e:
        print(sys.exc_info())
        if abort_code:
            abort(404)
        abort(422)

    return jsonify({
        'success': True,
        'delete': id
    })


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
def bad_request(error):
    return jsonify({
        'error': 404,
        'success': False,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 400,
        'success': False,
        'message': 'bad request'
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def Auth_Error(auth_error):
    return jsonify({
        'error': auth_error.status_code,
        'success': False,
        'message': auth_error.error
    }), auth_error.status_code
