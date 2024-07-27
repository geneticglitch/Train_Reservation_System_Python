import pymysql
import time
import random
# ----------------Color print function----------------


import time


def printcolor(text, color, sleeptime=0.15):
    # --Color Start--
    COLOR_RED = "\033[31m"
    COLOR_GREEN = "\033[32m"
    COLOR_YELLOW = "\033[33m"
    COLOR_BLUE = "\033[34m"
    COLOR_MAGENTA = "\033[35m"
    COLOR_RESET = "\033[0m"
    # -- Color End--

    color_code = COLOR_RESET  # Default color code

    if color == "red":
        color_code = COLOR_RED
    elif color == "green":
        color_code = COLOR_GREEN
    elif color == "yellow":
        color_code = COLOR_YELLOW
    elif color == "blue":
        color_code = COLOR_BLUE
    elif color == "magenta":
        color_code = COLOR_MAGENTA


    print(color_code + text + COLOR_RESET)
    time.sleep(sleeptime)

# ----------------Color print function----------------


# Establish connection
printcolor("Establishing connection to database...", "yellow")
try:
    cnx = pymysql.connect(
        host='localhost',
        user='root',
        password='PASSWORD',
    )
    cursor = cnx.cursor()
    time.sleep(1)
    printcolor("Connection established.", "green")

    try:
        try:
            #check for database first
            printcolor("Checking for database...", "yellow", 1)
            cursor.execute("USE indianrailways")
            printcolor("Database exists.", "green", 0.5)
        except:
            #create database
            printcolor("Error database does not exist", "red",0.5)
            printcolor("Creating database...", "yellow",0.5)
            cursor.execute("CREATE DATABASE indianrailways")
            cursor.execute("USE indianrailways")
            printcolor("Database created successfully.", "green", 0.7)
        printcolor("Checking for tables...", "yellow", 1)
        cursor.execute("SELECT * FROM trains")
        cursor.execute("SELECT * FROM stops")
        cursor.execute("SELECT * FROM coaches")
        cursor.execute("SELECT * FROM users")
        cursor.execute("SELECT * FROM bookings")
        cursor.execute("SELECT * FROM seats")
        printcolor("Tables exist.", "green", 0.5)
    except:
        def createtable():
            create_tables = [
                """
                CREATE TABLE IF NOT EXISTS Trains (
                    TrainID INT PRIMARY KEY AUTO_INCREMENT,
                    TrainName VARCHAR(50)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Stops (
                    StopID INT PRIMARY KEY AUTO_INCREMENT,
                    TrainID INT,
                    StopName VARCHAR(50),
                    ArrivalTime TIME,
                    DepartureTime TIME,
                    FOREIGN KEY (TrainID) REFERENCES Trains (TrainID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Coaches (
                    CoachID INT PRIMARY KEY AUTO_INCREMENT,
                    TrainID INT,
                    CoachName VARCHAR(50),
                    Capacity INT,
                    RemainingSeats INT,
                    FOREIGN KEY (TrainID) REFERENCES Trains (TrainID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Users (
                    UserID INT PRIMARY KEY AUTO_INCREMENT,
                    UserName VARCHAR(50),
                    Password VARCHAR(100),
                    DateOfBirth DATE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Bookings (
                    BookingID INT PRIMARY KEY AUTO_INCREMENT,
                    PNRNumber VARCHAR(10),
                    UserID INT,
                    TrainID INT,
                    CoachID INT,
                    PickupStopID INT,
                    DropStopID INT,
                    BookingDate DATETIME,
                    FOREIGN KEY (UserID) REFERENCES Users (UserID),
                    FOREIGN KEY (TrainID) REFERENCES Trains (TrainID),
                    FOREIGN KEY (CoachID) REFERENCES Coaches (CoachID),
                    FOREIGN KEY (PickupStopID) REFERENCES Stops (StopID),
                    FOREIGN KEY (DropStopID) REFERENCES Stops (StopID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Seats (
                    SeatID INT PRIMARY KEY AUTO_INCREMENT,
                    CoachID INT,
                    SeatNumber VARCHAR(10),
                    IsAvailable BOOLEAN,
                    BookingID INT,
                    FOREIGN KEY (CoachID) REFERENCES Coaches (CoachID),
                    FOREIGN KEY (BookingID) REFERENCES Bookings (BookingID)
                )
                """
            ]
            for table in create_tables:
                cursor.execute(table)
                cnx.commit()
                printcolor("Table created successfully.", "green", 0.7)

        printcolor("Error tables do not exist", "red")
        printcolor("Creating Tables...", "yellow")
        createtable()

    printcolor("Continuing...To...MainMenu", "green", 0.8)
