from flask import Flask,render_template,redirect,url_for,session,request,flash,get_flashed_messages, make_response
from wtforms import StringField,IntegerField,EmailField,SelectField,DateField,TimeField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Length,NumberRange
from bleach import clean
from html import escape
from functools import wraps
import time
import base64
from datetime import datetime
from datetime import timedelta, timezone
from flask_mysqldb import MySQL,MySQLdb
import smtplib
from markupsafe import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json



app = Flask(__name__)
app.config["SECRET_KEY"] = "thisissecret@34256^&"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '7890'
app.config['MYSQL_DB'] = 'My_Hotel'
app.permanent_session_lifetime = timedelta(days=5)


mysql = MySQL(app)

class USER(FlaskForm):
    f_name = StringField("First Name", validators=[DataRequired("First Name is Required"),Length(min=3,max=20,message="First Name must be between 3-20")])
    l_name = StringField("Last_Name", validators=[DataRequired("Last Name is Required"),Length(min=3,max=20,message="Last Name must be between 3-20")])
    gender = SelectField('Gender',choices=[('Male'), ('Female')],validators=[DataRequired("Gender is Required")])
    p_no1 = StringField("Phone Number1", validators=[DataRequired("Phone Number1 is Required"),Length(min=10,max=13,message="Phone Number must between 9-13")])
    email = EmailField("Email", validators=[DataRequired("Email is required"),Length(min=12,max=50,message="Email must between 12-50")])



class event(FlaskForm):
    f_name = StringField("First Name", validators=[DataRequired("First Name is Required"),Length(min=3,max=20,message="First Name must be between 3-20")])
    l_name = StringField("Last_Name", validators=[DataRequired("Last Name is Required"),Length(min=3,max=20,message="Last Name must be between 3-20")])
    gender = SelectField('Gender',choices=[('Male'), ('Female')],validators=[DataRequired("Gender is Required")])
    p_no1 = StringField("Phone Number1", validators=[DataRequired("Phone Number1 is Required"),Length(min=10,max=13,message="Phone Number must between 9-13")])
    email = EmailField("Email", validators=[DataRequired("Email is required"),Length(min=12,max=50,message="Email must between 12-50")])
    number_pep = IntegerField(
        "Number Of People (2-500)",
        validators=[
            DataRequired("This field is required."),
            NumberRange(min=2, max=500, message="Please select a value between 2 and 500.")
        ],
        default=2  
    )
    event_date = DateField("Event Date",validators=[DataRequired("This Field is Required")])
    start_time = TimeField("Start Time",validators=[DataRequired("This Field is Required")])



@app.route("/",methods=["GET","POST"])
def home():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT Room_type, MIN(Room_Image) AS Room_Image FROM Hotel_Rooms GROUP BY room_type;)") 
    result = cur.fetchall()
    length = len(result)
    for room in result:
        if room["Room_Image"] is not None: 
            image_data = base64.b64encode(room["Room_Image"]).decode('utf-8')
            room["Room_Image"] = f"data:image/jpeg;base64,{image_data}"
    return render_template("home_page.html",data=result,length =length)

@app.route("/clear",methods=["GET","POST"])
def homes():
    flash("Successfully Booked Check Your Email ","success")
    return redirect(url_for("home"))

@app.route("/services_)given", methods=["GET","POST"])
def services():
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT Room_Image FROM Hotel_Rooms Where Room_Type = 'Presidential'") 
    result = cur.fetchall()
    length = len(result)
    for room in result:
        if room["Room_Image"] is not None: 
            image_data = base64.b64encode(room["Room_Image"]).decode('utf-8')
            room["Room_Image"] = f"data:image/jpeg;base64,{image_data}"
    session.clear()
    return render_template("services.html",s_show=False,data=result)
    

@app.route("/rooms_all*9", methods=["GET","POST"])
def rooms():
    return render_template("room.html",r_show = False)


@app.route("/events+@#4", methods=["GET","POST"])
def events():
    return render_template("events.html",e_show = False)

@app.route("/books@$!;", methods=["GET","POST"])
def books():
    return redirect(url_for("homes"))

