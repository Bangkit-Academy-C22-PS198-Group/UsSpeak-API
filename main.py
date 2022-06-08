from functools import wraps
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from mutagen.wave import WAVE

# import os
import datetime
import jwt  
import json
import tensorflow as tf
import numpy as np
import librosa
import csv
import random
# import pickle
# import numpy as np
# import librosa

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

# Database Configuration
# filename = os.path.dirname(os.path.abspath(__file__))
# database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
# app.config['SQLALCHEMY_DATABASE_URI'] = database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password123@localhost/database_2'
app.config['SQLALCHEMY_DATABASE_URI']= "mysql://root:password123@34.101.234.99/capstone-db?unix_socket=/cloudsql/c22-ps198-352707:asia-southeast2:c22-ps198-instance"
# app.config['SQLALCHEMY_DATABASE_URI'] = gen_connection_string()
app.config["SECRET_KEY"] = "secretkey"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

path = 'new_model.h5'
load_options = tf.saved_model.LoadOptions(experimental_io_device='/job:localhost')
model = tf.keras.models.load_model(path, options=load_options)
random = random.randint(1,3)

class AuthModel(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))
    picture = db.Column(db.LargeBinary((2**32)-1))

class AudioModel(db.Model):
    email_auth = db.Column(db.String(50))
    filename = db.Column(db.String(100), primary_key=True)
    emotion = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    duration = db.Column(db.Time)
    data = db.Column(db.LargeBinary((2**32)-1))
    suggestion = db.Column(db.Text)

db.create_all()

# decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('authorization')
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

def audio_duration(length):
    hours = length // 3600  # calculate in hours
    length %= 3600
    mins = length // 60  # calculate in minutes
    length %= 60
    seconds = length  # calculate in seconds
    return '{}:{}:{}'.format(hours, mins, seconds)

class Register(Resource):
    def post(self):
        data_name = request.json.get('name')
        data_email = request.json.get('email')
        data_password = request.json.get('password')

        if data_email and data_password:
            dataModel = AuthModel(email=data_email, name=data_name, password=data_password)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"message":"Registration Success", "error":False}),200 )
        return jsonify({"message":"Email and Password must be filled", "error":True})

class Login(Resource):
    def post(self):
        data_email = request.json.get('email')
        data_password = request.json.get('password')

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
        file = request.files.get('file')
        
        #load suggestion
        filename = 'suggestion_fix.csv'
        with open(filename, 'r') as f:
            rows = list(csv.reader(f))

        #predict
        X, sample_rate = librosa.load(file, res_type="kaiser_fast")
        mfcc = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_fft=4096, hop_length=256, n_mfcc=40).T,axis=0)
        mfcc = mfcc.reshape(1,-1)
        result = np.argmax(model.predict(mfcc), axis=-1)

        for i in range(0, 6, 1):
            if result[0] == i:
                data_emotion = 'Sad'
                data_suggestion = rows[i][random]
                break
            else:
                data_emotion = rows[i][0]
                data_suggestion = rows[i][random]
                break

        #duration
        audio = WAVE(file)
        audio_info = audio.info
        length = int(audio_info.length)
        duration = audio_duration(length)
        data_duration = datetime.datetime.strptime(duration, '%H:%M:%S').time()

        #check emotion
        upload_data = AudioModel(email_auth=current_email, emotion=data_emotion, duration=data_duration, suggestion=data_suggestion, filename=file.filename, data=file.read())
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
                "suggestion" : data.suggestion,
                "date" : data.date
            } for data in q
        ] 
        return make_response(jsonify(output), 200)

class Profile(Resource):
    @token_required
    def put(current_email, self):
        q = AuthModel.query.get(current_email)
        
        data_name = request.json.get('name')
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
    app.run()
    