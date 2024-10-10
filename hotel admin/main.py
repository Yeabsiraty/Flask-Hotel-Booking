from flask import Flask,render_template,redirect,jsonify,session,url_for,flash,get_flashed_messages,request
from wtforms import StringField,PasswordField
from werkzeug.security import check_password_hash,generate_password_hash
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_mysqldb import MySQL,MySQLdb
import bcrypt
from datetime import datetime
from functools import wraps
import base64

from datetime import datetime, timedelta 

app = Flask(__name__)

app.config["SECRET_KEY"] = "thisissecret@34256^&"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '7890'
app.config['MYSQL_DB'] = 'My_Hotel'

mysql = MySQL(app)


class Login_Form(FlaskForm):
     username = StringField("Username",validators=[DataRequired("Thise field is required!")])
     password = StringField("Password", validators=[DataRequired("Thies field is required!")])
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed

def check_password(stored_hash, provided_password):
    provided_password_bytes = provided_password.encode('utf-8') 
    return bcrypt.checkpw(provided_password_bytes, stored_hash.encode('utf-8'))  # Encode only the provided password

def status_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "status" not in session or session["status"] == False:
            return redirect(url_for("login")) 
        return f(*args, **kwargs)
    return decorated_function




@app.route("/", methods=["GET","POST"])
def login():
     session["status"] = False
     form = Login_Form()
     if request.method=="POST" and form.validate_on_submit():
          username = form.username.data
          passw = form.password.data
          if all([username,passw]):
                try:
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("select * from  Hotel_Admin as a inner join Hotel_Employees as e on a.Employee_Id = e.Employee_Id where a.Username = %s",(username,))
                    result = cur.fetchall()
                    if result:
                        for data in result:
                            d_pas = data["Pass_key"]
                            name = data["First_Name"]
                            if check_password(d_pas,passw):
                                    session["status"] = True
                                    return redirect(url_for('dashboard'))
                            else:
                                    flash("Incorrect Passw or username!","error")
                            

                    else:
                         flash("Account not Found!","error")
                except Exception as e:
                    print(e)               
                    flash("Please Try Again!","error")
                finally:
                     cur.close()
          
     return render_template("login.html",form=form)


@app.route("/dashboard")
@status_check
def dashboard():
    total = 0
    room_book = 0
    event = 0
    room_free = 0
    in_hotel = 0
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT COUNT(Room_No) AS count FROM Room_Book")
        room_book = cur.fetchone()['count'] or 0 
        cur.execute("SELECT COUNT(EVENT_ID) AS count FROM Event_Book")
        event = cur.fetchone()['count'] or 0 
        cur.execute("SELECT COUNT(Room_No) AS count FROM Hotel_Rooms WHERE Room_Availability = %s", (True,))
        room_free = cur.fetchone()['count'] or 0 
        date = datetime.now().date()
        cur.execute("SELECT COUNT(DISTINCT u.User_Id) AS count FROM User_Book u JOIN Room_Book r ON u.User_Id = r.User_Id WHERE r.Check_Out > %s", (date,))
        in_hotel = cur.fetchone()["count"] or 0
        total = room_book + event 
    except Exception as e:
         print(e)
         flash("Please Try Again","error")
    finally:
         cur.close()
    return render_template("homepage.html",total = total,room_book = room_book,event = event,room_free = room_free,in_hotel = in_hotel)

@app.route("/notification",methods = ["GET","POST"])
@status_check
def notification():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    room_type = ""
    try:
        cur.execute("Select * from Room_Book where Check_Out <= %s",(datetime.now().date(),))
        result = cur.fetchall()
        if result:
            for data in result:
                room_no = data["Room_No"]
                cur.execute("select Room_Type from Hotel_Rooms where Room_No = %s ",(room_no,))
                room_type = cur.fetchone()
                room_type = room_type["Room_Type"]

    except Exception as e:
        print(e)
    finally:
        cur.close()
    return render_template("notification.html",database = result,room_type = room_type)

@app.route("/search_room", methods=["POST"])
def search_room():
    search_query = request.form.get('search')
    result = []
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM Hotel_Rooms WHERE Room_No LIKE %s or Room_Type LIKE %s or Room_Price LIKE %s or Room_Size LIKE %s", (f"%{search_query}%",f"%{search_query}%",f"%{search_query}%",f"%{search_query}%"))
        result = cur.fetchall()
        for room in result:
            if room["Room_Image"] is not None: 
                image_data = base64.b64encode(room["Room_Image"]).decode('utf-8')
                room["Room_Image"] = f"data:image/jpeg;base64,{image_data}"
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return jsonify(result)


