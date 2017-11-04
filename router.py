import os
import psycopg2
import urllib.parse
from flask import Flask, flash, session, g
from flask import jsonify
import logging
from logging.handlers import RotatingFileHandler
import sys
import bcrypt
import smtplib
from email.mime.text import MIMEText
import socket
import requests
import sendgrid
from sendgrid.helpers.mail import *
from itsdangerous import URLSafeTimedSerializer
import urllib.request
import datetime


BAD_REQUEST = 400

app = Flask(__name__)

# Functions to write:
	# make new user
	# log in
	# forgot password
	# searh for user
	# search for event
	# create new event
	# edit event
	# view/get event
	# view/get user

def connect_db():
	print("In connect_db")
	if not 'DATABASE_URL' in os.environ:
		print("You must have DATABASE_URL in your environment variable. See documentation.")
		print("Execute 'source .env' to set up this environment variable if running locally.")
		return 

	try:
		urllib.parse.uses_netloc.append("postgres")
		url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
		db = psycopg2.connect(
		    database=url.path[1:],
		    user=url.username,
		    password=url.password,
		    host=url.hostname,
		    port=url.port
		)

		return db

	except Exception as ex:
		print(ex)
		print("Unable to connect to database on system.")
		return

def get_db():
	print("In get_db")
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'pathwerks_db'):
		g.pathwerks_db = connect_db()
	return g.pathwerks_db

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().execute(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    try:
	    if hasattr(g, 'pathwerks_db'):
	        g.pathwerks_db.close()
    except:
	    print("Database connection was not open or was invalid.")

@app.route('/')
def hello_world():
	print("Got Here.")
	return 'Hello, World!'

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hased password. Useing bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)

def generate_token(email):
    serializer = URLSafeTimedSerializer(os.environ["SECURITY_KEY"])
    return serializer.dumps(email, salt=os.environ["SALT_KEY"])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.environ["SECURITY_KEY"])
    try:
        email = serializer.loads(
            token,
            salt=os.environ["SALT_KEY"],
            max_age=expiration
        )
    except:
        raise Exception("Error: Log in timed out. Please sign in again.")
    return email

# This function is called at the beginning of each API call, except for plogin and tlogin. 
# It's purpose is to confirm the identity of the caller by looking up the token in the 
# cookie (i.e. session). The email address and userid value are returned in that case. 
# Otherwise, an exception is raised with the message pertaining to why. See addvehicle 
# for an example of its use.

def confirm_identity():
	if not 'token' in session:
		raise Exception("Error: Not logged in.")

	token = session['token']

	email = confirm_token(token)

	db = get_db()
	cur = db.cursor()

	cur.execute("""Select userid, validated from "User" where email= %s;""",(email,))
	lst = cur.fetchall()

	if len(lst) == 0:
		raise Exception("Error: You must create a Userid first.")

	if len(lst) != 1:
		print("Error: User " + email + " is in the database more than once.")
		raise Exception("Error: Database error. Contact support.")

	validated = bool(lst[0][1])
	userid = lst[0][0]

	if not validated:
		raise Exception("Error: You must validate your email\naddress first. Look for an email\nfrom pathwerks.com and click\nthe link.")

	return (email, userid)



# --------------------------------------------------------------------
@app.route('/newuser/<email>/<password>')
def addUser(email, password):
	db = get_db()
	cur = db.cursor()

	cur.execute("""SELECT * FROM "User" WHERE email = %s;""", (email,))
	lst = cur.fetchall()

	if len(lst) != 0:
		# We're trying to add a user but it is already in the database
		print("YO WE ALREADY ADDED THIS EMAIL: " + email)
		return "Error: user already added.", BAD_REQUEST

	# The user (email) isn't in the database, so we can add the email and hashed password in
	hashed_password = get_hashed_password(password)
	cur.execute("""INSERT INTO "User" (email, password) VALUES (%s, %s);""", (email, hashed_password))
	db.commit()

	token = generate_token(email)
	sg = sendgrid.SendGridAPIClient(apikey = os.environ.get('SENDGRID_API_KEY'))
	from_email = Email("hawkol01@luther.edu")
	to_email = Email(email)
	subject = "Confirm your dedication to time management!"
	content= Content("test/html", """<a href=https://time-management-app13.herokuapp.com/verifyuser/""" + token + """">Please click this link to begin your journey of self-discovery using Boop!</a>""")
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body = mail.get())

	session['token'] = token
	return token 
	# INSERT INTO APPROPRIATE TABLES
# --------------------------------------------------------------------



