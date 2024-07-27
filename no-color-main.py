import pymysql
import time
import random


# Establish connection
print("Establishing connection to database...")
try:
    cnx = pymysql.connect(
        host='localhost',
        user='root',
        password='aryan2703',
    )
    cursor = cnx.cursor()
    time.sleep(1)
    print("Connection established.")

    try:
        try:
            print("Checking for database...")
            cursor.execute("USE indianrailways")
            print("Database exists.")
        except:
            print("Error database does not exist")
            print("Creating database...")
            cursor.execute("CREATE DATABASE indianrailways")
            cursor.execute("USE indianrailways")
            print("Database created successfully.")
        print("Checking for tables...")
        cursor.execute("SELECT * FROM trains")
        cursor.execute("SELECT * FROM stops")
        cursor.execute("SELECT * FROM coaches")
        cursor.execute("SELECT * FROM users")
        cursor.execute("SELECT * FROM bookings")
        cursor.execute("SELECT * FROM seats")
        print("Tables exist.")
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
                print("Table created successfully.")

        print("Error tables do not exist")
        print("Creating Tables...")
        createtable()

    print("Continuing...To...MainMenu")
except Exception as e:
    print("Connection failed -- .")
    print(e)
    print("Exiting...")
    exit()

cursor = cnx.cursor()


# ----------------------------User-------------------------
def dashboard(user_id, user_name):
    def book_ticket(user_id, user_name):
        print("BOOK TICKET")
        print("List of trains")
        listing_trains()
        train_id = int(input("Enter Train ID : "))
        query = "SELECT * FROM stops WHERE TrainID="+str(train_id)
        cursor.execute(query)
        stops = cursor.fetchall()
        print("Stops", "yellow")
        for stop in stops:
            print(str(stop[0])+" : "+stop[2]+" : " +
                       str(stop[3])+" - "+str(stop[4]))
        pickup_stop_id = int(input("Enter Pickup Stop ID : "))
        drop_stop_id = int(input("Enter Drop Stop ID : "))
        query = "SELECT * FROM coaches WHERE TrainID="+str(train_id)
        cursor.execute(query)
        coaches = cursor.fetchall()
        for coach in coaches:
            print(str(coach[0])+" : "+coach[2] +
                       " : "+str(coach[4])+" seats")
        coach_id = int(input("Enter Coach ID : "))
        query = "SELECT * FROM coaches WHERE CoachID="+str(coach_id)
        cursor.execute(query)
        coach = cursor.fetchone()
        remaining_seats = coach[4]
        if remaining_seats == 0:
            print("No seats available in this coach")
            return
        else:
            remaining_seats -= 1
            query = "UPDATE coaches SET RemainingSeats=" + \
                str(remaining_seats)+" WHERE CoachID="+str(coach_id)
            cursor.execute(query)
            cnx.commit()

        print("Booking ticket...")
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
        print("REMEMBER THE PNR NUMBER:")
        print("PNR Number : "+number_str)
        print("Ticket booked successfully")
        return

    def cancel_ticket(user_id, user_name):
        print("CANCEL TICKET")
        print("Enter PNR Number")
        pnr_number = input(">")
        query = "SELECT * FROM bookings WHERE PNRNumber="+str(pnr_number)
        cursor.execute(query)
        booking = cursor.fetchone()
        if booking:
            if booking[2] == user_id:
                print("Confirm Cancel Ticket(y/n)")
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
                    print("Ticket cancelled successfully")
                    return
                else:
                    print("Ticket not cancelled")
                    return
            else:
                print("You can't cancel this ticket")
                return
        else:
            print("Invalid PNR Number")
            return

    def view_bookings(user_id, user_name):
        print("VIEW BOOKINGS")
        query = "SELECT * FROM bookings WHERE UserID="+str(user_id)
        cursor.execute(query)
        bookings = cursor.fetchall()
        if bookings:
            print("List of bookings")
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
                print("PNR Number : "+booking[1])
                print("Given Name",user_name)
                print("Train Name : "+train[1])
                print(
                    "Pickup Stop : "+pickup[2]+" : "+str(pickup[3])+" - "+str(pickup[4]))
                print(
                    "Drop Stop : "+drop[2]+" : "+str(drop[3])+" - "+str(drop[4]))
                print("Coach Name : " +
                           coach[2]+" : "+str(coach[4])+" seats")
                print("Booking Date : "+str(booking[7]))
                print("----------------------------",)
            return
        else:
            print("No bookings found")
            return
    while True:
        print("WELCOME TO DASHBOARD")
        print("Type 1 - Book Ticket")
        print("Type 2 - Cancel Ticket")
        print("Type 3 - View Bookings")
        print("Type 0 - SIGN OUT")
        userinput = int(input(">"))

        if userinput == 1:
            book_ticket(user_id, user_name)
        elif userinput == 2:
            cancel_ticket(user_id, user_name)
        elif userinput == 3:
            view_bookings(user_id, user_name)
        elif userinput == 0:
            print("BACK TO MAIN MENU")
            break
        else:
            print("INVALID INPUT")
            return


