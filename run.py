from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
import sqlite3 as sql
import base64
import face_recognition
import os
import quickstart as q
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(16)
semester = {'1': 'FirstSem', '2': 'SecondSem', '3': 'ThirdSem', '4': 'FourthSem', '5': 'FifthSem', '6': 'SixthSem',
            '7': 'SeventhSem',
            '8': 'EightSem'}
calendar_id = {'1': '0a799g10j77tnkbeis8bad2r0s@group.calendar.google.com',
               '2': '0a799g10j77tnkbeis8bad2r0s@group.calendar.google.com',
               '3': '6qqlv4qv37cl95dob1mknauvhc@group.calendar.google.com',
               '4': '6qqlv4qv37cl95dob1mknauvhc@group.calendar.google.com',
               '5': 'ju8270ettpthjkuu3pqm60in2c@group.calendar.google.com',
               '6': 'ju8270ettpthjkuu3pqm60in2c@group.calendar.google.com',
               '7':'1ft2u087qunvhp1doimj54tfes@group.calendar.google.com',
               '8': '1ft2u087qunvhp1doimj54tfes@group.calendar.google.com'}


# ROUTE TO RENDER HOMEPAGE
@app.route("/")
def homepage():
    return render_template('homepage.html')


# ROUTE TO PROCESS THE CAPTURED IMAGE
@app.route('/showcam', methods=['GET', 'POST'])
def showcam():
    if request.method == 'GET':
        if 'admin' in session:
            now = datetime.datetime.now()
            return render_template('showcam.html', now=now)
        else:
            return redirect(url_for('homepage'))
    else:
        # Get the image data and make an image file
        img_data = request.form['file']
        head, data = img_data.split(',', 1)
        img_name = "static/img/capturedimage" + ".png"
        plain_data = base64.b64decode(data)
        fh = open(img_name, "wb")
        fh.write(plain_data)
        fh.close()

        sem = (request.form.get('sem'))
        t_name = semester.get((sem))
        c_id = calendar_id.get(sem)
        found = 'NO'
        # Check captured image with the image in the database
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()

                # Get all the subjects in database
                cur.execute("SELECT * FROM " + t_name)
                col_name_list = [row[0] for row in cur.description]

                # GET ALL THE IMAGE LOCATIONS IN DATABASE
                cur.execute("SELECT USN,image from students where sem = ?", (sem,))
                rows = cur.fetchall()
                msg = ''
                for row in rows:
                    print(row)
                    # PROCESS THE CAPTURED IMAGE AND DATABASE IMAGE
                    known_image = face_recognition.load_image_file(row[1])
                    unknown_image = face_recognition.load_image_file(img_name)

                    # CALCULATE THE ENCODINGS OF BOTH THE IMAGES
                    known_encoding = face_recognition.face_encodings(known_image)[0]
                    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

                    # COMPARE THE ENCODINGS OF BOTH THE IMAGES
                    results = face_recognition.compare_faces([known_encoding], unknown_encoding)
                    print('---------',results)
                    if str(results[0]) == "True":
                        print(row[0])
                        found = 'YES'
                        # CALENDAR API ----  GET THE CURRENT SUBJECT FROM CALENDAR
                        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                        events_result = q.service.events().list(calendarId=c_id,
                                                                timeMin=now, maxResults=1, singleEvents=True,
                                                                orderBy='startTime').execute()
                        events = events_result.get('items', [])
                        subject = events[0]['summary']
                        print(subject)

                        # GET THE DETAILS OF CLASSES ATTENDED FROM DATABASE
                        cur.execute("SELECT * from " + t_name + " where USN = ?", (row[0],))
                        sub_row = cur.fetchone()
                        print(sub_row)

                        # GET THE INDEX OF THE SUBJECT IN DATABASE
                        index = col_name_list.index(subject)

                        now1 = datetime.datetime.now();
                        # print(db_time.hour, db_time.day, db_time.month, db_time.year)

                        if t_name != 'EightSem' and  sub_row[6] is None:
                            cur.execute("UPDATE " + t_name + " set LastModified  = ? where USN=?", (now1, row[0]))
                            # UPDATE THE ATTENDANCE
                            cur.execute("UPDATE " + t_name + " set '" + subject + "' = ? where USN=?",
                                        (sub_row[index] + 1, row[0]))
                        elif t_name == 'EightSem' and  sub_row[4] is None:
                            cur.execute("UPDATE " + t_name + " set LastModified  = ? where USN=?", (now1, row[0]))
                            # UPDATE THE ATTENDANCE
                            cur.execute("UPDATE " + t_name + " set '" + subject + "' = ? where USN=?",
                                        (sub_row[index] + 1, row[0]))

                        else:
                            if t_name != 'EightSem' :
                                last = datetime.datetime.strptime(sub_row[6], "%Y-%m-%d %H:%M:%S.%f")
                                if now1.day == last.day and now1.month == last.month and now1.year == last.year:
                                    if now1.hour > last.hour:
                                        # UPDATE THE ATTENDANCE
                                        cur.execute("UPDATE " + t_name + " set '" + subject + "' = ? where USN=?",
                                                    (sub_row[index] + 1, row[0]))
                                        cur.execute("UPDATE " + t_name + " set LastModified  = ? where USN=?",
                                                    (now1, row[0]))
                                        msg = "Attendance updated Successfuly"
                                    else:
                                        msg = "Attendance already Updated"
                                else:
                                    # UPDATE THE ATTENDANCE
                                    cur.execute("UPDATE " + t_name + " set '" + subject + "' = ? where USN=?",
                                                (sub_row[index] + 1, row[0]))
                                    cur.execute("UPDATE " + t_name + " set LastModified  = ? where USN=?", (now1, row[0]))
                                    msg = "Attendance updated Successfuly"
                            else:
                                last = datetime.datetime.strptime(sub_row[4], "%Y-%m-%d %H:%M:%S.%f")
                                if now1.day == last.day and now1.month == last.month and now1.year == last.year:
                                    if now1.hour > last.hour:
                                        # UPDATE THE ATTENDANCE
                                        cur.execute("UPDATE " + t_name + " set '" + subject + "' = ? where USN=?",
                                                    (sub_row[index] + 1, row[0]))
                                        cur.execute("UPDATE " + t_name + " set LastModified  = ? where USN=?",
                                                    (now1, row[0]))
                                        msg = "Attendance updated Successfuly"
                                    else:
                                        msg = "Attendance already Updated"
                                else:
                                    # UPDATE THE ATTENDANCE
                                    cur.execute("UPDATE " + t_name + " set '" + subject + "' = ? where USN=?",
                                                (sub_row[index] + 1, row[0]))
                                    cur.execute("UPDATE " + t_name + " set LastModified  = ? where USN=?",
                                                (now1, row[0]))
                                    msg = "Attendance updated Successfuly"

                        con.commit()
                        break
                if found == 'NO':
                    msg = "Person Not Found"
        except Exception as e:
            # ROLL BACK IF EXCEPTION OCCURS DURING DATABASE OPERATION
            print(e)
            con.rollback()
            msg = 'Person not found'
        finally:
            con.close()
            if msg == '' :
                msg = "Attendance updated Successfuly"
            return jsonify({'reply': msg})


