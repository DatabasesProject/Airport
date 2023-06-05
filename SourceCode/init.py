from asyncio.format_helpers import _get_function_source
from calendar import c, month
from cgitb import Hook
import datetime
from datetime import date
from datetime import time
from distutils.log import error
from fnmatch import fnmatchcase
from functools import total_ordering
from math import remainder
from re import A
import re
from select import select
from sre_parse import GLOBAL_FLAGS
from sys import get_coroutine_origin_tracking_depth
from sysconfig import get_paths
from this import d
from webbrowser import get
from zoneinfo import available_timezones
import re
import hashlib
import json
import ast
import yaml
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__, static_folder='images')

#Configure MySQL
conn = pymysql.connect(host='localhost', 
					   port= 8889,
                       user='root',
                       password='root',
                       db='Airport',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)




# Define a route to the homepage
@app.route('/', methods=['GET', 'POST'])
def homepage():
	
	error=None

	cursor =conn.cursor()

   # Select all unique departure airports from Flight table
	select_Departure_Airport= 'SELECT DISTINCT Departure_Airport FROM Flight'
	cursor.execute(select_Departure_Airport)
	list_Departure_Airport= cursor.fetchall()

   # Select all unique arrival airports from Flight table
	select_Arrival_Airport = 'SELECT DISTINCT Arrival_Airport FROM Flight'
	cursor.execute(select_Arrival_Airport)
	list_Arrival_Airport= cursor.fetchall()

    # Select all unique airlines from Flight table
	select_Airlines = 'SELECT DISTINCT Airline_Name FROM Flight'
	cursor.execute(select_Airlines)
	list_Airlines= cursor.fetchall()
	
	 # Select all unique flight numbers from Flight table
	select_flight_number = 'SELECT DISTINCT flight_number FROM Flight'
	cursor.execute(select_flight_number)
	list_flight_number= cursor.fetchall()

	cursor.close()
    
	# Get the 'logged_in' and 'staffLogin' values from the session object
	logged_in = session.get('logged_in', False)
	staff=session.get('staffLogin', False)

	# Determine if the user is logged in or not and set staff and nonLogged variables accordingly
	if logged_in == True:
		staff=False
		nonLogged= False

	elif staff == True:
		logged_in = False
		nonLogged= False
	else:
		nonLogged=True
	
	selected_tab = request.args.get('tab', default='one-way', type=str)
	 
	return render_template('Home.html', Departure=list_Departure_Airport, Arrival=list_Arrival_Airport, Airline_N= list_Airlines, Flight_num=list_flight_number,logged_in=logged_in, staff=staff, nonlogged=nonLogged, selected_tab=selected_tab)

# Define a route to the login page
@app.route('/login')
def login():
	return render_template('login.html')


# Define route for customer login authentication
@app.route('/CustomerloginAuth', methods=['GET', 'POST'])
def CustomerloginAuth():
	
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
    
	# Hashes the password
	password=hashlib.md5(password.encode())


	#cursor used to send queries
	cursor = conn.cursor()
	
	#executes query Checks if login is correct
	query = 'SELECT Customer_Email, Customer_password FROM Customer WHERE Customer_Email = %s and Customer_password = %s'
	cursor.execute(query, (username, password.hexdigest()))
	
	#stores the results in a variable
	data = cursor.fetchone()


	
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		# assign all the necssery sessions 
		session['num_travelers']=1
		session['Return_date']=1
		session['price']=1
		session['Flight_number'] = 1		
		session['Airline_name'] = 1
		session['Departure_date']= 1
		session['Departure_time']= 1
		session['Flight_number2'] = 1
		session['Airline_name2'] = 1
		session['Departure_date2']= 1
		session['Departure_time2']= 1
		session['username'] = username
		session['logged_in'] = True
		return redirect(url_for('homepage'))

	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('LoginPage.html', error=error)