def user():
    def login():
        print("LOGIN")
        username = input("Enter username : ")
        password = input("Enter password : ")
        cursor.execute(
            "SELECT * FROM users WHERE UserName=%s AND Password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            print("Login Successful")
            print("Welcome "+user[1])
            print("Redirecting to dashboard...")
            time.sleep(1)
            dashboard(user[0], user[1])
            return
        else:
            print("Invalid username or password")
            return

    def create_account():
        print("CREATE ACCOUNT")
        username = input("Enter username : ")
        password = input("Enter password : ")
        dob = input("Enter date of birth(YYYY-MM-DD) : ")
        try:
            cursor.execute(
                "INSERT INTO users(UserName,Password,DateOfBirth) VALUES(%s,%s,%s)", (username, password, dob))
            cnx.commit()
            print("Account created successfully")
            return
        except:
            print("Error creating account")
            return

    # User Menu Begin
    while True:
        print("WELCOME TO USER MENU")
        print("Type 1 - Login")
        print("Type 2 - Create Account")
        print("Type 3 - PNR enquiry")
        print("Type 0 - BACK")
        userinput = int(input(">"))

        if userinput == 1:
            login()
        elif userinput == 2:
            create_account()
        elif userinput == 3:
            pnr_enquiry()
        elif userinput == 0:
            print("BACK TO MAIN MENU")
            break
        # User Menu End
# ---------------------User------------------------

# util functions --------------------


def pnr_enquiry():
    print("PNR ENQUIRY")
    pnr_number = input("Enter PNR Number : ")
    query = "SELECT * FROM bookings WHERE PNRNumber="+str(pnr_number)
    cursor.execute(query)
    booking = cursor.fetchone()
    if booking:
        query = "SELECT * FROM users WHERE UserID="+str(booking[2])
        cursor.execute(query)
        user = cursor.fetchone()
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
        print("PNR Number : "+booking[1])
        print("Given Name",user[1])
        print("Train Name : "+train[1])
        print(
            "Pickup Stop : "+pickup[2]+" : "+str(pickup[3])+" - "+str(pickup[4]))
        print(
            "Drop Stop : "+drop[2]+" : "+str(drop[3])+" - "+str(drop[4]))
        print("Coach Name : " +
                   coach[2]+"")
        print("Seat Number : "+seat[2])
        print("Booking Date : "+str(booking[7]))
        print("----------------------------")
        return
    else:
        print("Invalid PNR Number")
        return


def listing_trains():
    cursor.execute("SELECT * FROM trains")
    trains = cursor.fetchall()
    for train in trains:
        print("----------------")
        print(str(train[0])+" : "+train[1])
        query_stops = "SELECT * FROM stops WHERE TrainID="+str(train[0])
        cursor.execute(query_stops)
        stops = cursor.fetchall()
        for stop in stops:
            print("  "+stop[2]+" : "+str(stop[3]) +
                       " - "+str(stop[4]))
        query_coaches = "SELECT * FROM coaches WHERE TrainID="+str(train[0])
        cursor.execute(query_coaches)
        coaches = cursor.fetchall()
        for coach in coaches:
            print("  "+coach[2]+" : "+str(coach[4])+" seats")
        print("----------------")
    return


def addstation(train_name, train_id):
    print("Add Station to Train "+train_name)
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
    print("Add Coach to Train "+train_name)
    coach_name = input("Enter coach name : ")
    capacity = int(input("Enter capacity : "))
    cursor.execute(
        "INSERT INTO coaches(TrainID,CoachName,Capacity,RemainingSeats) VALUES(%s,%s,%s,%s)", (train_id, coach_name, capacity, capacity))
    cnx.commit()
    print("Coach Ceated Successfully")
    print("Adding Seats to Coach")
    print("Please Wait...")
    addseats(cursor.lastrowid, coach_name, capacity)
    return

# util functions --------------------


# ---------------------Admin------------------------

def addtrain():

    try:
        # Add Train Start
        print("Add/Create Trains")
        train_name = input("Enter train name : ")
        cursor.execute(
            "INSERT INTO trains(trainname) VALUES(%s)", (train_name))
        cnx.commit()
        train_id = cursor.lastrowid  # Retrieve the TrainID of the newly inserted record
        temp = "Train "+train_name+" added successfully." + \
            "Train ID : "+str(train_id)+"\n"
        print(temp)

        # After Train Creation Menu Start
        while True:
            header = "Add Station/Coach to Train "+train_name+" :"
            print(header)
            print("Type 1 - Add Station")
            print("Type 2 - Add Coach")
            print("Type 0 - BACK")
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
                print("BACK TO MAIN MENU")
                break
            else:
                print("INVALID INPUT")
                continue
        # After Train Creation Menu End
    except Exception as e:
        print("Error adding train. /// Something when Wrong")
        print(e)
        return


def admin():
    print("WELCOME TO ADMIN MENU")
    print("Type 1 - Add Train")
    print("Type 2 - List Train")
    print("Type 0 - BACK")
    userinput = int(input(">"))

    if userinput == 1:
        addtrain()
    elif userinput == 2:
        listing_trains()
    elif userinput == 0:
        print("BACK TO MAIN MENU")
    else:
        print("INVALID INPUT")
        return

# ---------------------Admin------------------------


# main menu
while True:
    print("WELCOME TO INDIAN RAILWAYS")
    print("Type 1 - User")
    print("Type 2 - Admin")
    print("Type 0 - EXIT")
    userinput = int(input(">"))  # user input

    if userinput == 1:
        user()
    elif userinput == 2:
        admin()
    elif userinput == 0:
        print("EXITING...")
        break
    else:
        print("INVALID INPUT")
        continue
