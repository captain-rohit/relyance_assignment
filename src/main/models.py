from app import db,bcrypt
from flask import current_app
import jwt,datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import uuid

class User(db.Model):
    
     __tablename__ = 'users'
     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     first_name = db.Column(db.String(100), nullable= False)
     last_name = db.Column(db.String(100),nullable=True)
     email = db.Column(db.String(100),nullable=False)
     password = db.Column(db.String(255), nullable=False)
     registered_date = db.Column(db.DateTime, default=func.now(), nullable=False)
     balance = db.Column(db.FLOAT, nullable=False)
     logins = db.Column(db.Integer,nullable = False)
     # requests = relationship("Request", cascade="all, delete")
     # payments = relationship("Payment", cascade="all, delete")

     def __init__(self, email, password, first_name, last_name, credit):
          self.email = email
          self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
          self.first_name = first_name
          self.last_name = last_name
          self.balance = credit
          self.logins = 1


     def encode_auth_token(self, user_id):
        """Generates the auth token"""
        try:
             payload = {
                    # 'exp': datetime.datetime.utcnow() + datetime.timedelta(
                    #      days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                    #      seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                    # ),
                    # 'iat': datetime.datetime.utcnow(),
                    'sub': user_id
             }
             encoded = jwt.encode(
                    payload,
                    current_app.config.get('SECRET_KEY'),
                    algorithm='HS256'
             )
             return encoded
        except Exception as e:
               return e

     @staticmethod
     def decode_auth_token(auth_token):
          """
          Decodes the auth token - :param auth_token: - :return: integer|string
          """
          try:
               payload = jwt.decode(
                    auth_token, current_app.config.get('SECRET_KEY'), algorithms="HS256")
               return payload['sub']
          except jwt.ExpiredSignatureError:
               return 'Signature expired. Please log in again.'
          except jwt.InvalidTokenError:
               return 'Invalid token. Please log in again.'


class Payment(db.Model):
     __tablename__ = 'payments_data'
     transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     user_from = db.Column(db.Integer, db.ForeignKey('users.id'))
     user_to = db.Column(db.Integer, db.ForeignKey('users.id'))
     amount = db.Column(db.FLOAT, nullable=False)
     paid_on = db.Column(db.DateTime, default=func.now(), nullable=False)
     received_from = relationship("User", foreign_keys='Payment.user_from')
     paid_to = relationship("User", foreign_keys='Payment.user_to')

     def __init__(self,user_from,user_to,amount):
          self.user_from = user_from
          self.user_to = user_to
          self.amount = amount


class Request(db.Model):
     __tablename__ = 'owing_data'
     ticket_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
     amount = db.Column(db.FLOAT,nullable = False)
     user_from = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
     user_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
     made_on = db.Column(db.DateTime, default=func.now(), nullable=False)
     owes_from = relationship("User", foreign_keys='Request.user_from')
     owes_to = relationship("User", foreign_keys='Request.user_to')


     def __init__(self,user_from,user_to,amount):
          self.user_from = user_from
          self.user_to = user_to
          self.amount = amount
