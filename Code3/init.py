from calendar import c
from cgitb import Hook
from csv import list_dialects
from datetime import date
from distutils.log import error
from fnmatch import fnmatchcase
from functools import total_ordering
from re import A
from sre_parse import GLOBAL_FLAGS
from sys import get_coroutine_origin_tracking_depth
from this import d
from zoneinfo import available_timezones
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


# session['logged_in'] = False


#Define a route to hello function
@app.route('/')
def homepage():

	cursor =conn.cursor()

	select_Departure_Airport= 'SELECT DISTINCT Departure_Airport FROM Flight'
	cursor.execute(select_Departure_Airport)
	list_Departure_Airport= cursor.fetchall()

	select_Arrival_Airport = 'SELECT DISTINCT Arrival_Airport FROM Flight'
	cursor.execute(select_Arrival_Airport)
	list_Arrival_Airport= cursor.fetchall()

	select_Airlines = 'SELECT DISTINCT Airline_Name FROM Flight'
	cursor.execute(select_Airlines)
	list_Airlines= cursor.fetchall()
	
	select_flight_number = 'SELECT DISTINCT flight_number FROM Flight'
	cursor.execute(select_flight_number)
	list_flight_number= cursor.fetchall()

	cursor.close()

	logged_in = session.get('logged_in', False)

	return render_template('Home.html', Departure=list_Departure_Airport, Arrival=list_Arrival_Airport, Airline_N= list_Airlines, Flight_num=list_flight_number,logged_in=logged_in)


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
			session['username'] = username
			session['logged_in'] = True
			return redirect(url_for('homepage'))

	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('LoginPage.html', error=error)



#Define route for login
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


@app.route('/logout')
def logout():
	
	session.pop('username')
	session.pop('logged_in', False)

 
	return redirect('/')


@app.route('/Register')
def register():

	cursor =conn.cursor()
	select_Airlines = 'SELECT DISTINCT Airline_Name FROM Flight'
	cursor.execute(select_Airlines)
	list_Airlines= cursor.fetchall()
	cursor.close()

	return render_template('Register.html', Airline_N=list_Airlines)


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
	airline=request.form['Airline_Name']
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



@app.route('/OneWay',  methods=['GET', 'POST'])
def OneWay():
	
	error=None

	cursor =conn.cursor()

	Departure_Airport= request.form['Departure_Airport']
	Arrival_Airport = request.form['Arrival_Airport']
	Departure_date = request.form['departure_date']
	num_tickets= int(request.form['num_travelers'])
	
	# getting the number of seats each flight
	get_flight_capacity = 'SELECT Seats FROM Airplane NATURAL JOIN Flight Where Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s AND  Flight_status !="Canceled" '
	cursor.execute(get_flight_capacity, (Departure_Airport,Departure_date ,Arrival_Airport))
	flight_capacity= int(cursor.fetchall())


	number_purchesed_seats='SELECT COUNT(Ticket_id) AS Purchase_tickets FROM Purchase NATURAL JOIN  Ticket  NATURAL JOIN Flight GROUP by Flight_Number'
	cursor.execute(number_purchesed_seats)
	purchesed_seats= int(cursor.fetchall())
	
	available_seats=flight_capacity- purchesed_seats

	print(available_seats)
    
	if(available_seats <= 0):
		error="Flight Is Full Booked"
	
	else:
		get_flight_data = 'SELECT Airline_Name, Flight_Number, Departure_Airport, Departure_date, Departure_time, Arrival_Airport, Arrival_date, BasePrice, Flight_status FROM Flight Natural Join Airplane WHERE Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s AND  Flight_status !="Canceled" '
		cursor.execute(get_flight_data, (Departure_Airport,Departure_date, Arrival_Airport))
		data = cursor.fetchall()

	get_flight_data = 'SELECT * FROM Flight Natural Join Airplane WHERE Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s AND  Flight_status !="Canceled" '
	cursor.execute(get_flight_data, (Departure_Airport,Departure_date, Arrival_Airport))
	data = cursor.fetchall()
	
	if data:
		session['Flight_number'] = data[0]['Flight_Number']
		session['Departure_date']= Departure_date
		session['num_travelers'] = num_tickets
		session['BasePrice']= data[0]['BasePrice']
		session['Airline_name']=data[0]['Airline_Name']
		session['Departure_time']=str(data[0]['Departure_time'])
		
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
	
	logged_in = session.get('logged_in', False)
	# if not logged in
	if logged_in==False:
		return redirect(url_for('login'))
	
	num_tickets=session['num_travelers']
	price = session['BasePrice']
	total_amount=price*num_tickets
	return render_template('Purchase.html',  num_tickets=num_tickets,total_amount=total_amount)



