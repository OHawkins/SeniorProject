import os
import psycopg2
import urllib.parse

# This Python program is written this way because Heroku will provide the database in the 
# DATABASE_URL environment variable. We don't pick the name. It is provided by the web hosting
# site. For local testing database the initlocal script can be called to set up the environment
# to run this locally on a test system. 

def main():
	if not 'DATABASE_URL' in os.environ:
		print("You must have DATABASE_URL in your environment variable. See documentation.")
		return 

	urllib.parse.uses_netloc.append("postgres")
	url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

	try:
		db = psycopg2.connect(
		    database=url.path[1:],
		    user=url.username,
		    password=url.password,
		    host=url.hostname,
		    port=url.port
		)

	except Exception as ex:
		print(ex)
		print("Unable to connect to database on system.")
		return

	with open('schema.sql', mode='r') as f:
		db.cursor().execute(f.read())

	db.commit()

	print("Database Creation Complete")

if __name__ == "__main__":
	main()



#postgres://ayadcvekawllbv:bf93aefb081d50e95a643dd5a57a3c958b213933274b26c55b3a1deb0207e3de@ec2-23-21-80-230.compute-1.amazonaws.com:5432/d1ak7qikg87gnr
