#Import Flask Library
from dataclasses import dataclass
from functools import total_ordering
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost', 
					   port= 8889,
                       user='root',
                       password='root',
                       db='Airport',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


#storing the each Airplane seats capicity 
cur1 =conn.cursor()
capcity={}
capcity_query ='SELECT Airbus, Seats FROM Airplane where 1'
cur1.execute(capcity_query)
capcity = cur1.fetchall()



#Define a route to hello function
@app.route('/')
def homepage():
	return render_template('HomePage.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')


@app.route('/search',  methods=['GET', 'POST'])
def search():
	
	Departure_Airport= request.form['Departure_Airport']
	Arrival_Airport = request.form['Arrival_Airport']
	Departure_date = request.form['departure_date']
	# Return_Date = request.form['return_date']

	cursor =conn.cursor()
	query = 'SELECT Airline_Name, Flight_Number, Departure_Airport, Departure_date, Arrival_Airport, Arrival_date, BasePrice, Seats FROM Flight Natural Join Airplane WHERE Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s'
	cursor.execute(query, (Departure_Airport,Departure_date, Arrival_Airport))
	data1 = cursor.fetchall()
	cursor.close()
	return render_template('Flight.html', Flight=data1)

@app.route('/PurchaseAuth',  methods=['GET', 'POST'])
def purchase():
	# number_tickets= request.form.get('Tickets')
	# ticket_price_str= request.form.get('BasePrice')
	# ticket_price = int(ticket_price_str)
	# total_price = ticket_price *int(number_tickets)

	return render_template('PurchasePage.html')

# @app.route('/purchase')
# def purchase():


# #Authenticates the login
# @app.route('/loginAuth', methods=['GET', 'POST'])
# def loginAuth():
# 	#grabs information from the forms
# 	username = request.form['username']
# 	password = request.form['password']

# 	#cursor used to send queries
# 	cursor = conn.cursor()
# 	#executes query
# 	query = 'SELECT * FROM user WHERE username = %s and password = %s'
# 	cursor.execute(query, (username, password))
# 	#stores the results in a variable
# 	data = cursor.fetchone()
# 	#use fetchall() if you are expecting more than 1 data row
# 	cursor.close()
# 	error = None
# 	if(data):
# 		#creates a session for the the user
# 		#session is a built in
# 		session['username'] = username
# 		return redirect(url_for('home'))
# 	else:
# 		#returns an error message to the html page
# 		error = 'Invalid login or username'
# 		return render_template('login.html', error=error)

#Authenticates the register
# @app.route('/registerAuth', methods=['GET', 'POST'])
# def registerAuth():
# 	#grabs information from the forms
# 	username = request.form['username']
# 	password = request.form['password']

# 	#cursor used to send queries
# 	cursor = conn.cursor()
# 	#executes query
# 	query = 'SELECT * FROM user WHERE username = %s'
# 	cursor.execute(query, (username))
# 	#stores the results in a variable
# 	data = cursor.fetchone()
# 	#use fetchall() if you are expecting more than 1 data row
# 	error = None
# 	if(data):
# 		#If the previous query returns data, then user exists
# 		error = "This user already exists"
# 		return render_template('register.html', error = error)
# 	else:
# 		ins = 'INSERT INTO user VALUES(%s, %s)'
# 		cursor.execute(ins, (username, password))
# 		conn.commit()
# 		cursor.close()
# 		return render_template('index.html')

# @app.route('/home')
# def home():
    
#     username = session['username']
#     cursor = conn.cursor()
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, (username))
#     data1 = cursor.fetchall() 
#     for each in data1:
#         print(each['blog_post'])
#     cursor.close()
#     return render_template('home.html', username=username, posts=data1)

		
# @app.route('/post', methods=['GET', 'POST'])
# def post():
# 	username = session['username']
# 	cursor = conn.cursor()
# 	blog = request.form['blog']
# 	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
# 	cursor.execute(query, (blog, username))
# 	conn.commit()
# 	cursor.close()
# 	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)

