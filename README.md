# Emotion Recognition API for Bangkit Capstone Project 2022

Our API in Android app that can predict the audio emotion to suggest the user for better public speaking


## Prerequisite
- Python 3

## Setup
- Clone repo
  ```
	git clone https://github.com/Bangkit-Academy-C22-PS198-Group/UsSpeak-API.git
	cd UsSpeak-API
  ```
- Create python virtual environment
    ```
	python -m venv env
    ```
- initialize virtual environment (Make sure to run in CMD)
    ```
	venv\Scripts\activate
    ```
- Install dependencies
    ```
	pip install -r requirements.txt
    ```
- run the api
    ```
	python main.py
    ```

## Deploy to Google App Engine
	gcloud app deploy

## Disclaimer
- If new CloudSQL is necessary
    ```
	https://cloud.google.com/sql/docs/mysql/create-instance
    ```

- Change the app.config['SQLALCHEMY_DATABASE_URI'] to the CloudSQL information
    ```
	"mysql://<CloudSQL_user>:<CloudSQL_pass>@<Instance_IP>/<db_name>?unix_socket=/cloudsql/<cloudSQL_connectionname>
    ```
- Not all dependencies is necessary


## Connect to local MySQL
- Change the app.config['SQLALCHEMY_DATABASE_URI'] to
    ```
	"mysql://<MySQL_user>:<MySQL_Pass>@localhost/<db_name>"
    ```

## API
## Login
- URL 
  ```
	/login
  ```
- Method
    ```
	POST
    ```
- Content-Type
    ```
	application/json
    ```
- Data Params
    ```
	email, password
    ```
- Success Response
    ```
	Code: 200
	Content: {"error": false, 
		    "message": "Login Success",
	            "token": jwt token }
    ```

## Register
- URL
    ```
	/register
    ```
- Method 
    ```
	POST
    ```
- Content-Type
    ```
	application/json
    ```
- Data Params
    ```
	email, password, name
    ```
- Success Response
    ```
    Code: 200
	Content: {"error": false, "message": "Registration Success"}
    ```

## Upload
- URL
    ```
	/upload
    ```
- Method
    ```
	POST
    ```
- Header
    ```
	authorization: jwt token
    ```
- Content-Type
    ```
	multipart/form-data
    ```
- Data Params
    ```
	file=[file]
    ```

- Success Response
    ```
	Code: 200
	  \Content: {"error": false, "message": file.filename + " upload success"}
    ```

## Get Upload History
- URL
    ```
	/history
    ```
- Method
    ```
	GET
    ```
- Header
    ```
	authorization: jwt token
    ```
- Content-Type
	```
    -
    ```
- Data Params
	```
    -
    ```
- Success Response
    ```
	    Code: 200
	    Content: { "items": [ 
			{ "date" : date,
			  "duration" : duration,
		          "emotion" : emotion,
		          "suggestion" : suggestion
		         }
    ```

## Change Account Name
- URL
    ```
	/profile
    ```
- Method
    ```
	PUT
    ```
- Header
    ```
	authorization: jwt token
    ```
- Content-Type
    ```
	application/json
    ```
- Data Params
    ```
	name
    ```
- Success Response
    ```
	Code: 200
	Content: {"error": false, "message": "name has been updated}
    ```

## Get Account Name and Email
- URL
    ```
	/profile
    ```
- Method
    ```
	GET
    ```
- Header
    ```
	authorization: jwt token
    ```
- Content-Type
    ```
	-
    ```
- Data Params
    ```
	-
    ```
- Success Response
    ```
	 Code: 200
	  Content: {"name": name, "email": email}
    ```
    