# ROUTE TO SIGNUP STUDENTS
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # STORE THE FORM DATA IN LOCAL VARIABLES
        student_usn = request.form['student_usn']
        student_name = request.form['student_name']
        student_branch = request.form['student_branch']
        student_phno = request.form['student_phno']
        student_passwd = request.form['student_passwd']
        student_sem = request.form.get('sem')
        t_name = semester.get(student_sem)
        print(t_name)
        # CREATE AN IMAGE FILE FOR THE STUDENT
        img_data = request.form['file']
        head, data = img_data.split(',', 1)
        img_name = "static/img/" + student_usn + ".png"
        plain_data = base64.b64decode(data)
        fh = open(img_name, "wb")
        fh.write(plain_data)
        fh.close()
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                # cur.execute("drop table if exists students")
                # INSERT THE FORM DATA INTO THE DATABASE
                cur.execute("INSERT INTO students (USN,name,branch,image,phone_no,sem,password) VALUES (?,?,?,?,?,?,?)",
                            (student_usn, student_name, student_branch, img_name, student_phno, student_sem,
                             student_passwd))
                print("1")
                cur.execute("INSERT INTO " + t_name + "(USN) VALUES (?)", (student_usn,))
                con.commit()
                msg = "Successfully Registered"
        except:
            con.rollback()
            msg = "Error in Registering "
        finally:
            con.close()
            flash(msg)
            print(msg)
            return redirect(url_for('homepage'))
    else:
        now = datetime.datetime.now();
        return render_template('signup.html', now=now)


# ROUTE TO LOGIN STUDENT
@app.route('/studentlogin', methods=['GET', 'POST'])
def studentlogin():
    if request.method == 'POST':
        student_id = request.form['student_usn']
        student_passwd = request.form['student_passwd']
        session.clear()
        session['student'] = request.form['student_usn']
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT password,sem FROM students where USN=?", (student_id,))
                passwd_sem = cur.fetchone()
                sem = passwd_sem[1]
                t_name = semester.get(str(sem))

                # CHECK IF ENTERED PASSWORD IS EQUAL TO REAL PASSWORD
                if student_passwd == passwd_sem[0]:
                    msg = "Successfully Logged IN"
                    cur.execute("SELECT * FROM students JOIN " + t_name +
                                "  ON students.USN = " + t_name + ".USN where students.USN=?  ", (student_id,))
                    row = cur.fetchone()
                    cur.execute("SELECT * FROM " + t_name)
                    col_name_list = [sub[0] for sub in cur.description]
                else:
                    msg = "Incorrect Password"
        except Exception as e:
            msg = "Please enter the USN or password correctly"
            print(e)
        finally:
            con.close()
            flash(msg)
            print(msg)
            if msg == "Successfully Logged IN":
                return render_template('studentdetails.html', row=row, sub=col_name_list)
            else:
                return render_template('login.html')
    else:
        return render_template('login.html')