@app.route("/books@s$!/<room_type>",methods=["Get","POST"])
def book_selecting(room_type):
    type = room_type
    return render_template("book.html",type = room_type,cookie_data=cookie_data_get(request),)


def set_cookie_active(res,num_adults,num_kids,check_in,check_out,stay):
    user_session={
                        "num_adults": num_adults,
                        "num_kids" : num_kids,
                        "check_in" : check_in,
                        "check_out" : check_out,
                        "length_of_stay" : stay,
                    }
    res.set_cookie(
    'user_data', 
    json.dumps(user_session), 
    httponly=True, 
    secure=False, 
    samesite='Lax', 
    expires=datetime.now(timezone.utc) + timedelta(20) 
)
   

def cookie_data_get(request):
    user_data = request.cookies.get('user_data')
    if user_data:
        return json.loads(user_data)  
    return {}

def delete_cookie(request):
    session.clear()
    request.set_cookie(
        'user_data', '',
        httponly=True, 
        secure=False, 
        samesite='Lax', 
        expires=datetime.now(timezone.utc) - timedelta(days=1)  
    )


@app.route("/check_in_form", methods=["GET", "POST"])
def check_in_form():
    result = []
    if request.method == "GET":
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            next_day = datetime.now().date() + timedelta(days=1)
            cur.execute("Select Room_No from Room_Book where Check_Out <= %s",(next_day,))
            r_Av = cur.fetchall()
            if r_Av:
                for r_Av in r_Av:
                    av_room = r_Av["Room_No"]
                    cur.execute("Update Hotel_Rooms set Room_Availability = true where Room_No = %s ",(av_room,))
                    cur.execute("DELETE FROM Room_Book WHERE Room_No = %s ",(av_room,))
                    mysql.connection.commit()
            cur.execute("SELECT * FROM Hotel_Rooms WHERE Room_Availability = TRUE ORDER BY RAND()")
            result = cur.fetchall()
            for room in result:
                if room["Room_Image"] is not None: 
                    image_data = base64.b64encode(room["Room_Image"]).decode('utf-8')
                    room["Room_Image"] = f"data:image/jpeg;base64,{image_data}"
        except Exception as e:
            print(e)
        finally:
            session["Result_length"] = len(result)
            session["status"] = 1
            cur.close()

    error = ""
    user_cookie_data = cookie_data_get(request)

    if request.method == "POST":
        session.permanent = True
        num_adults = request.form.get('num_adults', type=int)
        num_kids = request.form.get('num_kids', type=int)
        check_in_date = request.form.get('check_in')
        check_out_date = request.form.get('check_out')
        if not check_in_date:
            error = "Check in is required"
        elif not check_out_date:
            error = "Check out is required"
        else:
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
            stay = (check_out - check_in).days
            resp = make_response(redirect(url_for('check_in_form')))
            set_cookie_active(resp, num_adults, num_kids, check_in.isoformat(), check_out.isoformat(), stay)
            return resp
            
    return render_template('book.html', error=error, database=result, cookie_data=user_cookie_data)

def status_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "status" not in session:
            return redirect(url_for("check_in_form")) 
        return f(*args, **kwargs)
    return decorated_function