@app.route('/newuser/<email>/<password>')
def newuser(email,password):
	print("In newuser")
	db = get_db()
	cur = db.cursor()
	cur.execute("""Select * from "User" where email= %s;""",(email,))
	lst = cur.fetchall()
	if len(lst) == 0:
		# the email address is not already taken
		# so build a hash value for the new entry. We use bcrypt because
		# it is slow and would help prevent a malicious attack
		hashed_password  = get_hashed_password(password)
		cur.execute("""INSERT INTO "User" (email, password) VALUES (%s,%s)""", (email, hashed_password))
		db.commit()

		token = generate_token(email)
		sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
		from_email = Email("custserv@pathwerks.com")
		to_email = Email(email)
		subject = "Please confirm your email address for Pathwerks.com"
		content = Content("text/html", """<a href="https://hidden-shore-94090.herokuapp.com/verifyuser/"""+token+"""">Please click this link to verify your account on Pathwerks.com</a>""")
		mail = Mail(from_email, subject, to_email, content)
		response = sg.client.mail.send.post(request_body=mail.get())

		session['token'] = token
		return token 

	#Did find a matching email so user cannot be created again.
	print("Error", email, "was already taken")
	return "Error: Email address is already taken.", BAD_REQUEST



# --------------------------------------------------------------------
@app.route('/verifyuser/<token>')
def verifyuser(token):
	db = get_db()
	cur = db.cursor()

	try:
		email = confirm_token(token)
	except Exception as ex:
		return str(ex), BAD_REQUEST

	cur.execute("""SELECT * FROM "User" WHERE email = %s;""", (email,))
	lst = cur.fetchall()
	if len(lst) == 1:
		cur.execute("""UPDATE "User" SET validated = true WHERE email=%s;""",(email,))
		db.commit()
		return "OK"

	return "Error: User does not exist.", BAD_REQUEST
# --------------------------------------------------------------------



# This will login with a user or create a user if no user by this email currently 
# exists. 

@app.route('/plogin/<email>/<password>')
def plogin(email,password):
	db = get_db()
	cur = db.cursor()
	cur.execute("""Select password,validated from "User" where email= %s;""",(email,))
	lst = cur.fetchall()
	
	if len(lst) == 1:
		# validate the password.
		if not lst[0][1]:
			return "Error: Account not validated. Check your email and validate account prior to logging in.", BAD_REQUEST

		if not check_password(password,lst[0][0]):
			return "Error: Invalid Userid or Password", BAD_REQUEST

		token = generate_token(email)
		session['token'] = token

		cur.execute("""Update "User" SET token=%s where email=%s;""",(token,email))
		db.commit()

		return token

	#Did not find a match. So, create the user instead.
	return newuser(email,password)

@app.route('/tlogin/<email>/<token>')
def tlogin(email,token):
	db = get_db()
	cur = db.cursor()
	cur.execute("""Select token,validated from "User" where email= %s;""",(email,))
	lst = cur.fetchall()

	if len(lst) == 1:
		# validated password?
		if not lst[0][1]:
			return "Error: Account not validated. Check your email and validate account prior to logging in.", BAD_REQUEST

		if token != lst[0][0]:
			return "Error: Invalid token", BAD_REQUEST


		try:
			tokenEmail = confirm_token(token,2592000)
		except Exception as ex:
			return str(ex), BAD_REQUEST

		if tokenEmail != email:
			return "Error: Invalid Email or Token", BAD_REQUEST

		token = generate_token(email)
		session['token'] = token

		cur.execute("""Update "User" SET token=%s where email=%s;""",(token,email))
		db.commit()

		return token

	#Did find a matching email so user cannot be created again.
	return "Error: Invalid email address.", BAD_REQUEST

@app.route('/getvehicles/')
def getvehicles():

	try:
		email, userid = confirm_identity()
	except Exception as ex:
		# Respond to the client with the error message.
		return str(ex), BAD_REQUEST

	db = get_db()
	cur = db.cursor()

	cur.execute("""Select vehicle_name, jpg from "Vehicle", "User", "Ownership", "VehicleModel" where email=%s and "Ownership".userid = "User".userid and "Ownership".vid = "Vehicle".vid and "Vehicle".modelid = "VehicleModel".modelid;""",(email,))
	lst = cur.fetchall()

	return jsonify(lst)

def getDataField(data_field, resp):
	idx = resp.find('<td class="wrap"> ' + data_field + ' </td>')
	if idx >= 0:
		txt = resp[idx:]
		data = txt.split(">")[3].split("<")[0].strip()
		return data

	return ""