# Route to show the edit form
@app.route('/editstudent/<sem>', methods=['GET'])
def editstudent(sem):
    if request.method == 'GET':
        usn = session['student']
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                t_name = semester.get(str(sem))
                cur.execute("SELECT * FROM students JOIN " + t_name +
                            "  ON students.USN = " + t_name + ".USN where students.USN=?  ", (usn,))
                row = cur.fetchone()
                cur.execute("SELECT * FROM " + t_name)
                col_name_list = [sub[0] for sub in cur.description]
        except:
            con.rollback()
        finally:
            con.close()
            return render_template('editstudent.html', row=row, sub=col_name_list)


# Route to get the edited student details from student
@app.route('/editstudent', methods=['POST'])
def edit_studentdetails():
    student_usn = session['student']
    student_name = request.form['student_name']
    student_branch = request.form['student_branch']
    student_phno = request.form['student_phno']
    student_sem = request.form['student_sem']
    if request.form.get('checkbox'):
        # CREATE AN IMAGE FILE FOR THE STUDENT
        img_data = request.form['file']
        head, data = img_data.split(',', 1)
        img_name = "static/img/" + student_usn + ".png"
        plain_data = base64.b64decode(data)
        fh = open(img_name, "wb")
        fh.write(plain_data)
        fh.close()
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(" UPDATE students set name = ?,branch=?,phone_no=?,sem=? where USN=?",
                        (student_name, student_branch, student_phno, student_sem, student_usn))
            msg = "Successfully Updated"
    except Exception as e:
        msg = e
        con.rollback()
    finally:
        con.close()
        print(msg)
        return jsonify({'reply': msg})


# ROUTE TO RENDER adminpage TEMPLATE
@app.route('/adminpage')
def adminpage():
    now = datetime.datetime.now();
    return render_template('adminpage.html', now=now)


# Route to show all the student details if logged In
@app.route('/admin')
def admin():
    if 'admin' in session:
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM students")
                rows = cur.fetchall()

        except:
            con.rollback()

        finally:
            con.close()
            now = datetime.datetime.now();
            return render_template('adminpage.html', rows=rows, now=now)
    return render_template('admin.html')


# Route to show the student details if he is logged In
@app.route('/login')
def login():
    if 'student' in session:
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT sem FROM students where USN=?", (session['student'],))
                Sem = cur.fetchone()
                sem = Sem[0]
                t_name = semester.get(str(sem))
                cur.execute("SELECT * FROM students JOIN " + t_name +
                            "  ON students.USN = " + t_name + ".USN where students.USN=?  ", (session['student'],))
                row = cur.fetchone()
                cur.execute("SELECT * FROM " + t_name)
                col_name_list = [sub[0] for sub in cur.description]
        except Exception as e:
            print(e)
            con.rollback()
        finally:
            con.close()
            return render_template('studentdetails.html', row=row, sub=col_name_list)
    return render_template('login.html')


# Route to clear all the session details
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.clear()
    return redirect(url_for('homepage'))


# Route to show the Calendar
@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if request.method == 'GET':
        now = datetime.datetime.now()
        return render_template('calendar.html', now=now)
    else:
        sem = request.form.get('sem')
        sem_name = semester.get(str(sem))
        print(sem_name)
        now = datetime.datetime.now()
        return render_template('calendar.html', calendar=sem_name, now=now)


# ROUTE FOR ADMIN TO LOGIN
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        admin_passwd = request.form['admin_passwd']
        session.clear()
        session['admin'] = request.form['admin_id'];
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT password FROM admin where id=?", (admin_id,))
                real_passwd = cur.fetchone()
                if admin_passwd in real_passwd:
                    msg = "Successfully Logged IN"
                else:
                    msg = "Incorrect Password"
        except:
            msg = "Please enter the USN or password correctly"

        finally:
            con.close()
            flash(msg)
            if msg == "Successfully Logged IN":
                now = datetime.datetime.now()
                return render_template('adminpage.html', msg=msg, now=now)
            else:
                return render_template('admin.html', msg=msg)
    else:
        return render_template('login.html')


@app.route('/details', methods=['POST'])
def getDetails():
    sem = request.form.get('sem')
    t_name = semester.get(sem)
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM students JOIN " + t_name +
                        "  ON students.USN = " + t_name + ".USN where students.sem=?  ", (int(sem),))
            rows = cur.fetchall()
            cur.execute("SELECT * FROM " + t_name)
            col_name_list = [sub[0] for sub in cur.description]
    except Exception as e:
        msg = e

    finally:
        con.close()
        now = datetime.datetime.now();
        return render_template('adminpage.html', rows=rows, sub=col_name_list, now=now)


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
