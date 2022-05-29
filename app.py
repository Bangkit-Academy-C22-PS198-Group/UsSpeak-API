
from functools import wraps
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

import jwt
import datetime
import json

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

PASSWORD = "password123"
PUBLIC_IP_ADDRESS = "34.101.82.176"
DBNAME = "proto1"
PROJECT_ID ="capstone-prototype1"
INSTANCE_NAME ="database-proto1"

# Database Configuration
# filename = os.path.dirname(os.path.abspath(__file__))
# database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
# app.config['SQLALCHEMY_DATABASE_URI'] = database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/database_1'
app.config["SQLALCHEMY_DATABASE_URI"]= "mysql://root:password123@35.184.77.215/test1?unix_socket=/cloudsql/Testing-project:database1"
app.config["SECRET_KEY"] = "secretkey"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


class AuthModel(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))
    picture = db.Column(db.LargeBinary((2**32)-1))

class AudioModel(db.Model):
    email_auth = db.Column(db.String(50))
    filename = db.Column(db.String(100), primary_key=True)
    emotion = db.Column(db.String(50))
    date = db.Column(db.Date)
    duration = db.Column(db.Time)
    data = db.Column(db.LargeBinary((2**32)-1))

# db.create_all()

# decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return make_response(jsonify({'message': 'Token Missing'}), 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = AuthModel.query.filter_by(email = data['email']).first()
            if current_user:
                current_email = data['email']
            else:
                return make_response(jsonify({'message' : 'wrong email token'}), 401)
        except:
            return make_response(jsonify({'message' : 'Wrong Token'}), 401)

        return f(current_email, *args, **kwargs)
    return decorated

class Register(Resource):
    def post(self):
        data_name = request.form.get('name')
        data_email = request.form.get('email')
        data_password = request.form.get('password')

        if data_email and data_password:
            dataModel = AuthModel(email=data_email, name=data_name, password=data_password)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"message":"Registration Success", "error":False}),200 )
        return jsonify({"message":"Email and Password must be filled", "error":True})

class Login(Resource):
    def post(self):
        data_email = request.form.get('email')
        data_password = request.form.get('password')

        q_email = [data.email for data in AuthModel.query.all()]
        q_password = [data.password for data in AuthModel.query.all()]
        
        if data_email in q_email and data_password in q_password:
            token = jwt.encode(
                {
                    "email":data_email, 
                    "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                }, app.config["SECRET_KEY"], algorithm="HS256")
            return make_response(jsonify({"message":"Login Success", "error":False, "token":token}), 200) 
        return jsonify({"message":"Login fail, Try again !", "error":True})

class Upload(Resource):
    @token_required
    def post(current_email,self):
        data_emotion = request.form.get('emotion')
        non_object_date = request.form.get('date')
        non_object_duration = request.form.get('duration')
        file = request.files['file']

        data_date = datetime.datetime.strptime(non_object_date, '%Y-%d-%m').date()
        data_duration = datetime.datetime.strptime(non_object_duration, '%H:%M:%S').time()
        upload_data = AudioModel(email_auth=current_email, emotion=data_emotion, date=data_date, duration=data_duration, filename=file.filename, data=file.read())
        db.session.add(upload_data)
        db.session.commit()
        return make_response(jsonify({"message": file.filename + " Upload Success","error": False}),200)

class History(Resource):
    @token_required
    def get(current_email, self):
        q = AudioModel.query.filter(AudioModel.email_auth == current_email)
        output = [
            {
                "emotion" : data.emotion,
                "duration" : json.dumps(data.duration, default=str),
                "date" : data.date
            } for data in q
        ] 
        return make_response(jsonify(output), 200)

class Profile(Resource):
    @token_required
    def put(current_email, self):
        q = AuthModel.query.get(current_email)
        
        data_name = request.form.get('name')
        data_pp = request.files['picture']
        
        q.name = data_name
        q.picture = data_pp.read()

        db.session.commit()
        return make_response(jsonify({'message': 'Name and Picture updated!', "error": False}), 200)

api.add_resource(Register, "/register", methods=["POST"])
api.add_resource(Login, "/login", methods=["POST"])
api.add_resource(Upload, "/upload", methods=["POST"])
api.add_resource(History, "/history", methods=["GET"])
api.add_resource(Profile, "/profile", methods=["PUT"])

if __name__ == "__main__":
    app.run(debug=True)