@app.route("/PurchaseAuth",  methods=[ 'GET', 'POST'])
def purchaseAuth():

	num_tickets = session['num_travelers']
	price = session['BasePrice']
	email=session['username']
	flight_number = session['Flight_number']
	Departure_date =session['Departure_date']
	Airline_name = session['Airline_name']
	Departure_time=session['Departure_time']

	
	cursor =conn.cursor()

	for i in range(num_tickets):
		
		p_fname = request.form("First_name")
		P_lname = request.form("Last_Name")
		DOB = request.form("DOB")
		name_card = request.form('Card_Name')
		Card_Type = request.form('Card_Type')
		card_number = request.form('card_number')
		card_exp= request.form('Card_Expiration')
		final_price= 850
		
		get_date='Select CURDATE()'
		cursor.execute(get_date)
		Purchase_date=cursor.fetchone()

		get_time='SELECT CURTIME()'
		cursor.execute(get_time)
		Purchase_time=cursor.fetchone()

		get_ticket_number='SELECT Ticket_ID FROM Ticket WHERE Airline_name=%s and flight_Number =%s and Departure_date=%s and Departure_time= %s and Ticket_Id not in (SELECT Ticket_Id FROM Purchase)' 
		cursor.execute(get_ticket_number, (Airline_name,flight_number, Departure_date, Departure_time))
		ticket_id = cursor.fetchone()

		insert_Purchase_info = "INSERT INTO Purchase(Customer_Email,Ticket_ID,Passenger_Fname, Passenger_Lname, Passenger_DOB, Final_price, Name_card, Card_number, Card_expiration, Card_type, Purchase_date, Purchase_time) VALUES (%s, %s,%s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s) "
		cursor.execute(insert_Purchase_info, (email,ticket_id ,p_fname, P_lname , DOB, final_price, name_card, card_number, card_exp, Card_Type, Purchase_date, Purchase_time))
		conn.commit()
	
	cursor.close()
	return render_template('CustomerAccount.html', num_tickets=num_tickets)
	



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
	
	cursor =conn.cursor()

	select_Airbus='SELECT airbus FROM Airplane'
	cursor.execute(select_Airbus)
	list_Airbus=cursor.fetchall()

	select_airline='SELECT * FROM Airline'
	cursor.execute(select_airline)
	list_airline=cursor.fetchall()

	select_airportID='SELECT Airport_ID FROM Airport'
	cursor.execute(select_airportID)
	list_airportID=cursor.fetchall()

	select_airportName='SELECT Airport_Name FROM Airport'
	cursor.execute(select_airportName)
	list_airportName=cursor.fetchall()

	return render_template('createflight.html', Airline =list_airline, Airbus_N =list_Airbus,  Airport=list_airportID, Airport_D=list_airportName,Airport_A=list_airportName )

@app.route('/insertFlight', methods=['GET', 'POST'])
def insertFlight():

	Airport_ID=request.form['Airport_ID']
	Airline_Name = request.form['Airline_Name']
	Flight_Number = request.form['Flight_Number']
	departure_date = request.form['Departure_date']
	departure_time = request.form['Departure_time']
	departure_airport= request.form['Departure_Airport']
	arrival_date= request.form['Arrival_date']
	arrival_time= request.form['Arrival_time']
	arrival_airport= request.form['Airival_Airport']
	base_price = request.form['BasePrice']
	airbus = request.form['Airbus']
	status = request.form['Status']

	cursor =conn.cursor()
	query = "INSERT INTO Flight (Airport_ID, Airbus,Airline_Name, Flight_Number, Departure_date, Departure_time, Departure_Airport, Arrival_time, Arrival_date, Arrival_Airport, BasePrice, Flight_status) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
	cursor.execute(query,(Airport_ID, airbus, Airline_Name, Flight_Number, departure_date, departure_time, departure_airport,arrival_time,arrival_date, arrival_airport, base_price, status))
	conn.commit() 
	cursor.close()

	return redirect(url_for('createflight'))

@app.route('/createAirplane')
def createAirplane():

	cursor =conn.cursor()
	select_Airlines = 'SELECT DISTINCT Airline_Name FROM Flight'
	cursor.execute(select_Airlines)
	list_Airlines= cursor.fetchall()
	cursor.close()

	return render_template('createAirplane.html', Airline_N=list_Airlines)

@app.route('/insertAirplane', methods=['GET', 'POST'])
def insertAirAirplane():

	Airline_Name= request.form['Airline_Name']
	airbus= request.form['airbus']
	seats= request.form['seats']
	manufacturer= request.form['manufacturer']
	Manufacture_date= request.form['Manufacture_date']
	
	cursor =conn.cursor()
	query = "INSERT INTO Airplane (Airline_Name, airbus, seats, manufacturer, Manufacture_date ) VALUES (%s, %s,%s, %s, %s)"
	cursor.execute(query,(Airline_Name, airbus, seats,manufacturer,Manufacture_date))
	conn.commit()
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
	conn.commit()
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