def getVehicleInfo(cur, vin):
	info = {"modelid":1, "make":"Unknown", "model":"", "year":"", "vehicle_type":"", "engine_cylinders":"", "engine_liters":"", "horse_power":"", "drive_type":""}
	vintag = vin[:10]

	cur.execute("""Select modelid, make, model, year, vehicle_type, engine_cylinders, engine_liters, horse_power, drive_type, jpg from "VehicleModel" where vintag=%s;""",(vintag,))

	lst = cur.fetchall()

	if len(lst)==0:
		# Then the model is not yet in the database so it must be added.
		resp = urllib.request.urlopen("https://vpic.nhtsa.dot.gov/decoder/Decoder?VIN="+vin).read().decode('utf-8')

		ec = int(resp[resp.find("Error Code:"):].split(">")[1].split("-")[0].strip())

		if ec != 0:
			info["modelid"] = 2
			info["make"] = "Invalid VIN"
			return info


		info["make"] = getDataField("Make", resp)
		info["model"] = getDataField("Model", resp)
		info["year"] = getDataField("Model Year", resp)
		info["vehicle_type"] = getDataField("Vehicle Type", resp)
		info["engine_cylinders"] = getDataField("Engine Number of Cylinders", resp)
		info["engine_liters"] = getDataField("Displacement (L)", resp)
		info["horse_power"] = getDataField("Engine Brake (hp)", resp)
		info["drive_type"] = getDataField("Drive Type", resp)
		info["jpg"] = "http://www.fueleconomy.gov/feg/photos/"+info["year"]+"_"+info["make"]+"_"+info["model"]+".jpg"


		cur.execute("""INSERT INTO "VehicleModel" (vintag,make,model,year,vehicle_type,engine_cylinders,engine_liters,horse_power,drive_type,jpg) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING modelid""", (vin[:10],info["make"],info["model"],info["year"],info["vehicle_type"],info["engine_cylinders"],info["engine_liters"],info["horse_power"],info["drive_type"],info["jpg"]))
		modelid = cur.fetchone()[0]
		info["modelid"] = modelid
	else:
		# The model information was found in the database. Fill it in in the info dictionary
		info["modelid"] = lst[0][0]
		info["make"] = lst[0][1]
		info["model"] = lst[0][2]
		info["year"] = lst[0][3]
		info["vehicle_type"] = lst[0][4]
		info["engine_cylinders"] = lst[0][5]
		info["engine_liters"] = lst[0][6]
		info["horse_power"] = lst[0][7]
		info["drive_type"] = lst[0][8]
		info["jpg"] = lst[0][9]

	return info

# --------------------------------------------------------------------
@app.route('/getuser/<email>')
def getUser(email):

	# Confirm identity here 

	db = get_db()
	cur = dub.cursor()

	cur.execute(
		"""SELECT * FROM "User" WHERE email = %s;""", (email)
		)
	lst = cur.fetchall()

	if len(lst) == 0:
		# No users found
		return "Error: user not found.", BAD_REQUEST

	print("List of users found: ")
	print(jsonify(lst))
# --------------------------------------------------------------------

@app.route('/getvehicle/<name>')
def getvehicle(name):

	try:
		email, userid = confirm_identity()
	except Exception as ex:
		# Respond to the client with the error message.
		return str(ex), BAD_REQUEST

	db = get_db()
	cur = db.cursor()

	cur.execute("""Select vin from "Vehicle", "Ownership" where vehicle_name =%s and "Vehicle".vid="Ownership".vid and "Ownership".userid = %s;""",(name,userid))
	lst = cur.fetchall()

	if len(lst)==0:
		# We may need to initiate a transfer of vehicle here if the userid
		# is not the same as this user. 
		return "Error: Vehicle not found.", BAD_REQUEST

	vin = lst[0][0]

	info = getVehicleInfo(cur, vin)

	info.pop("modelid") # remove the modelid from the dictionary to be returned.

	return jsonify(info)



@app.route('/addvehicle/<name>/<vin>/<odo>')
def addvehicle(name,vin,odo):
	
	try:
		email, userid = confirm_identity()
	except Exception as ex:
		# Respond to the client with the error message.
		return str(ex), BAD_REQUEST

	db = get_db()
	cur = db.cursor()

	cur.execute("""Select vid from "Vehicle" where vin=%s;""",(vin,))
	lst = cur.fetchall()

	if len(lst)!=0:
		# We may need to initiate a transfer of vehicle here if the userid
		# is not the same as this user. 
		return "Error: VIN already added.", BAD_REQUEST

	info = getVehicleInfo(cur,vin)
	modelid = info["modelid"]

	cur.execute("""INSERT INTO "Vehicle" (vin, modelid, initialodo) VALUES (%s,%s,%s) RETURNING vid""", (vin,modelid,odo))
	vid = cur.fetchone()[0]

	cur.execute("""INSERT INTO "Ownership" (userid, vid, vehicle_name, start_date) VALUES (%s,%s,%s,%s)""", (userid, vid, name, datetime.date.today()))

	db.commit()

	return "OK"



app.secret_key = b'\xa3K\x07\x95\xf7\x9cn:\xbeRWaj\xf1\xdc\xf48\xca\xe4R\xea\x8dI9'

if __name__ == "__main__":
	#logging.basicConfig(filename='error.log', level=logging.INFO)
	handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.logger.setLevel(logging.INFO)
	app.run(debug=True,host='0.0.0.0')