@app.route("/book_room/<int:r_no>", methods = ["GET","POST"])
@status_check
def book_room(r_no):
    print(r_no)
    if r_no != "":
        data = cookie_data_get(request)
        if session["status"] == 1:
            form = USER()
            cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur2.execute("Select * from Hotel_Rooms where Room_No = %s",(r_no,))
            result = cur2.fetchall()
            for room in result:
                if room["Room_Image"] is not None: 
                    image_data = base64.b64encode(room["Room_Image"]).decode('utf-8')
                    room["Room_Image"] = f"data:image/jpeg;base64,{image_data}"
            if form.validate_on_submit():
                f_name = form.f_name.data
                l_name = form.l_name.data
                gender = form.gender.data
                p_no1 = form.p_no1.data
                email = form.email.data
                try:
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("select * from Room_Book where Room_No = %s",(r_no,))
                    ch=cur.fetchone()
                    if ch:
                        return redirect("home")
                    cookie = cookie_data_get(request)
                    cur.execute("INSERT INTO User_Book (First_Name, Last_Name, Gender, Phone_Number,  Email) VALUES ( %s, %s, %s, %s, %s)",
                    (f_name, l_name, gender, p_no1, email))
                    user_id = cur.lastrowid
                    check_in_date = datetime.fromisoformat(cookie.get("check_in")).date()
                    check_out_date = datetime.fromisoformat(cookie.get("check_out")).date()
                    cur.execute("INSERT INTO Room_Book (Room_No,User_Id,Check_In,Check_Out) VALUES (%s,%s,%s, %s)",(r_no,user_id, check_in_date, check_out_date))
                    cur.execute(" UPDATE Hotel_Rooms SET Room_Availability = false where Room_No = %s ",(r_no,))
                    cur.execute("select * From User_Book where User_ID=%s",(user_id,))
                    emails = cur.fetchone()
                    if emails: 
                        emailu = emails['Email']
                        f_name = emails["First_Name"]
                        l_name = emails["Last_Name"]
                    mysql.connection.commit()
                    name = f_name+" "+l_name
                    email = emailu
                    messages = clean(escape(f"Dear {f_name} Your Reserve Hotel from Hotel is successfully Done!\n Your Room_no is: {r_no}\nYour Check_In is: {cookie.get("check_in")}\n Your Check Out: {cookie.get("check_out")}\nHave a Good Time!"))
                    passw = "jvqo ohff thol ovay"
                    from_user = "yeabsiratesfaye4118@gmail.com"
                    to_user = email
                    subject = "Hotel Booking"
                    message = MIMEMultipart()
                    message["From"] = from_user
                    message["To"] = to_user
                    message["Subject"] = subject
                    body = f"-name: {name}\n-email: {email}\n-message: {messages}"
                    message.attach(MIMEText(body, "plain"))
                    smtp_server = "smtp.gmail.com"
                    smtp_port = 587
                    try:
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()  
                            server.login(from_user, passw)  
                            server.send_message(message) 
                           
                    except Exception as e:
                            return redirect(url_for("home"))
                except Exception as e:
                    print("Error: ", e)
                    flash("Not Booked Yet! please try again!","error")
                finally:
                    cur.close()
                    res = make_response(redirect(url_for('homes')))
                    delete_cookie(res)
                    return res
            return render_template("book_form.html",form = form, data = result,cookie_data=data)
    return redirect("check_in_form")




