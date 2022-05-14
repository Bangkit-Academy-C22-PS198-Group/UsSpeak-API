import random
import os
from flask import Flask, app, render_template, request

app = Flask(__name__)
    
@app.route("/upload", methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template('upload.html')
    elif request.method == "POST":
        audio_file = request.files.get("file")
        file_name = str(random.randint(0,1000))
        audio_file.save(file_name)
        print(audio_file)
        return "Upload Success"

        # remove audio file

        # send back the predicted keyword in json 
if __name__ == "__main__":
    app.run(host="localhost", port="5000")