except Exception as e:
    printcolor("Connection failed -- .", "red")
    print(e)
    printcolor("Exiting...", "red")
    exit()

cursor = cnx.cursor()


# ----------------------------User-------------------------
def dashboard(user_id, user_name):
    def book_ticket(user_id, user_name):
        printcolor("BOOK TICKET", "blue")
        printcolor("List of trains", "yellow")
        listing_trains()
        train_id = int(input("Enter Train ID : "))
        query = "SELECT * FROM stops WHERE TrainID="+str(train_id)
        cursor.execute(query)
        stops = cursor.fetchall()
        printcolor("Stops", "yellow")
        for stop in stops:
            printcolor(str(stop[0])+" : "+stop[2]+" : " +
                       str(stop[3])+" - "+str(stop[4]), "green")
        pickup_stop_id = int(input("Enter Pickup Stop ID : "))
        drop_stop_id = int(input("Enter Drop Stop ID : "))
        query = "SELECT * FROM coaches WHERE TrainID="+str(train_id)
        cursor.execute(query)
        coaches = cursor.fetchall()
        for coach in coaches:
            printcolor(str(coach[0])+" : "+coach[2] +
                       " : "+str(coach[4])+" seats", "green")
        coach_id = int(input("Enter Coach ID : "))
        query = "SELECT * FROM coaches WHERE CoachID="+str(coach_id)
        cursor.execute(query)
        coach = cursor.fetchone()
        remaining_seats = coach[4]
        if remaining_seats == 0:
            printcolor("No seats available in this coach", "red")
            return
        else:
            remaining_seats -= 1
            query = "UPDATE coaches SET RemainingSeats=" + \
                str(remaining_seats)+" WHERE CoachID="+str(coach_id)
            cursor.execute(query)
            cnx.commit()

        printcolor("Booking ticket...", "green")
        booking_date = time.strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO bookings(PNRNumber,UserID,TrainID,CoachID,PickupStopID,DropStopID,BookingDate) VALUES(%s,%s,%s,%s,%s,%s,%s)"
        number = random.randint(1000000000, 9999999999)
        number_str = str(number)
        cursor.execute(query, (number_str, user_id, train_id,
                       coach_id, pickup_stop_id, drop_stop_id, booking_date))
        cnx.commit()
        # get booking id and seat the seat booking feild to booking id
        query = "SELECT * FROM bookings WHERE PNRNumber="+str(number_str)
        cursor.execute(query)
        booking = cursor.fetchone()
        booking_id = booking[0]
        query = "SELECT * FROM seats WHERE CoachID=" + \
            str(coach_id)+" AND IsAvailable=1"
        cursor.execute(query)
        seats = cursor.fetchall()
        seat = seats[0]
        seat_id = seat[0]
        query = "UPDATE seats SET IsAvailable=0,BookingID=" + \
            str(booking_id)+" WHERE SeatID="+str(seat_id)
        cursor.execute(query)
        cnx.commit()
        printcolor("REMEMBER THE PNR NUMBER:", "green")
        printcolor("PNR Number : "+number_str, "red")
        printcolor("Ticket booked successfully", "green")
        return

    def cancel_ticket(user_id, user_name):
        printcolor("CANCEL TICKET", "blue")
        printcolor("Enter PNR Number", "yellow")
        pnr_number = input(">")
        query = "SELECT * FROM bookings WHERE PNRNumber="+str(pnr_number)
        cursor.execute(query)
        booking = cursor.fetchone()
        if booking:
            if booking[2] == user_id:
                printcolor("Confirm Cancel Ticket(y/n)", "yellow")
                userinput = input(">")
                if userinput == "y":
                    query = "SELECT * FROM coaches WHERE CoachID=" + \
                        str(booking[4])
                    cursor.execute(query)
                    coach = cursor.fetchone()
                    remaining_seats = coach[4]
                    remaining_seats += 1
                    query = "UPDATE coaches SET RemainingSeats=" + \
                        str(remaining_seats)+" WHERE CoachID="+str(booking[4])
                    cursor.execute(query)
                    cnx.commit()
                    query = "SELECT * FROM seats WHERE BookingID=" + \
                        str(booking[0])
                    cursor.execute(query)
                    seat = cursor.fetchone()
                    seat_id = seat[0]
                    query = "UPDATE seats SET IsAvailable=1,BookingID=NULL WHERE SeatID=" + \
                        str(seat_id)
                    cursor.execute(query)
                    cnx.commit()
                    query = "DELETE FROM bookings WHERE PNRNumber=" + \
                        str(pnr_number)
                    cursor.execute(query)
                    cnx.commit()
                    printcolor("Ticket cancelled successfully", "green")
                    return
                else:
                    printcolor("Ticket not cancelled", "red")
                    return
            else:
                printcolor("You can't cancel this ticket", "red")
                return
        else:
            printcolor("Invalid PNR Number", "red")
            return

    def view_bookings(user_id, user_name):
        printcolor("VIEW BOOKINGS", "blue")
        query = "SELECT * FROM bookings WHERE UserID="+str(user_id)
        cursor.execute(query)
        bookings = cursor.fetchall()
        if bookings:
            printcolor("List of bookings", "yellow")
            for booking in bookings:
                query = "SELECT * FROM trains WHERE TrainID="+str(booking[3])
                cursor.execute(query)
                train = cursor.fetchone()
                query = "SELECT * FROM stops WHERE StopID="+str(booking[5])
                cursor.execute(query)
                pickup = cursor.fetchone()
                query = "SELECT * FROM stops WHERE StopID="+str(booking[6])
                cursor.execute(query)
                drop = cursor.fetchone()
                query = "SELECT * FROM coaches WHERE CoachID="+str(booking[4])
                cursor.execute(query)
                coach = cursor.fetchone()
                printcolor("PNR Number : "+booking[1], "red")
                printcolor("Train Name : "+train[1], "green")
                printcolor(
                    "Pickup Stop : "+pickup[2]+" : "+str(pickup[3])+" - "+str(pickup[4]), "green")
                printcolor(
                    "Drop Stop : "+drop[2]+" : "+str(drop[3])+" - "+str(drop[4]), "green")
                printcolor("Coach Name : " +
                           coach[2]+" : "+str(coach[4])+" seats", "green")
                printcolor("Booking Date : "+str(booking[7]), "green")
                printcolor("----------------------------", "red")
            return
        else:
            printcolor("No bookings found", "red")
            return
    while True:
        printcolor("WELCOME TO DASHBOARD", "blue")
        printcolor("Type 1 - Book Ticket", "green")
        printcolor("Type 2 - Cancel Ticket", "green")
        printcolor("Type 3 - View Bookings", "green")
        printcolor("Type 0 - SIGN OUT", "red")
        userinput = int(input(">"))

        if userinput == 1:
            book_ticket(user_id, user_name)
        elif userinput == 2:
            cancel_ticket(user_id, user_name)
        elif userinput == 3:
            view_bookings(user_id, user_name)
        elif userinput == 0:
            printcolor("BACK TO MAIN MENU", "red")
            break
        else:
            printcolor("INVALID INPUT", "red")
            return