@app.route("/event_booking/<event_type>",methods = ["GET","POST"])
def event_booking(event_type):
        form = event()
        error_catering_field = ""
        error_room_field = ""
        room_field = ""
        catering_field = ""
        if request.method=="POST" and form.validate_on_submit():
            f_name = form.f_name.data
            l_name = form.l_name.data
            gender = form.gender.data
            phone_no = form.p_no1.data
            email = form.email.data
            form.number_pep.data = request.form.get('number_pep', type=int)
            event_date = form.event_date.data
            start_time = form.start_time.data
            room_field = request.form.get("room_field")
            catering_field = request.form.get("catering_field")
            number_pep = form.number_pep.data
           
            if all([f_name, l_name, gender, phone_no, email, number_pep, event_date, start_time]):
                if room_field == "" or catering_field == "":
                    if room_field == "" and catering_field == "":
                        error_catering_field = "This Field Is Required"
                        error_room_field = "This Field Is Required"
                    elif room_field !="" and catering_field =="":
                        error_catering_field = "This Field Is Required"
                    elif room_field =="" and catering_field !="":
                        error_room_field = "This Field Is Reuired"
                else:    
                    if room_field == "Yes" or catering_field == "Yes":
                        if room_field == "Yes" and catering_field == "No":
                            try:
                                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                                cur.execute("INSERT INTO User_Book (First_Name, Last_Name, Gender, Phone_Number,  Email) VALUES ( %s, %s, %s, %s, %s)",
                                (f_name, l_name, gender, phone_no, email))
                                user_id = cur.lastrowid
                                cur.execute("insert into Event_Book (User_Id,Event_Name,Start_Time,Event_Date,Number_Of_People,Room_Required,Catering_Required) values (%s,%s,%s,%s,%s,%s,%s)",(user_id,event_type,start_time,event_date,number_pep,True,False))
                                mysql.connection.commit()
                                name = f_name+" "+l_name
                                email = email
                                messages = clean(escape(f"Dear {f_name} Your Reserve Hotel from Hotel is successfully Done!\n Your Event Type is: {event_type}\nYour Event Date is: {event_date}\n Your Start Time: {start_time}\nRoom Required: Yes\nCatering Required: No\nHave a Good Time!"))
                                passw = "jvqo ohff thol ovay"
                                from_user = "yeabsiratesfaye4118@gmail.com"
                                to_user = email
                                subject = "Hotel Booking"
                                message = MIMEMultipart()
                                message["From"] = from_user
                                message["To"] = to_user
                                message["Subject"] = subject
                                body = f"-name: {name}\n-email: {email}\n-message: {messages}"
                                message.attach(MIMEText(body, "plain"))
                                smtp_server = "smtp.gmail.com"
                                smtp_port = 587
                                try:
                                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                                        server.starttls()  
                                        server.login(from_user, passw)  
                                        server.send_message(message) 
                                         
                                        flash("You Booked The Event SuccessFully! You Get A phone Call From Our Service Center!","success")
                                        return redirect(url_for("event_booking"))
                                except Exception as e:
                                        print(e)
                                        return redirect(url_for("events"))
                            except Exception as e:
                                print(e)
                                flash("Ops! The selected Date Is Not Available","error")
                            finally:
                                cur.close()
                            
                        elif catering_field == "Yes" and room_field == "No":
                            try:
                                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                                cur.execute("INSERT INTO User_Book (First_Name, Last_Name, Gender, Phone_Number,  Email) VALUES ( %s, %s, %s, %s, %s)",
                                (f_name, l_name, gender, phone_no, email))
                                user_id = cur.lastrowid
                                cur.execute("insert into Event_Book (User_Id,Event_Name,Start_Time,Event_Date,Number_Of_People,Room_Required,Catering_Required) values (%s,%s,%s,%s,%s,%s,%s)",(user_id,event_type,start_time,event_date,number_pep,False,True))
                                mysql.connection.commit()
                                name = f_name+" "+l_name
                                email = email
                                messages = clean(escape(f"Dear {f_name} Your Reserve Hotel from Hotel is successfully Done!\n Your Event Type is: {event_type}\nYour Event Date is: {event_date}\n Your Start Time: {start_time}\nRoom Required: No\nCatering Required: Yes\nHave a Good Time!"))
                                passw = "jvqo ohff thol ovay"
                                from_user = "yeabsiratesfaye4118@gmail.com"
                                to_user = email
                                subject = "Hotel Booking"
                                message = MIMEMultipart()
                                message["From"] = from_user
                                message["To"] = to_user
                                message["Subject"] = subject
                                body = f"-name: {name}\n-email: {email}\n-message: {messages}"
                                message.attach(MIMEText(body, "plain"))
                                smtp_server = "smtp.gmail.com"
                                smtp_port = 587
                                try:
                                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                                        server.starttls()  
                                        server.login(from_user, passw)  
                                        server.send_message(message) 
                                         
                                        flash("You Booked The Event SuccessFully! You Get A phone Call From Our Service Center!","error")
                                        return redirect(url_for("event_booking"))
                                except Exception as e:
                                        print(e)
                                        return redirect(url_for("events"))
                            except Exception as e:
                                print(e)
                                flash("Ops! The selected Date Is Not Available","error")
                            finally:
                                cur.close()
                            
                        elif room_field == "Yes" and catering_field == "Yes":
                            try:
                                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                                cur.execute("INSERT INTO User_Book (First_Name, Last_Name, Gender, Phone_Number,  Email) VALUES ( %s, %s, %s, %s, %s)",
                                (f_name, l_name, gender, phone_no, email))
                                user_id = cur.lastrowid
                                cur.execute("insert into Event_Book (User_Id,Event_Name,Start_Time,Event_Date,Number_Of_People,Room_Required,Catering_Required) values (%s,%s,%s,%s,%s,%s,%s)",(user_id,event_type,start_time,event_date,number_pep,True,True))
                                mysql.connection.commit()
                                name = f_name+" "+l_name
                                email = email
                                messages = clean(escape(f"Dear {f_name} Your Reserve Hotel from Hotel is successfully Done!\n Your Event Type is: {event_type}\nYour Event Date is: {event_date}\n Your Start Time: {start_time}\nRoom Required: Yes\nCatering Required: Yes\nHave a Good Time!"))
                                passw = "jvqo ohff thol ovay"
                                from_user = "yeabsiratesfaye4118@gmail.com"
                                to_user = email
                                subject = "Hotel Booking"
                                message = MIMEMultipart()
                                message["From"] = from_user
                                message["To"] = to_user
                                message["Subject"] = subject
                                body = f"-name: {name}\n-email: {email}\n-message: {messages}"
                                message.attach(MIMEText(body, "plain"))
                                smtp_server = "smtp.gmail.com"
                                smtp_port = 587
                                try:
                                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                                        server.starttls()  
                                        server.login(from_user, passw)  
                                        server.send_message(message) 
                                        flash("You Booked The Event SuccessFully! You Get A phone Call From Our Service Center!","success")
                                        return redirect(url_for("event_booking"))
                                except Exception as e:
                                        print(e)                                  
                                        return redirect(url_for("events"))
                            except Exception as e:
                                print(e)
                                flash("Ops! The selected Date Is Not Available","error")
                            finally:
                                cur.close()

                    else:
                        try:
                            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                            cur.execute("INSERT INTO User_Book (First_Name, Last_Name, Gender, Phone_Number,  Email) VALUES ( %s, %s, %s, %s, %s)",
                            (f_name, l_name, gender, phone_no, email))
                            user_id = cur.lastrowid
                            cur.execute("insert into Event_Book (User_Id,Event_Name,Start_Time,Event_Date,Number_Of_People,Room_Required,Catering_Required) values (%s,%s,%s,%s,%s,%s,%s)",(user_id,event_type,start_time,event_date,number_pep,False,False))
                            mysql.connection.commit()
                            name = f_name+" "+l_name
                            email = email
                            messages = clean(escape(f"Dear {f_name} Your Reserve Hotel from Hotel is successfully Done!\n Your Event Type is: {event_type}\nYour Event Date is: {event_date}\n Your Start Time: {start_time}\nRoom Required: No\nCatering Required: No\nHave a Good Time!"))
                            passw = "jvqo ohff thol ovay"
                            from_user = "yeabsiratesfaye4118@gmail.com"
                            to_user = email
                            subject = "Hotel Booking"
                            message = MIMEMultipart()
                            message["From"] = from_user
                            message["To"] = to_user
                            message["Subject"] = subject
                            body = f"-name: {name}\n-email: {email}\n-message: {messages}"
                            message.attach(MIMEText(body, "plain"))
                            smtp_server = "smtp.gmail.com"
                            smtp_port = 587
                            try:
                                with smtplib.SMTP(smtp_server, smtp_port) as server:
                                    server.starttls()  
                                    server.login(from_user, passw)  
                                    server.send_message(message) 
                                    print("message sented")
                                    return redirect(url_for("homes"))
                            except Exception as e:
                                    print(e)
                                    return redirect(url_for("events"))
                        except Exception as e:
                            print(e)
                            flash("Ops! The Selected Date Is Not Available","error")
                        finally:
                            cur.close()
        return render_template("event_book.html",event_type = event_type,form = form, error_catering_field =error_catering_field, error_room_field=error_room_field,room_field=room_field,catering_field=catering_field)
        















@app.route('/upload', methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        image_file = request.files['image']
        if image_file:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Hotel_Rooms (Room_Type, Room_Price,Room_Image, Room_Size, Room_Availability ) VALUES ('Deluxe',95,%s, 104,true);",(image_file.read(),))
            mysql.connection.commit()
            cur.close()
            return render_template("home_page.html")  # Directly return the index to show the updated list of images
    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)