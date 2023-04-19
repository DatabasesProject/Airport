from datetime import date
from fnmatch import fnmatchcase
from re import A
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

#Define a route to hello function
@app.route('/')
def homepage():
	return render_template('Home.html')


@app.route('/login')
def login():
	return render_template('login.html')

# #Define route for login
@app.route('/CustomerloginAuth', methods=['GET', 'POST'])
def CustomerloginAuth():
	
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	
	#executes query
	query = 'SELECT Customer_Email, Customer_password FROM Customer WHERE Customer_Email = %s and Customer_password = %s'
	cursor.execute(query, (username, password))
	
	#stores the results in a variable
	data = cursor.fetchone()

	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('customerlogedIn'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('LoginPage.html', error=error)



# #Define route for login
@app.route('/StaffloginAuth', methods=['GET', 'POST'])
def StaffloginAuth():
	
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	
	#executes query
	query = 'SELECT Username, Staff_password FROM Staff WHERE username = %s and Staff_password = %s'
	cursor.execute(query, (username, password))
	
	#stores the results in a variable
	data = cursor.fetchone()

	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('stafflogedIn'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('LoginPage.html', error=error)

@app.route('/customerLoggedIn')
def customerlogedIn():
	return render_template('CustmerLogin.html')




@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')


@app.route('/Register')
def register():
	return render_template('Register.html')


@app.route('/Cregister',  methods=['GET', 'POST'])
def customer_register():

	c_email = request.form['Email']
	password = request.form['Password']
	phone_number = request.form['PhoneNumber']
	fname= request.form['FirstName']
	lname= request.form['LastName']
	dob= request.form['DOB']
	passportNumber= request.form['PassportNumber']
	passportCountry= request.form['PassportCountry']
	passportExp= request.form['PassportExpiration']
	street= request.form['Street']
	building= request.form['Buliding']
	apt = request.form['Apartment']
	city= request.form['City']
	state= request.form['State']
	zipcode= request.form['ZipCode']

	cursor =conn.cursor()

	try:
		query1= "INSERT INTO Customer (Customer_Email, Passport_Number, Passport_Expiration, Passport_Country, First_name, Last_name, Customer_password, Customer_buliding, Street_name, Apartment, Customer_City, Customer_State, Zip_Code, Customer_date_of_birth) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s) "
		cursor.execute(query1, (c_email,passportNumber,passportExp,passportCountry,fname, lname, password,building,street,apt, city, state, zipcode, dob))
		conn.commit()
		query2 = "INSERT INTO Customer_Phone (Customer_Email, Customer_Phone_number) VALUES (%s, %s) "
		cursor.execute(query2, (c_email, phone_number))
		conn.commit()

	except Exception as e:
		conn.rollback()
		error = str(e)
		return render_template('Register.html', error=error)
    
	finally:
		cursor.close()
		return render_template('Home.html')




@app.route('/Sregister',  methods=['GET', 'POST'])
def staff_register():
	
	fname=request.form['FirstName']
	lname=request.form['LastName']
	dob= request.form['DOB']
	username=request.form['username']
	password=request.form['password']
	airline=request.form['AirlineName']
	SEmail=request.form['SEmail']
	sphone=request.form['SPhoneNumber']


	cursor =conn.cursor()

	try:
		query1= "INSERT INTO Staff (Username, Airline_Name, Staff_password, First_name, Last_name, DOB) VALUES (%s, %s,%s, %s, %s, %s) "
		cursor.execute(query1, (username, airline, password, fname, lname ,dob))
		conn.commit()

		query2 = "INSERT INTO Staff_Phone (Username, Staff_Phone_number) VALUES (%s, %s) "
		cursor.execute(query2, (username, sphone))
		conn.commit()

		query3 = "INSERT INTO Staff_Email (Username, Email_Address) VALUES (%s, %s) "
		cursor.execute(query3, (username, SEmail))
		conn.commit()

	except Exception as e:
		conn.rollback()
		error = str(e)
		return render_template('Register.html', error=error)
    
	finally:
		cursor.close()
		return render_template('Home.html')



@app.route('/search',  methods=['GET', 'POST'])
def search():
     
	# Return_Date= ''
	Departure_Airport= request.form['Departure_Airport']
	Arrival_Airport = request.form['Arrival_Airport']
	Departure_date = request.form['departure_date']


	# Return_Date = request.form['return_date']
	num_tickets= int(request.form['num_travelers'])
    
	cursor =conn.cursor()
	
	# if(Return_Date == ''):
	query = 'SELECT Airline_Name, Flight_Number, Departure_Airport, Departure_date, Arrival_Airport, Arrival_date, BasePrice, Flight_status FROM Flight Natural Join Airplane WHERE Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s'
	cursor.execute(query, (Departure_Airport,Departure_date, Arrival_Airport))
	data = cursor.fetchall()
	data[0]['BasePrice'] = data[0]['BasePrice'] * num_tickets

	cursor.close()

	return render_template('Flight.html', Flight=data)

# def check_status ():
# 	cursor =conn.cursor()

# 	cursor.execute(status_q)
# 	status=	cursor.fetchall()
# 	cursor.close()
# 	return status
# 	# print(status)



@app.route("/Purchase")
def purchase():
	return render_template('Purchase.html')



@app.route("/PurchaseAuth",  methods=[ 'GET', 'POST'])
def purchaseAuth():

	email = request.form['Email']
	p_fname = request.form('Passenger_First_Name')
	P_lname = request.form('Passenger_Last_Name')
	card_number = request.form('card_number')
	card_exp= request.form('Card_Expiration')
	DOB = request.form('DOB')
	final_price=100
	name_card = request.form('Card_Name')
	Card_Type = request.form('Card_Type')
	Purchase_date = request.form('Purchase_date')
	Purchase_time = request.form('Purchase_time')

	# num_tickets=session['num_travelers']


	cursor =conn.cursor()
	# return render_template('PurchasePage.html')
	try:
		query = "INSERT INTO Purchase(Customer_Email, Passenger_Fname, Passenger_Lname, Passenger_DOB, Final_price, Name_card, Card_number, Card_expiration, Card_type, Purchase_date, Purchase_time) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s) "
		cursor.execute(query, (email, p_fname, P_lname , DOB, final_price, name_card, card_number, card_exp, Card_Type, Purchase_date, Purchase_time))
		conn.commit()
		return render_template('PurchasePage.html')

	except Exception as e:
		conn.rollback()
		error = str(e)
		return render_template('Purchase.html', error=error)
    
	finally:
		cursor.close()
		return render_template('Purchase.html')


@app.route("/CustomerA",methods=['GET', 'POST'])
def customer_account():
	username = session['username']

	cursor =conn.cursor()

	try:
		query= 'SELECT * FROM Customer WHERE Customer_Email = %s'
		cursor.execute(query,(username))
		data = cursor.fetchone()
		return render_template('CustomerAccount.html',username=username, data=data)

	except Exception as e:
		conn.rollback()
		error = str(e)
		return render_template('CustomerAccount.html', error=error)
    
	finally:
		cursor.close()
		return render_template('CustomerAccount.html',username=username, data=data)

@app.route("/FlightInfo",methods=['GET', 'POST'])
def get_flight_info():
	return render_template('Flightinfo.html')

@app.route("/Feedback",methods=['GET', 'POST'])
def Feedback():
	return render_template('Feedback.html')

@app.route('/stafflogedIn')
def stafflogedIn():

	username = session['username']

	cursor =conn.cursor()

	try:
		query= 'SELECT * FROM Staff WHERE Username = %s'
		cursor.execute(query,(username))
		data = cursor.fetchone()

	except Exception as e:
		conn.rollback()
		error = str(e)
		return render_template('StaffAccount.html', error=error)
    
	finally:
		cursor.close()
		return render_template('StaffAccount.html',username=username, data=data)

@app.route('/createflight')
def createflight():
	return render_template('createflight.html')

@app.route('/insertFlight', methods=['GET', 'POST'])
def insertFlight():

	Airport_ID=request.form['Airport_ID']
	Airline_Name = request.form['Airline_Name']
	Flight_Number = request.form['Flight_Number']
	departure_date = request.form['departure_date']
	departure_time = request.form['departure_time']
	departure_airport= request.form['departure_airport']
	arrival_date= request.form['arrival_date']
	arrival_time= request.form['arrival_time']
	arrival_airport= request.form['arrival_airport']
	base_price = request.form['base_price']
	airbus = request.form['airbus']
	status = request.form['status']
	
	cursor =conn.cursor()
	query = "INSERT INTO Flight (Airport_ID, Airline_Name, Flight_Number departure_date, departure_time,departure_airport, arrival_date, arrival_time, arrival_airport,base_price, airbus,status) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
	cursor.execute(query,(Airport_ID, Airline_Name, Flight_Number, departure_date, departure_time,departure_airport, arrival_date, arrival_time, arrival_airport, base_price, airbus, status))
	cursor.commit()
	cursor.close()

	return render_template('createflight.html')

@app.route('/createAirplane')
def createAirplane():
	return render_template('createAirplane.html')

@app.route('/insertAirAirplane', methods=['GET', 'POST'])
def insertAirAirplane():

	Airline_Name= request.form['Airline_Name']
	airbus= request.form['airbus']
	seats= request.form['seats']
	manufacturer= request.form['manufacturer']
	Manufacture_date= request.form['Manufacture_date']
	
	cursor =conn.cursor()
	query = "INSERT INTO Airplane (Airline_Name, airbus, seats, manufacturer, Manufacture_date ) VALUES (%s, %s,%s, %s, %s)"
	cursor.execute(query,(Airline_Name, airbus, seats,manufacturer,Manufacture_date))
	cursor.commit()
	cursor.close()

	return render_template('createAirplane.html')

@app.route('/createAirport')
def createAirport():
	return render_template('createAirport.html')


@app.route('/insertAirport')
def insertAirport():

	Airport_ID= request.form["Airport_ID"]
	Airport_Name= request.form["Airport_Name"]
	Airport_City= request.form["Airport_City"]
	Airport_Country= request.form["Airport_Country"]
	Airport_Type= request.form["Airport_Type"]
	
	cursor =conn.cursor()
	query = "INSERT INTO Airport (Airport_ID, Airport_Name, Airport_City, Airport_Country, Airport_Type ) VALUES (%s, %s,%s, %s, %s)"
	cursor.execute(query,(Airport_ID, Airport_Name, Airport_City, Airport_Country, Airport_Type))
	cursor.commit()
	cursor.close()

	return render_template('createAirport.html')

@app.route('/Stats')
def Stats():
	return render_template('StaffStats.html')


		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)