def user():
    def login():
        printcolor("LOGIN", "blue")
        username = input("Enter username : ")
        password = input("Enter password : ")
        cursor.execute(
            "SELECT * FROM users WHERE UserName=%s AND Password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            printcolor("Login Successful", "green")
            printcolor("Welcome "+user[1], "green")
            printcolor("Redirecting to dashboard...", "green")
            time.sleep(1)
            dashboard(user[0], user[1])
            return
        else:
            printcolor("Invalid username or password", "red")
            return

    def create_account():
        printcolor("CREATE ACCOUNT", "blue")
        username = input("Enter username : ")
        password = input("Enter password : ")
        dob = input("Enter date of birth(YYYY-MM-DD) : ")
        try:
            cursor.execute(
                "INSERT INTO users(UserName,Password,DateOfBirth) VALUES(%s,%s,%s)", (username, password, dob))
            cnx.commit()
            printcolor("Account created successfully", "green")
            return
        except:
            printcolor("Error creating account", "red")
            return

    # User Menu Begin
    while True:
        printcolor("WELCOME TO USER MENU", "blue")
        printcolor("Type 1 - Login", "green")
        printcolor("Type 2 - Create Account", "green")
        printcolor("Type 3 - PNR enquiry", "green")
        printcolor("Type 0 - BACK", "red")
        userinput = int(input(">"))

        if userinput == 1:
            login()
        elif userinput == 2:
            create_account()
        elif userinput == 3:
            pnr_enquiry()
        elif userinput == 0:
            printcolor("BACK TO MAIN MENU", "red")
            break
        # User Menu End
# ---------------------User------------------------

# util functions --------------------


def pnr_enquiry():
    printcolor("PNR ENQUIRY", "blue")
    pnr_number = input("Enter PNR Number : ")
    query = "SELECT * FROM bookings WHERE PNRNumber="+str(pnr_number)
    cursor.execute(query)
    booking = cursor.fetchone()
    if booking:
        query = "SELECT * FROM trains WHERE TrainID="+str(booking[3])
        cursor.execute(query)
        train = cursor.fetchone()
        query = "SELECT * FROM stops WHERE StopID="+str(booking[5])
        cursor.execute(query)
        pickup = cursor.fetchone()
        query = "SELECT * FROM stops WHERE StopID="+str(booking[6])
        cursor.execute(query)
        drop = cursor.fetchone()
        query = "SELECT * FROM coaches WHERE CoachID="+str(booking[4])
        cursor.execute(query)
        coach = cursor.fetchone()
        query = "SELECT * FROM seats WHERE BookingID=" + \
            str(booking[0])
        cursor.execute(query)
        seat = cursor.fetchone()
        printcolor("PNR Number : "+booking[1], "red")
        printcolor("Train Name : "+train[1], "green")
        printcolor(
            "Pickup Stop : "+pickup[2]+" : "+str(pickup[3])+" - "+str(pickup[4]), "green")
        printcolor(
            "Drop Stop : "+drop[2]+" : "+str(drop[3])+" - "+str(drop[4]), "green")
        printcolor("Coach Name : " +
                   coach[2]+"", "green")
        printcolor("Seat Number : "+seat[2], "green")
        printcolor("Booking Date : "+str(booking[7]), "green")
        printcolor("----------------------------", "red")
        return
    else:
        printcolor("Invalid PNR Number", "red")
        return


def listing_trains():
    cursor.execute("SELECT * FROM trains")
    trains = cursor.fetchall()
    for train in trains:
        printcolor("----------------", "red")
        printcolor(str(train[0])+" : "+train[1], "green")
        query_stops = "SELECT * FROM stops WHERE TrainID="+str(train[0])
        cursor.execute(query_stops)
        stops = cursor.fetchall()
        for stop in stops:
            printcolor("  "+stop[2]+" : "+str(stop[3]) +
                       " - "+str(stop[4]), "yellow")
        query_coaches = "SELECT * FROM coaches WHERE TrainID="+str(train[0])
        cursor.execute(query_coaches)
        coaches = cursor.fetchall()
        for coach in coaches:
            printcolor("  "+coach[2]+" : "+str(coach[4])+" seats", "megenta")
        printcolor("----------------", "red")
    return


def addstation(train_name, train_id):
    printcolor("Add Station to Train "+train_name, "yellow")
    station_name = input("Enter station name : ")
    arrival_time = input("Enter arrival time(XX:XX) : ")
    departure_time = input("Enter departure time(XX:XX) : ")
    cursor.execute(
        "INSERT INTO stops(StopName,TrainID,ArrivalTime,DepartureTime) VALUES(%s,%s,%s,%s)", (station_name, train_id, arrival_time, departure_time))
    cnx.commit()
    return


def addcoach(train_name, train_id):
    def addseats(coach_id, coach_name, capacity):
        for i in range(1, capacity+1):
            coachname = coach_name+"-"+str(i)
            cursor.execute(
                "INSERT INTO seats(CoachID,SeatNumber,IsAvailable) VALUES(%s,%s,%s)", (coach_id, coachname, 1))
            cnx.commit()
        return
    printcolor("Add Coach to Train "+train_name, "yellow")
    coach_name = input("Enter coach name : ")
    capacity = int(input("Enter capacity : "))
    cursor.execute(
        "INSERT INTO coaches(TrainID,CoachName,Capacity,RemainingSeats) VALUES(%s,%s,%s,%s)", (train_id, coach_name, capacity, capacity))
    cnx.commit()
    printcolor("Coach Ceated Successfully", "green")
    printcolor("Adding Seats to Coach", "yellow")
    printcolor("Please Wait...", "yellow")
    addseats(cursor.lastrowid, coach_name, capacity)
    return

# util functions --------------------


# ---------------------Admin------------------------

def addtrain():

    try:
        # Add Train Start
        printcolor("Add/Create Trains", "yellow")
        train_name = input("Enter train name : ")
        cursor.execute(
            "INSERT INTO trains(trainname) VALUES(%s)", (train_name))
        cnx.commit()
        train_id = cursor.lastrowid  # Retrieve the TrainID of the newly inserted record
        temp = "Train "+train_name+" added successfully." + \
            "Train ID : "+str(train_id)+"\n"
        printcolor(temp, "green")

        # After Train Creation Menu Start
        while True:
            header = "Add Station/Coach to Train "+train_name+" :"
            printcolor(header, "blue")
            printcolor("Type 1 - Add Station", "green")
            printcolor("Type 2 - Add Coach", "green")
            printcolor("Type 0 - BACK", "red")
            userinput = int(input(">"))

            if userinput == 1:
                print("Going...to...adding station")
                time.sleep(0.7)
                addstation(train_name, train_id)
            elif userinput == 2:
                print("Going...to.... adding coach")
                time.sleep(0.7)
                addcoach(train_name, train_id)
            elif userinput == 0:
                printcolor("BACK TO MAIN MENU", "red")
                break
            else:
                printcolor("INVALID INPUT", "red")
                continue
        # After Train Creation Menu End
    except Exception as e:
        printcolor("Error adding train. /// Something when Wrong", "red")
        print(e)
        return


def admin():
    printcolor("WELCOME TO ADMIN MENU", "blue")
    printcolor("Type 1 - Add Train", "green")
    printcolor("Type 2 - List Train", "green")
    printcolor("Type 0 - BACK", "red")
    userinput = int(input(">"))

    if userinput == 1:
        addtrain()
    elif userinput == 2:
        listing_trains()
    elif userinput == 0:
        printcolor("BACK TO MAIN MENU", "red")
    else:
        printcolor("INVALID INPUT", "red")
        return

# ---------------------Admin------------------------


# main menu
while True:
    printcolor("WELCOME TO INDIAN RAILWAYS", "blue")
    printcolor("Type 1 - User", "green")
    printcolor("Type 2 - Admin", "green")
    printcolor("Type 0 - EXIT", "red")
    userinput = int(input(">"))  # user input

    if userinput == 1:
        user()
    elif userinput == 2:
        admin()
    elif userinput == 0:
        printcolor("EXITING...", "red")
        break
    else:
        printcolor("INVALID INPUT", "red")
        continue
