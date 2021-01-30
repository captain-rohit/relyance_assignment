
from flask import Blueprint, request, make_response, jsonify, current_app
from sqlalchemy import exc, or_
from flask_restful import Api, Resource
from db_utils import DbConnection
from .models import *
from app import bcrypt,db
from .utils import *
from .queries import *
import psycopg2

import os, json, requests, hmac, hashlib, base64

conn = DbConnection.get_db_connection_instance()

users_blueprint = Blueprint('user', __name__)


@users_blueprint.route('/user/register', methods=['POST'])
def register_user():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    
    email = post_data.get('email')
    password = post_data.get('password')
    fname = post_data.get('first_name')
    lname = post_data.get('last_name')
    credit = float(post_data.get('amount'))
    
    try:
        # check for existing user
        user = User.query.filter(
            or_(User.email == email)).first()
        if not user:
            # add new user to db
            new_user = User(
                email=email,
                password=password,
                first_name = fname, 
                last_name = lname,
                credit=credit
            )
            db.session.add(new_user)
            db.session.commit()
            # generate auth token
            auth_token = new_user.encode_auth_token(new_user.id)
            response_object['status'] = 'success'
            response_object['message'] = 'Successfully registered and logged in.'
            response_object['auth_token'] = auth_token
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That user already exists.'
            return jsonify(response_object), 406
    # handler errors
    except (exc.IntegrityError, ValueError):
        db.session.rollback()
        return jsonify(response_object), 400

@users_blueprint.route('/user/login',methods=['POST'])
def login_user():
    # get post data
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        # fetch the user data
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                response_object['status'] = 'success'
                response_object['message'] = 'Successfully logged in.'
                response_object['auth_token'] = auth_token
                user.logins += 1
                db.session.commit()
                return jsonify(response_object), 200
        else:
            response_object['message'] = 'Invalid Credentials'
            return jsonify(response_object), 404
    except Exception:
        response_object['message'] = 'Try again.'
        return jsonify(response_object), 500
    
@users_blueprint.route('/user/logout', methods=['GET'])
@authenticate
def logout_user(resp):
    try:        
        user = User.query.filter_by(id=resp).first()
        user.logins = max(0,user.logins-1) 
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Successfully logged out.'
        }
        return jsonify(response_object), 200
    except:
        pass


@users_blueprint.route('/user/profile', methods=['GET'])
@authenticate
def user_profile(resp):
    response = {
        'status' : 'success',
        'first_name' : None,
        'last_name' : None,
        'email' : None,
        'balance' : None,

    }
    try:
        user = User.query.filter_by(id=resp).first()
        response['first_name'] = user.first_name
        response['last_name'] = user.last_name
        response['email'] = user.email
        response['balance'] = user.balance
        return jsonify(response), 200

    except Exception:
        return jsonify({'message':'Try again'}), 500

@users_blueprint.route('/user/all_transactions', methods=['GET'])
@authenticate
def transactions(resp):
    response = {
        'status' : 'failed',
        'data' : 'No data'
    }
    cur = conn.cursor()
    try:
        user = User.query.filter_by(id=resp).first()
        
        query = fetch_transaction_to_query.format(user.id)
        # print(query)
        cur.execute(query)
        paid_to = cur.fetchall()

        query = fetch_transaction_from_query.format(user.id)
        cur.execute(query)
        received_from = cur.fetchall()
        response['status'] = 'success'
        response['data'] = {}
        received_from2 = list()
        paid_to2 = list()
        # if received
        for r in received_from:
            received_from2.append(
                {
                    "transaction_id" : r[0],
                    "credit_from" : r[1],
                    "amount" : r[2],
                    "on" : r[3]
                }
            )
        for r in paid_to:
            paid_to2.append(
                {
                    "transaction_id" : r[0],
                    "paid_to" : r[1],
                    "amount" : r[2],
                    "on" : r[3]
                }
            )
        response['data']['credit'] = received_from2
        response['data']['debit'] = paid_to2
        response['data']['count'] = len(received_from) + len(paid_to)
        response['data']['balance'] = user.balance
        return jsonify(response), 200
    except psycopg2.DatabaseError as e:
        return jsonify(response), 404


@users_blueprint.route('/user/owes', methods=['GET'])
@authenticate
def owes(resp):
    response = {
        'status' : 'failed',
        'data' : 'No data'
    }
    cur = conn.cursor()
    try:
        user = User.query.filter_by(id=resp).first()
        query = fetch_owe_from.format(user.id)
        cur.execute(query)
        credit = cur.fetchall()

        query = fetch_owe_to.format(user.id)
        cur.execute(query)
        debit = cur.fetchall()
        credit2 = list()
        debit2 = list()
        for r in debit:
            debit2.append(
                {
                    "ticket_id" : r[0],
                    "requested_by" : r[1],
                    "amount" : r[2],
                    "on" : r[3]
                }
            )

        for r in credit:
            credit2.append(
                {
                    "ticket_id" : r[0],
                    "requested_to" : r[1],
                    "amount" : r[2],
                    "on" : r[3]
                }
            )
        response['data'] = {}
        response['status'] = 'success'
        response['data']['debt'] = debit2
        response['data']['owes_to'] = credit2
        return jsonify(response), 200
    except Exception as e:
        print(e)
        return jsonify(response), 404