# Define route for Staff login authentication
@app.route('/StaffloginAuth', methods=['GET', 'POST'])
def StaffloginAuth():
	
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	password=hashlib.md5(password.encode())

	#cursor used to send queries
	cursor = conn.cursor()
	
	#executes query Checks if login is correct
	query = 'SELECT Username, Staff_password FROM Staff WHERE username = %s and Staff_password = %s'
	cursor.execute(query, (username, password.hexdigest()))
	
	#stores the results in a variable
	data = cursor.fetchone()

    # Get the airline name for the staff member
	get_airline_name='Select Airline_Name from Staff where username=%s'
	cursor.execute(get_airline_name, (username))
	Airline_name=cursor.fetchone()

	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		# assign all the necssery sessions
		session['Airline_Name']=Airline_name['Airline_Name']
		session['staffLogin'] = True
		session['username'] = username
		return redirect(url_for('homepage'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('LoginPage.html', error=error)


#logout for customer 
@app.route('/Clogout')
def Clogout():

	# Clear all the session variables related to the customer
	session.pop('username')
	session.pop('num_travelers')
	session.pop('Departure_date')
	session.pop('Departure_time')
	session.pop('Return_date')
	session.pop('Flight_number')
	session.pop('Airline_name')
	session.pop('Flight_number2')
	session.pop('Airline_name2')
	session.pop('Departure_date2')
	session.pop('Departure_time2')
	session.pop('price')
	session.pop('logged_in', False)

 
	return redirect('/')

#logout for Staff 
@app.route('/Slogout')
def Slogout():
	session.pop('username')
	session.pop('Airline_Name')
	session.pop('staffLogin', False)
 
	return redirect('/')

# register page that will display a forms to register users or staff
@app.route('/Register')
def register():
     
	 # Staff can only register for one airline
	cursor =conn.cursor()
	select_Airlines = 'SELECT DISTINCT Airline_Name FROM Airline'
	cursor.execute(select_Airlines)
	list_Airlines= cursor.fetchall()
	cursor.close()

	return render_template('Register.html', Airline_N=list_Airlines)

# insert the customer form into the database
@app.route('/Cregister',  methods=['GET', 'POST'])
def customer_register():


   # get the customer values from the forms 
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



	password=hashlib.md5(password.encode())
     

	cursor =conn.cursor()
  
     #insert into database customers information 
	try:
		query1= "INSERT INTO Customer (Customer_Email, Passport_Number, Passport_Expiration, Passport_Country, First_name, Last_name, Customer_password, Customer_buliding, Street_name, Apartment, Customer_City, Customer_State, Zip_Code, Customer_date_of_birth) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s) "
		cursor.execute(query1, (c_email,passportNumber,passportExp,passportCountry,fname, lname, password.hexdigest(),building,street,apt, city, state, zipcode, dob))
		conn.commit()
		query2 = "INSERT INTO Customer_Phone (Customer_Email, Customer_Phone_number) VALUES (%s, %s) "
		cursor.execute(query2, (c_email, phone_number))
		conn.commit()
		cursor.close()
		return redirect('/')

	except Exception as e:
		conn.rollback()
		error = str(e)
		return render_template('Register.html', error=error)
    
	finally:
		cursor.close()
		return redirect('/')



# Register a staff in the database
@app.route('/Sregister',  methods=['GET', 'POST'])
def staff_register():
	
	# get the staff values from the form
	fname=request.form['FirstName']
	lname=request.form['LastName']
	dob= request.form['DOB']
	username=request.form['username']
	password=request.form['password']
	airline=request.form['Airline_Name']
	SEmail=request.form['SEmail']
	sphone=request.form['SPhoneNumber']

	password=hashlib.md5(password.encode())


	cursor =conn.cursor()
    
	# checking if staff is already registered with another airline 
	staff_check = 'Select username from Staff where username = %s'
	cursor.execute(staff_check, username)
	check = cursor.fetchone()


	if	(check is  None):   # if he is not registered then insert staff into database
		try:
			#inserting into the staff table
			query1= "INSERT INTO Staff (Username, Airline_Name, Staff_password, First_name, Last_name, DOB) VALUES (%s, %s,%s, %s, %s, %s) "
			cursor.execute(query1, (username, airline, password.hexdigest(), fname, lname ,dob))
			conn.commit()
             
			#inserting into the staff phone table
			query2 = "INSERT INTO Staff_Phone (Username, Staff_Phone_number) VALUES (%s, %s) "
			cursor.execute(query2, (username, sphone))
			conn.commit()
            
			#inserting into the staff email table
			query3 = "INSERT INTO Staff_Email (Username, Email_Address) VALUES (%s, %s) "
			cursor.execute(query3, (username, SEmail))
			conn.commit()
			cursor.close()

		except Exception as e:
			conn.rollback()
			error = str(e)
			return render_template('Register.html', error=error)
		
		finally:
			cursor.close()
			return redirect('/')
	else:
		return "Can only register to one Airline"


# The OneWay function is used to display all the one-way flights 
@app.route('/OneWay',  methods=['GET', 'POST'])
def OneWay():
	
	error=None

	cursor =conn.cursor()
    
	# getting all the selected input fields
	Departure_Airport= request.form['Departure_Airport']
	Arrival_Airport = request.form['Arrival_Airport']
	Departure_date = request.form['departure_date']
	num_tickets= int(request.form['num_travelers'])

    
	# creating a temp view to store all the flights that are at 80% flight capacity or greater
	get_flight_info='Create View find_flights as (SELECT Flight_Number FROM price_adjust NATURAL JOIN Flight WHERE Departure_Airport = %s AND Departure_date = %s AND Arrival_Airport = %s AND Seats_Ratio > 0.8)'
	cursor.execute(get_flight_info, (Departure_Airport,Departure_date,Arrival_Airport))
	conn.commit()
      
	# adjusting the flight of the price if the flight capacity is 80% or more
	set_price= 'UPDATE Flight JOIN find_flights ON Flight.Flight_Number = find_flights.Flight_Number SET BasePrice = BasePrice * 1.25; '
	cursor.execute(set_price)
	conn.commit()
   
    # deleting the view from the database
	drop_table='DROP VIEW IF EXISTS find_flights'
	cursor.execute(drop_table)
	conn.commit()
   
    # Geting all the one-way flight selected by the user
	get_flight_data = 'SELECT Airport_ID, Flight_Number,Airline_Name, Departure_Airport, Departure_date,  Departure_time, Arrival_Airport, Arrival_date, Arrival_time, BasePrice FROM Flight NATURAL JOIN available_seats WHERE Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s AND  Flight_status !="Canceled" and Seats >= %s'
	cursor.execute(get_flight_data, (Departure_Airport,Departure_date, Arrival_Airport,num_tickets))
	data = cursor.fetchall()
	
	if data:
		# storing the number of tickets selected and the Departure date
		session['num_travelers'] = num_tickets
		session['Departure_date']= Departure_date

	cursor.close()
	return render_template('Flight.html', Flight=data)




# The round trip function displays all the departure and return flights avalilable
@app.route('/Roundtrip',  methods=['GET', 'POST'])
def Roundtrip():
	
	error=None
	
	cursor =conn.cursor()
    

	Departure_Airport= request.form['Departure_Airport']
	Arrival_Airport = request.form['Arrival_Airport']
	Departure_date = request.form['departure_date']
	return_date = request.form['return_date']
	num_tickets= int(request.form['num_travelers'])
  
   	# creating a temp view to store all the depatrure flights that are at 80% flight capacity or greater
	get_flight_info='Create View find_flights as (SELECT Flight_Number FROM price_adjust NATURAL JOIN Flight WHERE Departure_Airport = %s AND Departure_date = %s AND Arrival_Airport = %s AND  Seats_Ratio > 0.8)'
	cursor.execute(get_flight_info, (Departure_Airport,Departure_date,Arrival_Airport))
	conn.commit()

    # adjusting the flight of the price if the flight capacity is 80% or more
	set_price= 'UPDATE Flight JOIN find_flights ON Flight.Flight_Number = find_flights.Flight_Number SET BasePrice = BasePrice * 1.25; '
	cursor.execute(set_price)
	conn.commit()

   # deleting the view from the database
	drop_table='DROP VIEW IF EXISTS find_flights'
	cursor.execute(drop_table)
	conn.commit()

	# creating a temp view to store all the depatrure flights that are at 80% flight capacity or greater
	get_flight_info='Create View find_flights as (SELECT Flight_Number FROM price_adjust NATURAL JOIN Flight WHERE Departure_Airport = %s AND Departure_date = %s AND Arrival_Airport = %s AND Seats_Ratio > 0.8)'
	cursor.execute(get_flight_info, (Arrival_Airport,Departure_date, Departure_Airport))
	conn.commit()
    
	 # adjusting the flight of the price if the flight capacity is 80% or more
	set_price= 'UPDATE Flight JOIN find_flights ON Flight.Flight_Number = find_flights.Flight_Number SET BasePrice = BasePrice * 1.25; '
	cursor.execute(set_price)
	conn.commit()
    
    # deleting the view from the database
	drop_table='DROP VIEW IF EXISTS find_flights'
	cursor.execute(drop_table)
	conn.commit()
   
    # Display departure flight
	get_flight_dep = 'SELECT * FROM Flight NATURAL JOIN available_seats WHERE Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s AND  Flight_status !="Canceled" and Seats >= %s'
	cursor.execute(get_flight_dep, (Departure_Airport,Departure_date, Arrival_Airport,num_tickets ))
	flight_dep = cursor.fetchall()
    
	#Display Return Flight
	get_flight_arr= 'SELECT * FROM Flight NATURAL JOIN available_seats WHERE Departure_Airport=%s AND Departure_date=%s AND Arrival_Airport=%s AND  Flight_status !="Canceled" and Seats >= %s'
	cursor.execute(get_flight_arr, (Arrival_Airport,return_date, Departure_Airport,num_tickets ))
	flight_ret = cursor.fetchall()
     
		
   
	if flight_dep and flight_ret:
		# storing the number of tickets selected and the Departure date
		session['num_travelers'] = num_tickets
		session['Departure_date'] = Departure_date
		session['Return_date'] = return_date
		
	cursor.close()
	return render_template('FlightR.html', DFlight=flight_dep, RFlight=flight_ret, error=error)



# Finds the flight status for a flight 
@app.route('/FlightStatus',  methods=['GET', 'POST'])
def FlightStatus():
	
	cursor =conn.cursor()

	airline_name= request.form['Airline_Name']
	flight_num = request.form['Flight_Number']
	arrival_date = request.form['Arrival_date']

    #  Executes query to get the flight status
	get_flight_status = 'SELECT Airline_Name, Flight_Number, Departure_Airport, Departure_date, Arrival_Airport, Flight_status FROM Flight WHERE Airline_Name=%s AND Flight_Number=%s AND Arrival_date=%s'
	cursor.execute(get_flight_status, (airline_name, flight_num, arrival_date))
	data = cursor.fetchone()
	
	cursor.close()


	return render_template('FlightStatus.html', data=data)


# Define route for purchase form
@app.route("/purchase", methods=["POST"])
def purchase():
	
	# if user selects one-way flight
	if 'Select_Flight' in request.form:
		
		select_flight = request.form["Select_Flight"]


		logged_in = session.get('logged_in', False)
	
	   # if not logged in, redirect to login page
		if logged_in==False:
			return redirect(url_for('login'))

			# Converts to Dictionary
		select_flight=yaml.safe_load(select_flight)
	
        # Get the departure time of the selected flight
		Departure_time=str(eval(select_flight['Departure_time']))


       # Set session variables for flight information
		num_tickets=session['num_travelers']
		session['Flight_number'] = select_flight['Flight_Number']
		session['Airline_name'] = select_flight['Airline_Name']
		session['Departure_time']= Departure_time

        # Calculate total amount of purchase
		price = float(select_flight['BasePrice'])
		total_amount= price * num_tickets
		session['price']=price
       
		return render_template('Purchase.html',  num_tickets=num_tickets,total_amount=total_amount)

	# if user selects round-trip flights
	elif 'Dep_Flight' in request.form and 'Ret_Flight' in request.form:
		
		# get departure and return flight information from the form
		dep_flight = request.form["Dep_Flight"]
		ret_flight = request.form["Ret_Flight"]
		
	    
		logged_in = session.get('logged_in', False)
	
		# if not logged in, redirect to login page
		if logged_in==False:
			return redirect(url_for('login'))
		
		# Converts to Dictionary
		dep_flight=yaml.safe_load(dep_flight)
		ret_flight= yaml.safe_load(ret_flight)

		# Get the departure and return times for the selected flights
		Departure_time=str(eval(dep_flight['Departure_time']))
		Return_time=str(eval(ret_flight['Departure_time']))
		
		# Set session variables for flight information
		session['Flight_number'] = dep_flight['Flight_Number']
		session['Airline_name'] = dep_flight['Airline_Name']
		session['Departure_time']= Departure_time

		session['Flight_number2'] = ret_flight['Flight_Number']
		session['Airline_name2'] = ret_flight['Airline_Name']
		session['Return_time']= Return_time

        # Calculate total amount of purchase
		num_tickets=session['num_travelers']
		price= int(dep_flight['BasePrice'])+int(ret_flight['BasePrice'])
		total_amount=price*num_tickets
		price=session['price']

		return render_template('Purchase.html',  num_tickets=num_tickets,total_amount=total_amount)
	
	else:  # if both not selected 
		return redirect(url_for('homepage'))


# This function inserts a purchase into the database
@app.route("/PurchaseAuth",  methods=[ 'GET', 'POST'])
def purchaseAuth():
	
	# if oneway purchase
	if session['Flight_number2']==1:

        #get the session variable values 
		num_tickets = session['num_travelers']
		email=session['username']
		flight_number = session['Flight_number']
		Departure_date =session['Departure_date']
		Airline_name = session['Airline_name']
		Departure_time=session['Departure_time']

		
	
		cursor =conn.cursor()

       # insert all passengers in the purchase table 
		for i in range(num_tickets):
			
			p_fname = request.form.get("First_Name{}".format(i))
			P_lname = request.form.get("Last_Name{}".format(i))
			DOB = request.form.get("DOB{}".format(i))


			name_card = request.form['Card_Name']
			Card_Type = request.form['Card_Type']
			card_number = request.form['Card_Number']
			card_exp= request.form['Card_Expiration']
			final_price= session['price']
			
			# gets the current date
			get_date='Select CURDATE() As Date'
			cursor.execute(get_date)
			Purchase_date=cursor.fetchone()
			
             # gets the current time
			get_time='SELECT CURTIME() As Time'
			cursor.execute(get_time)
			Purchase_time=cursor.fetchone()
		
            # Gets the unique ticket ID from the ticket thats not in the purchase table to insure no duplicates
			get_ticket_number='SELECT Ticket_ID FROM Ticket WHERE Airline_name=%s and flight_Number =%s and Departure_date=%s and Departure_time= %s and Ticket_Id not in (SELECT Ticket_Id FROM Purchase)' 
			cursor.execute(get_ticket_number, (Airline_name,flight_number, Departure_date, Departure_time))
			ticket_id = cursor.fetchone()

		    # insert passengeres into the purchase table 
			insert_Purchase_info = "INSERT INTO Purchase(Customer_Email,Ticket_ID,Passenger_Fname, Passenger_Lname, Passenger_DOB, Final_price, Name_card, Card_number, Card_expiration, Card_type, Purchase_date, Purchase_time) VALUES (%s, %s,%s,%s, %s, %s, %s, %s, %s,%s, %s, %s) "
			cursor.execute(insert_Purchase_info, (email,ticket_id['Ticket_ID'] ,p_fname, P_lname , DOB, final_price, name_card, card_number, card_exp, Card_Type, Purchase_date['Date'], Purchase_time['Time']))
			conn.commit()
	
		cursor.close()

		# Display the total amount for the purchase
		total_amount=final_price*num_tickets

		return redirect(url_for('customer_account'))

	else:  #if round-tripa

		#Creates variables to store the session information
		num_tickets = session['num_travelers']
		email=session['username']
		flight_number = session['Flight_number']
		Departure_date =session['Departure_date']
		Airline_name = session['Airline_name']
		Departure_time=session['Departure_time']
		flight_number2 = session['Flight_number2']
		Return_date =session['Return_date']
		Airline_name2 = session['Airline_name2']
		Return_time =session['Return_time']
		
		cursor =conn.cursor()

		for i in range(num_tickets):
			#gets the purchase info data from the form
			p_fname = request.form.get("First_Name{}".format(i))
			P_lname = request.form.get("Last_Name{}".format(i))
			DOB = request.form.get("DOB{}".format(i))
			name_card = request.form['Card_Name']
			Card_Type = request.form['Card_Type']
			card_number = request.form['Card_Number']
			card_exp= request.form['Card_Expiration']
			final_price= session['price']
			
			#helper to get current date
			get_date='Select CURDATE() As Date'
			cursor.execute(get_date)
			Purchase_date=cursor.fetchone()
			
			#helper to get current time
			get_time='SELECT CURTIME() As Time'
			cursor.execute(get_time)
			Purchase_time=cursor.fetchone()
			
			#executes query that fetches an available ticket number to purchase for the departure flight
			get_ticket_number='SELECT Ticket_ID FROM Ticket WHERE Airline_name=%s and flight_Number =%s and Departure_date=%s and Departure_time= %s and Ticket_Id not in (SELECT Ticket_Id FROM Purchase)' 
			cursor.execute(get_ticket_number, (Airline_name,flight_number, Departure_date, Departure_time))
			ticket_id = cursor.fetchone()
		
			#executes query to insert (buy) tickets for customer departure
			insert_Purchase_info = "INSERT INTO Purchase(Customer_Email,Ticket_ID,Passenger_Fname, Passenger_Lname, Passenger_DOB, Final_price, Name_card, Card_number, Card_expiration, Card_type, Purchase_date, Purchase_time) VALUES (%s, %s,%s,%s, %s, %s, %s, %s, %s,%s, %s, %s) "
			cursor.execute(insert_Purchase_info, (email,ticket_id['Ticket_ID'] ,p_fname, P_lname , DOB, float(final_price), name_card, card_number, card_exp, Card_Type, Purchase_date['Date'], Purchase_time['Time']))
			conn.commit()

            #executes query that fetches an available ticket number for the  purchase for the return flight
			get_ticket_number2='SELECT Ticket_ID FROM Ticket WHERE Airline_name=%s and flight_Number =%s and Departure_date=%s and Departure_time= %s and Ticket_Id not in (SELECT Ticket_Id FROM Purchase)' 
			cursor.execute(get_ticket_number2, (Airline_name2,flight_number2, Return_date, Return_time))
			ticket_id2 = cursor.fetchone()
		
			#executes query to insert (buy) tickets for customer for the return flight
			insert_Purchase_info2 = "INSERT INTO Purchase(Customer_Email,Ticket_ID,Passenger_Fname, Passenger_Lname, Passenger_DOB, Final_price, Name_card, Card_number, Card_expiration, Card_type, Purchase_date, Purchase_time) VALUES (%s, %s,%s,%s, %s, %s, %s, %s, %s,%s, %s, %s) "
			cursor.execute(insert_Purchase_info2, (email,ticket_id2['Ticket_ID'] ,p_fname, P_lname , DOB, float(final_price), name_card, card_number, card_exp, Card_Type, Purchase_date['Date'], Purchase_time['Time']))
			conn.commit()
	
		cursor.close()
		total_amount=final_price*num_tickets

	return redirect(url_for('customer_account'))
	


#function for displaying customer info and show spending info
@app.route("/CustomerA",methods=['GET', 'POST'])
def customer_account():
	username = session['username']
	cursor =conn.cursor()

	try:
		#executes query that shows all customer attributes
		Customer_Query= 'SELECT * FROM Customer WHERE Customer_Email = %s'
		cursor.execute(Customer_Query,(username))
		data = cursor.fetchone()

		#executes query that shows customer total spent past year
		TrackSpending_QueryYear = 'SELECT SUM(Final_price) as Year_Money FROM Purchase WHERE (YEAR(Purchase_date) <= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)) and (Customer_Email = %s)'
		cursor.execute(TrackSpending_QueryYear,(username))
		money1 = cursor.fetchone()

		#executes query that shows customer total spent past year divided by months
		TrackSpending_QueryMonth = 'SELECT YEAR(Purchase_date) AS year, MONTH(Purchase_date) AS month, SUM(Final_price) AS total_spent FROM Purchase WHERE Purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) and Customer_Email = %s GROUP BY YEAR(Purchase_date), MONTH(Purchase_date) ORDER BY YEAR(Purchase_date) DESC, MONTH(Purchase_date) DESC;'
		cursor.execute(TrackSpending_QueryMonth,(username))
		money2 = cursor.fetchall()
		cursor.close()
		return render_template('CustomerAccount.html',username=username, data=data, money1 = money1, money2=money2)

	except Exception as e:
		conn.rollback()
		error = str(e)
		return render_template('CustomerAccount.html', error=error)
    
	finally:
		cursor.close()
		return render_template('CustomerAccount.html',username=username, data=data, money1 = money1, money2=money2)


#function that gets data and executes queries to display spending info for customer based on range of dates
@app.route('/TrackSpending', methods=['GET', 'POST'])
def TrackSpending():

	#gets info for range of dates from form
	email = session['username']
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	#executes query for display spending info total
	cursor = conn.cursor()
	get_total = 'SELECT SUM(Final_price) as Year_Money FROM Purchase WHERE (Purchase_date  > %s) and (Purchase_date  < %s) and (Customer_Email = %s)'
	cursor.execute(get_total, (start_date, end_date, email))
	total =cursor.fetchone()


	#executes query for display spending info monthly division
	get_monthly = 'SELECT YEAR(Purchase_date) AS year, MONTH(Purchase_date) AS month, SUM(Final_price) AS total_spent FROM Purchase WHERE (Purchase_date  > %s) and (Purchase_date  < %s) and (Customer_Email = %s) GROUP BY YEAR(Purchase_date), MONTH(Purchase_date) ORDER BY YEAR(Purchase_date) DESC, MONTH(Purchase_date) DESC;'
	cursor.execute(get_monthly, (start_date, end_date, email))
	monthly_money =cursor.fetchall()

	cursor.close()


	return render_template('TrackSpending_Page.html', total=total, monthly_money=monthly_money)



#function that executes queries to display past and future flights for customer 
@app.route("/FlightInfo",methods=['GET', 'POST'])
def get_flight_info():
    
	email = session['username']
	cursor =conn.cursor()
	
	#executes queries for fetching future flights
	get_future_flight= "SELECT Ticket_ID, Airline_Name, Flight_Number,Departure_Airport,Departure_date,Arrival_Airport, Arrival_date, Passenger_Fname, Passenger_Lname, final_price, Flight_status FROM Purchase NATURAL JOIN Ticket NATURAL JOIN Flight WHERE Customer_Email = %s and Departure_date > CURRENT_DATE"
	cursor.execute(get_future_flight,(email))
	future_flights= cursor.fetchall()

	#executes queries for fetching past flights
	get_past_flight= "SELECT Ticket_ID, Airline_Name, Flight_Number,Departure_Airport,Departure_date, Departure_time, Arrival_Airport, Arrival_date, Passenger_Fname, Passenger_Lname, final_price, Flight_status FROM Purchase NATURAL JOIN Ticket NATURAL JOIN Flight WHERE Customer_Email = %s and Departure_date < CURRENT_DATE"
	cursor.execute(get_past_flight,(email))
	past_flights= cursor.fetchall()

	cursor.close()

	return render_template('Flightinfo.html', future_flights=future_flights, past_flights=past_flights)


#function for cancelling  previous flights
@app.route("/cancelFlight",methods=['GET', 'POST'])
def cancelFlight():

	
	if 'Cancel1' in request.form:	#checks which flight is selected by radio button
		cursor =conn.cursor()
		cancel = request.form['Cancel1']
		cancel=yaml.safe_load(cancel)

		ticketID= cancel['Ticket_ID']

		# Check if if flight is in 24 hours 
		check_date = "Select Flight_Number From Flight Natural Join Ticket where Ticket_ID=%s And Flight_Number not in (Select Flight_Number From Flight Where Departure_date > DATE_ADD(NOW(), INTERVAL 24 HOUR))"
		cursor.execute(check_date, (ticketID))
		data = cursor.fetchall()

		
		if ( len(data) == 0):#if not in 24 hours delete from purchases and return to available tickets
			drop_flight='delete from purchase where Ticket_ID=%s'
			cursor.execute(drop_flight,(ticketID))
			conn.commit()
			cursor.close()
		
		else:# if within 24 hours dont delete
			redirect(url_for('customer_account'))

		return redirect(url_for('get_flight_info'))
	
	else:
		return redirect(url_for('customer_account'))


#function for rating and commenting on pastflights
@app.route("/Feedback",methods=['GET', 'POST'])
def Feedback():
	
	cursor =conn.cursor()
	
	#data for inserting  the feedback
	Customer_email=session['username']
	PastFlight= request.form['PastFlight']
	dateF=request.form['Date']
	Rating=request.form['Rating']
	Comment= request.form['Comment']

	#isoolate correct data from form
	PastFlight=yaml.safe_load(PastFlight)
	Departure_time=str(eval(PastFlight['Departure_time']))

	#Executes query for inserting ratings and comments
	insert_experience="Insert into Experiences (Airline_Name,Flight_Number, Departure_date, Departure_time, Customer_Email, flight_rating, flight_feedback) VALUES(%s,%s,%s,%s,%s,%s,%s)"
	cursor.execute(insert_experience,(PastFlight['Airline_Name'], PastFlight['Flight_Number'], dateF, Departure_time, Customer_email,Rating, Comment))
	conn.commit()
		
	cursor.close()

	return redirect(url_for('customer_account'))

#function for staff account page display
@app.route('/stafflogedIn')
def stafflogedIn():

	username = session['username']

	cursor =conn.cursor()

	try:
		#execute query to fetch all staff info for display
		query= 'SELECT * FROM Staff WHERE Username = %s'
		cursor.execute(query,(username))
		data = cursor.fetchone()
		

	except Exception as e:	#exception for if staff doesnt exist
		conn.rollback()
		error = str(e)
		return render_template('StaffAccount.html', error=error)
    
	finally:
		cursor.close()
		return render_template('StaffAccount.html',username=username, data=data)


#function for displaying  some flight info and have forms to search for other info
@app.route('/viewFlight')
def viewFlight():
	
	username = session['username']
	Airline_name=session['Airline_Name']
	
	cursor =conn.cursor()

	#query for next  30 day flights
	get_flight_month='SELECT * FROM Flight natural join Staff WHERE Airline_Name= %s and departure_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)'
	cursor.execute(get_flight_month,(Airline_name))
	Flight=cursor.fetchall()

	#values for forms (airports)
	select_Departure_Airport= 'SELECT DISTINCT Departure_Airport FROM Flight WHERE  Airline_Name = %s'
	cursor.execute(select_Departure_Airport, (Airline_name))
	list_Departure_Airport= cursor.fetchall()
	select_Arrival_Airport = 'SELECT DISTINCT Arrival_Airport FROM Flight WHERE  Airline_Name = %s'
	cursor.execute(select_Arrival_Airport, (Airline_name))
	list_Arrival_Airport= cursor.fetchall()

	#values for forms (flight numbers)
	select_flight_number = 'SELECT DISTINCT flight_number FROM Flight Where Airline_Name = %s'
	cursor.execute(select_flight_number,Airline_name)
	list_flight_number= cursor.fetchall()

	cursor.close()

	return render_template('viewFlight.html', Flight=Flight, Departure=list_Departure_Airport, Arrival=list_Arrival_Airport, Flight_num=list_flight_number)


#function for displaying flights between range of dates
@app.route('/searchFlight', methods=['GET', 'POST'])
def searchFlight():
	
	Airline_name=session['Airline_Name']

    # Retrieve the search parameters for flight search
	departure_airport = request.form['Departure_Airport']
	arrival_airport = request.form['Arrival_Airport']
	start_date = request.form['start_date']
	end_date = request.form['end_date']

    # Query the database with the search parameters for displaying flights
	cursor = conn.cursor()
	query = "SELECT * FROM Flight WHERE Airline_Name=%s  AND Departure_Airport = %s AND Arrival_Airport = %s AND Departure_date >= %s AND Departure_date <= %s"
	cursor.execute(query, (Airline_name,departure_airport, arrival_airport, start_date,end_date))
	results = cursor.fetchall()

	cursor.close()

    # Render the results in the template
	return render_template('searchResults.html', Flight=results)


#function for displaying customers of specific  flight
@app.route('/listCustomers', methods=['POST'])
def listCustomers():
	
	#gets  specific flight
	Flight_Number = request.form['Flight_Number']
	Airline_name= session['Airline_Name']
	
	cursor = conn.cursor()
	
	#executes query for displaying the customers
	get_customer='SELECT DISTINCT Flight_Number, Customer_Email FROM Purchase Natural Join Ticket Natural Join Flight natural join Staff WHERE Airline_Name= %s and Flight_Number=%s '
	cursor.execute(get_customer, (Airline_name, Flight_Number ))
	data=cursor.fetchall()

	cursor.close()


	return render_template('ListCustomers.html', data=data)


#function to route CHANGE STATUS AND fetches database info for form options (flights)
@app.route('/ChangeStatus')
def changeFlightStatus():
	Airline_name=session['Airline_Name']
	cursor = conn.cursor()

	#gets flights for form
	get_Flight_number='Select Flight_Number From Flight Where Airline_Name=%s'
	cursor.execute(get_Flight_number, (Airline_name))
	Flight_number= cursor.fetchall()
	
	cursor.close()

	return render_template('ChangeStatus.html', Flight_num=Flight_number)


#function to CHANGE STATUS by staff
@app.route('/UpdateStatus', methods=['POST'])
def UpdateStatus():
	
	
	Airline_name=session['Airline_Name']
	Flight= request.form['Flight_Number']
	
	#gets status for update from user
	new_status = request.form['Flight_status']

	cursor = conn.cursor()

	#gets flight numbers
	get_Flight_number='Select Flight_Number From Flight Where Airline_Name=%s'
	cursor.execute(get_Flight_number, (Airline_name))
	Flight_number= cursor.fetchall()

	#executes update  status query
	update_status='Update Flight Set Flight_status = %s Where Flight_Number = %s'
	cursor.execute(update_status, (new_status, Flight))
	conn.commit()
	cursor.close()
	
	return render_template('ChangeStatus.html', Flight_num=Flight_number)

	

	
#function to route create airplane fetches database info for form options
@app.route('/createflight')
def createflight():
	
	cursor =conn.cursor()
	
	#gets values from the database for form options (AIRBUS)
	select_Airbus='SELECT airbus FROM Airplane where 1'
	cursor.execute(select_Airbus)
	list_Airbus=cursor.fetchall()

	#gets values from the database for form options (AIRLINES)
	select_airline='SELECT * FROM Airline'
	cursor.execute(select_airline)
	list_airline=cursor.fetchall()

	#gets values from the database for form options (AIRPORT  ID)
	select_airportID='SELECT Airport_ID FROM Airport'
	cursor.execute(select_airportID)
	list_airportID=cursor.fetchall()

	#gets values from the database for form options (AIRPORT NAMES)
	select_airportName='SELECT Airport_Name FROM Airport'
	cursor.execute(select_airportName)
	list_airportName=cursor.fetchall()

	

	cursor.close()

	return render_template('createflight.html', Airline =list_airline, Airbus_N =list_Airbus,  Airport=list_airportID, Airport_D=list_airportName,Airport_A=list_airportName)


#function to create flight
@app.route('/insertFlight', methods=['GET', 'POST'])
def insertFlight():

	#get new flight info
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

	#execute query to add the flight
	cursor =conn.cursor()
	query = "INSERT INTO Flight (Airport_ID, Airbus,Airline_Name, Flight_Number, Departure_date, Departure_time, Departure_Airport, Arrival_time, Arrival_date, Arrival_Airport, BasePrice, Flight_status) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
	cursor.execute(query,(Airport_ID, airbus, Airline_Name, Flight_Number, departure_date, departure_time, departure_airport,arrival_time,arrival_date, arrival_airport, base_price, status))
	conn.commit() 
    
	
	# get the number of seats for the flight
	get_seats= 'SELECT Seats FROM Airplane Where Airbus=%s'
	cursor.execute(get_seats,(airbus))
	seats = cursor.fetchone()
	seats1 = int(seats['Seats'])

	ticketBase=Airline_Name+ Flight_Number
    
	# loop to Auto genrate a ticket_ID 
	for i in range (seats1):
		ticket_id= ticketBase +str(i)
		#query execution to add tickets
		insert_ticket='INSERT INTO Ticket (Ticket_ID, Airline_Name, Flight_Number, Departure_date, Departure_time) Values (%s, %s, %s, %s, %s)'
		cursor.execute(insert_ticket,(ticket_id, Airline_Name, Flight_Number, departure_date, departure_time))
		conn.commit() 
	
	cursor.close()

	return redirect(url_for('createflight'))

#function to create airplane and displays existing airplanes owned by airline
@app.route('/createAirplane')
def createAirplane():
	cursor =conn.cursor()

	Airline_name=session['Airline_Name']
	
	#query execution displays existing airplanes owned by airline
	get_Airplane= "Select * from Airplane where Airline_Name=%s"
	cursor.execute(get_Airplane, (Airline_name))
	Airplane = cursor.fetchall()
    
	#query execution to get airlines in database for the form inputs
	get_Airlines = "Select Airline_Name from Airline"
	cursor.execute(get_Airlines)
	Airlines= cursor.fetchall()
	cursor.close()

	return render_template('createAirplane.html', data=Airplane,Airlines= Airlines)


#create and insert airplane into database function
@app.route('/insertAirplane', methods=['GET', 'POST'])
def insertAirAirplane():

	#get new airplane info
	# Airline_Name2 = session['Airline_Name']
	Airline_Name= request.form['Airline_Name']
	airbus= request.form['airbus']
	seats= request.form['seats']
	manufacturer= request.form['manufacturer']
	Manufacture_date= request.form['Manufacture_date']
	
	#execute query to add the airport
	cursor = conn.cursor()
	query = "INSERT INTO Airplane (Airline_Name, airbus, seats, Manufacture, Manufacture_date ) VALUES (%s, %s,%s, %s, %s)"
	cursor.execute(query,(Airline_Name, airbus, seats,manufacturer,Manufacture_date))
	conn.commit()

	# #query execution displays existing airplanes owned by airline
	# get_Airplane= "Select * from Airplane where Airline_Name=%s"
	# cursor.execute(get_Airplane, (Airline_Name2))
	# Airplane= cursor.fetchall()

	cursor.close()


	return redirect(url_for('createAirplane'))
	#return render_template('createAirplane.html')

#define rout for creating airport
@app.route('/createAirport')
def createAirport():
	return render_template('createAirport.html')


#create and insert airport into database function
@app.route('/insertAirport', methods=['GET', 'POST'])
def insertAirport():
	
	#get new airport info
	Airport_ID= request.form["Airport_ID"]
	Airport_Name= request.form["Airport_Name"]
	Airport_City= request.form["Airport_City"]
	Airport_Country= request.form["Airport_Country"]
	Airport_Type= request.form["Airport_Type"]
	
	#execute query to add the airport
	cursor =conn.cursor()
	query = "INSERT INTO Airport (Airport_ID, Airport_Name, Airport_City, Airport_Country, Airport_Type ) VALUES (%s, %s,%s, %s, %s)"
	cursor.execute(query,(Airport_ID, Airport_Name, Airport_City, Airport_Country, Airport_Type))
	conn.commit()
	cursor.close()

	# return render_template('createAirport.html')
	return redirect(url_for('createAirport'))

# staff stats function and routing to display ratings,revenue info, and customer info, and links to staff specific searches
@app.route('/Stats')
def Stats():

	#executes query to get the flight ratings and comments
	cursor =conn.cursor()
	get_flight_ratings = 'SELECT Flight_Number, Airline_Name, AVG(flight_rating) AS avg_rating, GROUP_CONCAT(flight_feedback SEPARATOR "/" ) AS comments FROM Experiences GROUP BY Flight_Number, Airline_Name'
	cursor.execute(get_flight_ratings)
	flight_ratings= cursor.fetchall()

	#executes query to get the most frequent customer
	get_frequent = 'SELECT Customer_Email, COUNT(*) As Ticket_count FROM Purchase GROUP BY Customer_Email ORDER BY Ticket_count DESC LIMIT 1;'
	cursor.execute(get_frequent)
	frequent= cursor.fetchone()


	#executes queries to get last months and years revenue info
	get_month = 'SELECT MONTH(Purchase_date) As month, SUM(Final_Price) As Final FROM Purchase GROUP by month HAVING month =MONTH(DATE_SUB(CURRENT_DATE(),INTERVAL 1 MONTH))'
	cursor.execute(get_month)
	month= cursor.fetchone()
	
	get_year = 'SELECT YEAR(Purchase_date) As year, SUM(Final_Price) As Final FROM Purchase GROUP by year HAVING year =YEAR(DATE_SUB(CURRENT_DATE(),INTERVAL 1 YEAR))'
	cursor.execute(get_year)
	year = cursor.fetchone()

	#gets values from the database for form options (Customers)
	get_customer_email= "Select Customer_Email From Purchase"
	cursor.execute(get_customer_email)
	Customer_Email = cursor.fetchall()

	#gets values from the database for form options (Airlines)
	get_Airline= "Select DISTINCT Airline_Name From Purchase NATURAL Join Ticket"
	cursor.execute(get_Airline)
	Airline = cursor.fetchall()
	
	cursor.close()

	return render_template('StaffStats.html', flight_info= flight_ratings, frequent=frequent, lyear=year, lmonth=month, Customer_Email=Customer_Email, Airline=Airline)


# staff customer search function and routing to display particular customer's flights for an airline
@app.route('/staffCustomerS',  methods=['GET', 'POST'])
def staffCustomerS():
    #gets airline and customer email
	Customer_Email= request.form['Customer_Email']
	Airline_Name= request.form["Airline_Name"]
	
	#executes query to display customer flights
	cursor =conn.cursor()
	get_Customer_flights= 'SELECT Flight_Number, Departure_date, Departure_time FROM Purchase Natural JOIN Ticket WHERE Customer_Email =%s and Airline_Name = %s'
	cursor.execute(get_Customer_flights, (Customer_Email, Airline_Name))
	CustomerFlights=cursor.fetchall()
	cursor.close()

	return render_template('StaffSearchCustomer.html', CustomerFlights=CustomerFlights)


# staff reports search function and routing to display all ticket sales information
@app.route('/staffReportS', methods=['GET', 'POST'])
def staffReportS():
	#gets range of dates from the form
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	#executes query to display ticket report
	cursor = conn.cursor()
	get_reports = 'SELECT count(Ticket_ID) as Ticket_Amount FROM Purchase WHERE (Purchase_date > %s) and (Purchase_date < %s)'
	cursor.execute(get_reports, (start_date, end_date))
	Reports =cursor.fetchone()
	cursor.close()

	return render_template('TicketsReportsPage.html', Reports = Reports, start_date=start_date, end_date=end_date)



		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)