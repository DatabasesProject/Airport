# Air Ticket Reservation Web Application

Welcome to the Air Ticket Reservation Web Application! This application is designed to facilitate the reservation and booking of air tickets for various flights. It provides a user-friendly interface for customers to search for flights, purchase tickets, and view important flight information. The system also streamlines the operations for airline staff, allowing them to manage flight statuses and ensure a smooth travel experience.

![My Image](https://raw.githubusercontent.com/JackShkifati28/Air-Ticket-Reservation/main/Images/Homepage.png)

## Tools and Technologies Used

The Air Ticket Reservation Web Application utilizes the following tools and technologies:

### Front-end:
- HTML: Used for creating the structure and layout of web pages.
- CSS: Employed for styling the web pages and enhancing the visual presentation.

### Back-end:
- Python Flask: Serves as the core framework for building the server-side logic and handling requests and responses.
- MySQL: Employed as the relational database management system for efficient data storage and retrieval.

These tools and technologies enable the development of a dynamic and interactive web application, ensuring a seamless user experience for customers. The integration with MySQL allows for reliable data management, while Python Flask facilitates efficient server-side processing.

## ER Diagram

The ER (Entity-Relationship) diagram represents the conceptual model of the Air Ticket Reservation Web Application. It illustrates the entities involved in the system, their attributes, and the relationships between them. The ER diagram provides a visual representation of the database structure and serves as a basis for designing the relational schema.

![My Image](https://raw.githubusercontent.com/JackShkifati28/Air-Ticket-Reservation/main/Images/ER-Diagram.png)


## Relational Diagram

The Relational Diagram showcases the design of the database schema for the Air Ticket Reservation Web Application. It depicts the tables and their attributes, as well as the primary and foreign key relationships between the tables. The Relational Diagram provides a clear understanding of the database structure and aids in database management and query optimization.

![My Image](https://raw.githubusercontent.com/JackShkifati28/Air-Ticket-Reservation/main/Images/R-diagram.png)

## Website Features

### Home Page (Not Logged-in)

When the user is not logged in, the following features should be available on the home page:

- **View Public Info**:
  - Users, whether logged in or not, can search for future flights based on source city/airport name, destination city/airport name, and departure date for one-way trips (departure and return dates for round trips).
  - Users can also view flight status based on airline name, flight number, and arrival/departure date.

- **Register**:
  - Two types of user registrations (Customer and Airline Staff) are available via registration forms as mentioned in Part 1 of the project description.

- **Login**:
  - Two types of user login (Customer and Airline Staff) are available.
  - Users enter their username (email address will be used as the username for customers) and password via login forms.
  - The login authentication component checks the entered credentials against the corresponding user's table:
    - If the login is successful, a session is initiated with the user's username stored as a session variable. Optionally, other session variables can also be stored. Control is redirected to a component that displays the user's home page.
    - If the login is unsuccessful, a message is displayed indicating the login failure.

Once a user has successfully logged in, the reservation system should display their respective home page based on the user's role. Additionally, after executing other actions or sequences of related actions, control will return to the component that displays the home page. If the previous action was unsuccessful, the home page should display an error message.

### Customer Use Cases

After successfully logging in as a customer, the user may perform the following use cases:

- **View My Flights**:
  - Customers can view their purchased flight information, with various filtering options available, such as specifying a range of dates or specifying the destination and/or source airport name or city name.

- **Search for Flights**:
  - Customers can search for future flights (one-way or round trip) based on source city/airport name, destination city/airport name, and departure or return dates.

- **Purchase Tickets**:
  - Customers can choose a flight and purchase tickets, providing all the necessary data via forms. This use case can be implemented along with the "Search for Flights" use case.

- **Cancel Trip**:
  - Customers can cancel a purchased ticket for a flight that will take place more than 24 hours in the future. After cancellation, the ticket will no longer belong to the customer and will become available for purchase by other customers.

- **Give Ratings and Comment on Previous Flights**:
  - Customers can rate and comment on their previous flights for which they purchased tickets and have already taken the flights.

- **Track My Spending**:
  - The default view displays the total amount of money spent in the past year and a bar chart/table showing month-wise money spent for the last 6 months.
  - Customers also have the option to specify a range of dates to view the total amount of money spent within that range, along with a bar chart/table showing month-wise money spent within the specified range.

- **Logout**:
  - The session is destroyed, and a "goodbye" page or the login page is displayed.

### Airline Staff Use Cases

After successfully logging in as an airline staff member, the user may perform the following use cases:

- **View Flights**:
  - The default view shows all future flights operated by the airline the staff member works for in the next 30 days.
  - Airline staff can view all current, future, and past flights operated by their airline based on a range of dates, source/destination airports, city, etc.
  - Airline staff can also view all the customers of a particular flight.

- **Create New Flights**:
  - Airline staff can create a new flight by providing all the necessary data via forms. Unauthorized users should be prevented from performing this action.
  - The default view shows all future flights operated by the airline the staff member works for in the next 30 days.

- **Change Status of Flights**:
  - Airline staff can change the status of a flight (e.g., from on-time to delayed or vice versa) via forms.

- **Add Airplane in the System**:
  - Airline staff can add a new airplane to the system by providing all the necessary data via forms. Unauthorized users should be prevented from performing this action.
  - On the confirmation page, staff members can view all the airplanes owned by the airline they work for.

- **Add New Airport in the System**:
  - Airline staff can add a new airport to the system by providing all the necessary data via forms. Unauthorized users should be prevented from performing this action.

- **View Flight Ratings**:
  - Airline staff can view each flight's average ratings and all the comments and ratings given by customers for that flight.

- **View Frequent Customers**:
  - Airline staff can view the most frequent customer within the last year.
  - Additionally, airline staff can see a list of all flights a particular customer has taken on their airline only.

- **View Reports**:
  - Airline staff can view total amounts of tickets sold based on a range of dates (e.g., last year, last month).
  - Airline staff can also view month-wise ticket sales in a bar chart/table.

- **View Earned Revenue**:
  - Airline staff can view the total amount of revenue earned from ticket sales in the last month and last year.

- **Logout**:
  - The session is destroyed, and a "goodbye" page or the login page is displayed.