banking_blueprint = Blueprint('banking', __name__)

@banking_blueprint.route('/banking/pay', methods=['POST'])
@authenticate
def pay(resp):
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400

    try:
        amount = float(post_data.get('amount'))
        to_user = post_data.get('to')
        password = post_data.get('password')
        curr = User.query.filter_by(id=resp).first()
        if amount>curr.balance:
            response_object['message'] = 'Insufficient Balance'
            return jsonify(response_object), 416

        if curr and bcrypt.check_password_hash(curr.password, password):
            curr.balance -= amount
            user_to = User.query.filter_by(email=to_user).first()
            if not user_to or user_to == curr:
                response_object['message'] = 'Receipient not found'
                return jsonify(response_object), 400

            user_to.balance += amount
            new_payment = Payment(user_from = curr.id,user_to=user_to.id,amount=amount)
            db.session.add(new_payment)
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Payment accepted'
            return jsonify(response_object), 202

        else:
            response_object['message'] = 'failed to authorize'
            return jsonify(response_object), 401

    except Exception as e:
        db.session.rollback()
        response_object['status'] = 'fail'
        response_object['message'] = 'Transaction error'
        return jsonify(response_object), 402


@banking_blueprint.route('/banking/ticket', methods=['POST'])
@authenticate
def make_request(resp):
    request_data = request.get_json()
    response = {
        'status': 'fail',
        'message': 'Invalid request'
    }
    if not request_data:
        return jsonify(response), 400

    try:
        req_to = request_data['to']
        amount = float(request_data['amount'])
        curr_user = User.query.filter_by(id=resp).first()
        req_user = User.query.filter_by(email = req_to).first()
        if not req_user:
            response['message'] = 'Recipient not found'
            return jsonify(response), 404
        if req_user.id == curr_user.id or amount<=float(0):
            response['message'] = "Please make a valid request"
            return jsonify(response), 403

        ticket = Request(user_from=curr_user.id,user_to=req_user.id,amount=amount)
        db.session.add(ticket)
        db.session.commit()
        response['status'] = 'success'
        response['message'] = 'Request made successfully'
        return jsonify(response), 201
    except:
        db.session.rollback()
        response['status'] = 'fail'
        response['message'] = 'Request error'
        return jsonify(response), 402
        
@banking_blueprint.route('/banking/fulfill', methods=['POST'])
@authenticate
def fulfill_ticket(resp):
    post_data = request.get_json()
    response = {
        'status': 'fail',
        'message': 'Invalid request'
    }
    if not post_data:
        return jsonify(response), 400
    try:    
        auth_header = request.headers
        ticket_id = post_data.get('id')
        password = post_data.get('password')
        ticket = Request.query.filter_by(ticket_id=ticket_id).first()
        email = User.query.filter_by(id=ticket.user_from).first()
        if not ticket:
            response['message'] = 'Request not found'
            return jsonify(response), 404
        body = json.dumps({
            'amount' : ticket.amount,
            'to' : email.email,
            'password' : password
        })
        pay_req = requests.post("http://127.0.0.1:5000/banking/pay", headers = auth_header, data= body)
        if not pay_req.status_code == 202:
            return pay_req.json(), pay_req.status_code
        Request.query.filter_by(ticket_id=ticket_id).delete()
        db.session.commit()
        response['status'] = 'success'
        response['message'] = 'request fulfilled'
        return jsonify(response), 200
    except:
        response['status'] = 'fail'
        response['message'] = 'Transaction error'
        return jsonify(response), 402
        
@banking_blueprint.route('/banking/credit',methods = ['POST'])
@authenticate
def make_credit(resp):
    post_data = request.get_json()
    response = {
        'status' : 'failed',
        'message' : 'Invalid payload'
    }
    try:    
        amount = float(post_data.get('amount'))
        password = post_data.get('password')
        print(amount, password)
    except:
        return jsonify(response), 400
    try:
        user = User.query.filter_by(id=resp).first()
        if bcrypt.check_password_hash(user.password, password):
            user.balance += amount
            db.session.commit()
            response['status'] = 'success'
            response['message'] = 'Credit done'
            return jsonify(response), 200
        else:
            response['message'] = 'Invalid credentials'
            return jsonify(response), 401
    except Exception as e:
        print(e)
        return jsonify(response), 403