@app.route("/search_room_book", methods=["POST"])
def search_room_book():
    search_query = request.form.get('search')
    result = []
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
    SELECT rb.Room_No, ub.User_Id, ub.First_Name, ub.Last_Name, rb.Check_In, rb.Check_Out 
    FROM User_Book ub 
    INNER JOIN Room_Book rb ON rb.User_ID = ub.User_Id 
    WHERE rb.Room_No LIKE %s OR ub.User_Id LIKE %s OR ub.First_Name LIKE %s OR ub.Last_Name LIKE %s OR rb.Check_In LIKE %s OR rb.Check_Out LIKE %s
  """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        result = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return jsonify(result)






@app.route("/search_guest", methods=["POST"])
def search_guest():
    search_query = request.form.get('search', '')
    result = []
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM User_Book WHERE User_Id LIKE %s OR First_Name LIKE %s OR  Gender LIKE %s OR Last_Name LIKE %s OR Phone_Number LIKE %s OR Email LIKE %s", 
                    (f"%{search_query}%", f"%{search_query}%",f"%{search_query}%", f"%{search_query}%" , f"%{search_query}%" , f"%{search_query}%"))
        result = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return jsonify(result)

@app.route("/room")
@status_check
def room():
    result = ""
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from Hotel_Rooms")
        result = cur.fetchall()
        for room in result:
                if room["Room_Image"] is not None: 
                    image_data = base64.b64encode(room["Room_Image"]).decode('utf-8')
                    room["Room_Image"] = f"data:image/jpeg;base64,{image_data}"
    except Exception as e:
        print(e)
    finally:
            cur.close()
    return render_template("room.html",database = result)


@app.route("/room_edit", methods = ["GET","POST"])
def room_edit():
    if request.method == "POST":
        room_no = request.form.get("room_no")
        room_type = request.form.get("room_type")
        room_size = request.form.get("room_size")
        room_price = request.form.get("room_price")
        room_image = request.files.get("room_image") 
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if room_image and room_image.filename:
                cur.execute("update Hotel_Rooms set Room_Type = %s , Room_Size = %s , Room_Price = %s,Room_Image = %s where Room_No=%s",(room_type,room_size,room_price,room_image.read(),room_no))
                mysql.connection.commit()
                flash("Successfully Updated","success")
            else:
                cur.execute("update Hotel_Rooms set Room_Type = %s , Room_Size = %s , Room_Price = %s where Room_No=%s",(room_type,room_size,room_price,room_no))
                mysql.connection.commit()
                flash("Successfully Updated","success")
        except Exception as e:
            print(e)
            flash("Try again","error")
        finally:
                cur.close()
    return redirect(url_for("room"))

@app.route("/room_delete", methods = ["GET","POST"])
def room_delete():
    if request.method == "POST":
        room_no = request.form.get("room_no")
        password = request.form.get("password")
        if password == "1234":
            try:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("DELETE FROM Hotel_Rooms WHERE Room_No = %s", (room_no,))
                mysql.connection.commit()
                flash("Successfully Deleted!","success")
            except Exception as e:
                print(e)
            finally:
                    cur.close()
        else:
            flash("Your Password is Not Correct!","error")
    return redirect(url_for("room"))

@app.route("/room_add",methods = ["GET","POST"])
def room_add():
    if request.method == "POST":
        room_type = request.form.get("room_type")
        room_size = request.form.get("room_size")
        room_price = request.form.get("room_price")
        room_image = request.files.get("room_image")
        try:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("INSERT INTO Hotel_Rooms (Room_Type, Room_Price, Room_Image, Room_Size, Room_Availability) VALUES (%s, %s, %s, %s, true);", (room_type, room_price, room_image.read(), room_size))
                mysql.connection.commit()
                flash("Successfully Added!","success")
        except Exception as e:
                print(e)
                flash("Please Try Again!","error")
        finally:
                cur.close()
    return redirect(url_for("room"))


@app.route("/events")
@status_check
def event():
    return render_template("event.html")

@app.route("/guests")
@status_check
def guest():
    result2 = ""
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from User_Book;")
        result2 = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return render_template("guest.html",database2 = result2)


@app.route("/guest_edit", methods= ["GET","POST"])
def guest_edit():
    if request.method == "POST":
        g_id = request.form.get("guest_id")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        gender = request.form.get("gender")
        email = request.form.get("email")
        phone = request.form.get("phone_no")  
        if all([g_id,f_name,l_name,gender,email,phone]):
            try:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("update User_Book set First_Name = %s , Last_Name = %s , Gender = %s ,Email = %s , Phone_Number = %s where User_Id = %s",(f_name,l_name,gender,email,phone,g_id))
                mysql.connection.commit()
                flash("Successfully Updated","success")
            except Exception as e:
                print(e)
                flash("Try Again!","error")
            finally:
                cur.close()
    return redirect(url_for('guest'))

@app.route("/guest_delete", methods = ["GET","POST"])
def guest_delete():
    if request.method == "POST":
        guest_id = request.form.get("guest_id")
        password = request.form.get("password")
        if password == "1234":
            try:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("DELETE FROM User_Book WHERE User_Id = %s", (guest_id,))
                mysql.connection.commit()
                flash("Successfully Deleted!","success")
            except Exception as e:
                print(e)
            finally:
                    cur.close()
        else:
            flash("Your Password is Not Correct!","error")
    return redirect(url_for("guest"))


@app.route("/room_bookes",methods = ["GET","POST"])
@status_check
def room_book():
    result3 = ""
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT rb.Room_No, ub.User_Id,ub.First_Name, ub.Last_Name, rb.Check_In, rb.Check_Out FROM User_Book ub INNER JOIN Room_Book rb ON rb.User_ID = ub.User_Id;")
        result3 = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    
    return render_template("room_book.html",database3 = result3)


@app.route("/edit_room_book", methods = ["GET","POST"])
def edit_room_book():
    if request.method == "POST":
          room_no = request.form.get("room_no")
          check_in = request.form.get("check_in")
          check_out = request.form.get("check_out")
          if all([room_no,check_in,check_out]):
                try:
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("update Room_Book set Check_In = %s , Check_Out = %s where Room_No = %s",(check_in,check_out,room_no))
                    mysql.connection.commit()
                    flash("Successfully Deleted!","success")
                except Exception as e:
                    print(e)
                    flash("Try Again!","error")
                finally:
                    cur.close()
    return redirect(url_for('room_book'))
                

@app.route("/delete_room_book", methods = ["GET","POST"])
def delete_room_book():
    if request.method == "POST":
          room_no = request.form.get("room_no")
          password = request.form.get("password")
          if all([room_no,password]):
                if password == "1234":
                    try:
                        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        cur.execute("DELETE FROM Room_Book WHERE Room_No = %s", (room_no,))
                        cur.execute("update Hotel_Rooms set Room_Availability = %s where Room_No = %s",(True,room_no,))
                        mysql.connection.commit()
                        flash("Successfully Deleted!","success")
                    except Exception as e:
                        print(e)
                        flash("Try Again!","error")
                    finally:
                        cur.close()
                else:
                    flash("Your Password is Not Correct!","error")
    return redirect(url_for('room_book'))




@app.route("/event_book")
def event_book():
    result5 = ""
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select eb.User_Id,eb.EVENT_ID,ur.First_Name,ur.Email,ur.Phone_Number,eb.Event_Name,eb.Start_Time,eb.Event_Date,eb.Number_Of_People,eb.Room_Required,eb.Catering_Required from User_Book ur inner join Event_Book eb on ur.User_Id = eb.User_Id;")
        result5 = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return render_template("event_book.html",database5 = result5)


@app.route("/edit_book_event",methods = ["GET","POST"])
def edit_book_event():
    if request.method == "POST":
          event_id = request.form.get("event_id")
          event_type = request.form.get("event_type")
          event_date = request.form.get("event_date")
          no_peop = request.form.get("number_of_people")
          start_time = request.form.get("start_time")
          room_req = request.form.get("room_required")
          catering_req = request.form.get("catering_required")  

          print(event_id,event_type,event_date,no_peop,start_time,room_req,catering_req)    
          if all([event_id,event_type,event_date,no_peop,start_time,room_req,catering_req]):
                        
                if room_req == "1":
                    room_req = True
                else:
                    room_req = False
                if catering_req == "1":
                    catering_req= True
                else:
                    catering_req = False  
                try:
                        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        cur.execute("update Event_Book set Event_Name = %s, Event_Date = %s , Number_Of_People = %s , Start_Time = %s , Room_Required = %s , Catering_Required = %s where EVENT_ID = %s",(event_type,event_date,no_peop,start_time,room_req,catering_req,event_id))
                        mysql.connection.commit()
                        flash("Successfully Edited!","success")
                except Exception as e:
                        print(e)
                        flash("Try Again!","error")
                finally:
                        cur.close()
          else:
               print("no")
    return redirect(url_for("event_book"))



from datetime import datetime

@app.route("/search_event_book", methods=["POST"])
def search_event_book():
    search_query = request.form.get('search')
    print(f'Searching for: {search_query}')  # Debug: print the search query
    result = []
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(""" SELECT 
                eb.User_Id,
                eb.EVENT_ID,
                ur.First_Name,
                ur.Email,
                ur.Phone_Number,
                eb.Event_Name,
                eb.Start_Time,
                eb.Event_Date,
                eb.Number_Of_People,
                eb.Room_Required,
                eb.Catering_Required 
            FROM User_Book ur 
            INNER JOIN Event_Book eb ON ur.User_Id = eb.User_Id 
            WHERE 
                ur.User_Id LIKE %s OR 
                ur.First_Name LIKE %s OR 
                ur.Email LIKE %s OR 
                ur.Phone_Number LIKE %s OR 
                eb.Event_Name LIKE %s OR 
                eb.Start_Time LIKE %s OR 
                eb.Event_Date LIKE %s OR 
                eb.Number_Of_People LIKE %s
        """, (f"%{search_query}%",) * 8)

        result = cur.fetchall()
        
        # Convert any `timedelta` objects to string
        for row in result:
            # Ensure to convert date/time fields if they are of a `timedelta` type
            if isinstance(row['Start_Time'], timedelta):
                row['Start_Time'] = str(row['Start_Time'])  # or format it accordingly
            if isinstance(row['Event_Date'], datetime):
                row['Event_Date'] = row['Event_Date'].isoformat()  # Convert to ISO format for JSON
          
        print(f'Results found: {result}')  # Debug: print the results
    except Exception as e:
        print(f"An error occurred: {e}")  # Better error logging
        return jsonify({"error": str(e)}), 500  # Return error response
    finally:
        cur.close()  # Ensure cursor is closed
    return jsonify(result)




@app.route("/delete_book_event",methods = ["GET","POST"])
def delete_book_event():
    if request.method == "POST":
         event_id = int(request.form.get("event_id"))
         password = request.form.get("password")

         if all([event_id,password]):
              if password == "1234":
                    try:
                        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        cur.execute("DELETE FROM Event_Book WHERE EVENT_ID = %s", (event_id,))
                        mysql.connection.commit()
                        flash("Successfully Deleted!","success")
                    except Exception as e:
                        print(e)
                        flash("Try Again!","error")
                    finally:
                        cur.close()
              else:
                    flash("Your Password is Not Correct!","error")

    return redirect(url_for("event_book"))
     





@app.route("/staff")
@status_check
def staff():
    result6 = ""
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from Hotel_Employees")
        result6 = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return render_template("staff.html", database6 = result6)


@app.route("/search_staff", methods=["POST"])
def search_staff():
    search_query = request.form.get('search', '')
    result = []
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from Hotel_Employees WHERE Employee_Id LIKE %s OR First_Name LIKE %s OR Last_Name LIKE %s OR Phone_Number LIKE %s OR Email LIKE %s OR Roll LIKE %s OR Salary LIKE %s", 
                    (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%" , f"%{search_query}%" , f"%{search_query}%" , f"%{search_query}%" , f"%{search_query}%"))
        result = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return jsonify(result)


@app.route("/add_staff",methods=["GET","POST"])
def add_staff():
     if request.method == "POST":
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        p_no = request.form.get("p_no")
        email = request.form.get("email")
        roll = request.form.get("roll")
        salary= request.form.get("salary")
        if all([f_name,l_name,p_no,email,roll,salary]):
            try:
                  cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                  cur.execute("insert into Hotel_Employees (First_Name,Last_Name,Phone_Number,Email,Roll,Salary) values (%s,%s,%s,%s,%s,%s)",(f_name,l_name,p_no,email,roll,salary))
                  mysql.connection.commit()
                  flash("Successfully Add!","success")
            except Exception as e:
                 print(e)
                 flash("Please Try Again!","error")
            finally:
                 cur.close()
     return redirect("staff")




@app.route("/edit_staff",methods=["GET","POST"])
def edit_staff():
    if request.method == "POST":
          e_id = request.form.get("em_id")
          f_name = request.form.get("f_name")
          l_name = request.form.get("l_name")
          p_no = request.form.get("p_no")
          email = request.form.get("email")
          roll = request.form.get("roll")
          salary = request.form.get("salary")
          if all([e_id,f_name,l_name,p_no,email,roll,salary]):
                try:
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("update Hotel_Employees set First_Name = %s ,Last_Name = %s, Phone_Number = %s, Email = %s ,Roll = %s ,Salary = %s",(f_name,l_name,p_no,email,roll,salary))
                    mysql.connection.commit()
                    flash("Successfully Edited!","success")
                except Exception as e:
                     print(e)
                     flash("Please Try Again!","error")
                finally:
                     cur.close()
    return redirect(url_for("staff"))    



@app.route("/delete_staff",methods=["GET","POST"])
def delete_staff():
        if request.method == "POST":
             eid = request.form.get("emp_id")
             pas = request.form.get("password")
             if all([eid,pas]):
                  if pas == "1234":
                    try:
                        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        cur.execute("delete from Hotel_Employees where Employee_Id = %s",(eid))
                        mysql.connection.commit()
                        flash("Successfully Deleted!","success")
                    except Exception as e:
                        print(e)
                        flash("Please Try Again!","error")
                    finally:
                        cur.close()
        return redirect(url_for("staff"))

@app.route("/admin")
@status_check
def admin():
    result7 = ""
    try:
         cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cur.execute("select * from Hotel_Admin")
         result7 = cur.fetchall()
    except Exception as e:
         print(e)
    finally:
         cur.close()
    return render_template("admin.html",database7 = result7)







@app.route("/admin_add" ,methods=["GEt","POST"])
def admin_add():
    if request.method == "POST":
          e_id = request.form.get("emp_id")
          f_name = request.form.get("f_name")
          l_name = request.form.get("l_name")
          username = request.form.get("username")
          pas = request.form.get("password")
          c_pas = request.form.get("c_pass")
          if all([e_id,f_name,l_name,username,pas,c_pas]):
            if pas == c_pas:
                pas = hash_password(pas)
                try:
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("select * from Hotel_Employees where Employee_Id = %s and First_Name = %s and Last_Name = %s",(e_id,f_name,l_name))
                    result = cur.fetchone()
                    if result:
                        cur.execute("select * from Hotel_Admin where Username = %s",(username,))
                        rt = cur.fetchone()
                        if rt:
                            flash("username not available please use another username!","error")
                        else:
                            cur.execute("insert into Hotel_Admin (Employee_Id,Username,Pass_key)values(%s,%s,%s)",(e_id,username,pas))
                            mysql.connection.commit()
                            flash("Successfully Added","success")
                    else:
                         flash("Employee not found","error")

                except Exception as e:
                     print(e)
                     flash("Pelase Try Again!","error")
                finally:
                     cur.close()
            else:
                 flash("Password Doesn't Match!","error")
    return redirect(url_for("admin"))
        

@app.route("/edit_admin",methods = ["GET","POST"])
def edit_admin():
    if request.method == "POST":
          username = request.form.get("username")
          o_pas = request.form.get("o_pass")
          n_pas2 = request.form.get("n_pass")
          c_pass = request.form.get("c_pass")
          if all([username,o_pas,n_pas2,c_pass]):
                if n_pas2 == c_pass:
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    try:
                        cur.execute("select * from Hotel_Admin where Username = %s",(username,))
                        result = cur.fetchall()
                        if result:
                            for data in result:
                                d_pas = data["Pass_key"]
                                if check_password(d_pas,o_pas):
                                    try:
                                          n_pas = hash_password(n_pas2)
                                          cur.execute("update Hotel_Admin set Pass_key = %s where Username = %s",(n_pas,username))
                                          mysql.connection.commit()
                                          flash("successfully updated!","success")
                                    except Exception as e:
                                         print(e)
                                         flash("please try again!","error")
                                    finally:
                                         cur.close()
                                else:
                                     flash("Old password doesn't match!","error")
                        else:
                             flash("username not found!","error")
                    except Exception as e:
                         print(e)
                         flash("please try again!","error")
                else:
                     flash("password doesn't match!","error")
    return redirect(url_for("admin"))                


@app.route("/delete_admin",methods=["GET","POST"])
def delete_admin():
     if request.method == "POST":
            username = request.form.get("username")
            pas = request.form.get("password")
            if all([username,pas]):
                if pas == "1234":
                    try:
                        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        cur.execute("delete from Hotel_Admin where Username = %s",(username,))
                        mysql.connection.commit()
                    except Exception as e:
                        print(e)
                        flash("please try again!","error")
                    finally:
                        cur.close()
                else:
                     flash("password doesn't match!","error")
            else:
                 flash("username not found!" ,"error")
     return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)