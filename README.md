1.cerate all tables which found on mysql hotel.txt on your mysql workbeanch.


      --- edit this codes ---

2. on the first main.py file and on the second file which found on the hotel admin edit this code
      app.config["SECRET_KEY"] = "thisissecret@34256^&"
      app.config['MYSQL_HOST'] = '' #your host mostly it is 'localhost'
      app.config['MYSQL_USER'] = '' # your database username
      app.config['MYSQL_PASSWORD'] = '' # your database password
      app.config['MYSQL_DB'] = 'My_Hotel'

3. on the first main.py change this code to make the email sending process work the hotel admin have no email sending process
      passw = "" # use your email password
      from_user = ""  # use your email on this 
