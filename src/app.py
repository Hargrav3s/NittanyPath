from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from secrets import token_hex

from datetime import datetime

import sqlite3 as sql
import hashlib as hash

# Flask is for the main rendering of HTML pages as well as url mapping.
# SQLAlchemy is used for the user class used for flask_login
# flask_login is used as a login manager, keeping track of which users are logged in.
# datetime is used for comparing dates for dropping classes.
# sqlite3 is used to communicate with my database.
# hashlib is used to hash the database passwords using MD4 format.

app = Flask("NittanyPath-v1")
app.secret_key = token_hex(16)
host = 'http://127.0.0.1:5000/'

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

login = LoginManager(app)


# Used to load a user from User class.
@login.user_loader
def load_user(email):
    return User.query.get(email)


# User Class for SQLAlchemy
class User(UserMixin, db.Model):
    __tablename__ = "User"
    __table_args__ = {'extend_existing': True}

    email = db.Column("email", db.Text, primary_key=True)
    password = db.Column("password_hashed", db.Text)
    name = db.Column("name", db.Text)
    age = db.Column("age", db.Integer)
    gender = db.Column("gender", db.CHAR)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email


# Used to render the home page.
@app.route('/')
def index():
    return render_template('index.html')


# logic for the login page.
@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # if the user requests to login
    if request.method == "POST":

        # Check if forms are empty.
        if request.form['loginEmail'] == "" or request.form['loginPassword'] == "":
            flash("invalid username or password")
            return render_template('login.html', submission=False)

        connection = sql.connect('database.db')

        # check users for the email.
        cursor = connection.execute('SELECT * FROM User WHERE email = ?', (request.form['loginEmail'],))
        row = cursor.fetchone()

        # if the email exists within database.
        if row:

            # check the password
            given_password = hash.new('md4', request.form['loginPassword'].encode()).hexdigest()

            if given_password == row[1]:
                # User will be logged in.
                user = User.query.filter_by(email=request.form['loginEmail']).first()
                login_user(user)

                # send them to the dashboard
                return redirect(url_for('dashboard'))

        flash("invalid username or password")
        return render_template('login.html', error=error, submission=False)

    return render_template('login.html')


# logs out the user.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# the main dashboard for users.
@app.route('/dashboard')
@login_required
def dashboard():
    userType = get_user_type(current_user.email)
    classes = None

    # if user is a student, give them the student view.
    if userType == "student":
        classes = get_enrolled_classes(current_user.email)
        classesTaught = get_TA_classes(current_user.email)

    # if user is a professor, give them the professor view.
    elif userType == "professor":
        classesTaught = get_taught_classes(current_user.email)

    # if user is unknown type for any reason, return them to the login page.
    else:
        return redirect(url_for('login'))

    # render the dashboard.
    return render_template('dashboard.html', name=current_user.name, classes=classes, classesTaught=classesTaught)


# the main display for all users.
# displays regular class information for non-enrolled students and professors.
# displays assignment, exam, and post information for students.
# displays controls for professors.
# displays posts for TAs.
@app.route('/classInfo/<class_id>', methods=['GET', 'POST'])
@login_required
def classInfo(class_id):
    # get course info.
    courseInfo = get_class_info(class_id)

    if request.method == 'POST':

        # Post method is only used for enrolled students to drop the course.
        if isEnrolled(current_user.email, class_id):
            section = get_student_section(current_user.email, class_id)
            dropCourse(current_user.email, class_id, section[2])
        return redirect(url_for('dashboard'))

    # if courseInfo not available return to dashboard.
    if not courseInfo:
        return redirect(url_for('dashboard'))

    # get user's type
    user_type = get_user_type(current_user.email)

    if user_type == 'student':

        # if student is a TA for the class, return view for TA.
        if isTAforClass(current_user.email, class_id):
            # TA Teaches this class!
            return render_template('classInfo.html', isStudent=True, isEnrolled=False, isTA=True, isProf=False,
                                   courseInfo=courseInfo)

        # if user is enrolled in the class.
        if isEnrolled(current_user.email, class_id):
            # get professor and section information.
            professor = get_professor_contact(courseInfo[3])
            section = get_student_section(current_user.email, class_id)

            avgHWGrade = get_avg_hw_grade(current_user.email, class_id)
            avgExamGrade = get_avg_exam_grade(current_user.email, class_id)
            totalGrade = get_total_grade(current_user.email, class_id)
            print(avgHWGrade)
            print(avgExamGrade)
            print(totalGrade)

            # return view for enrolled student.
            return render_template('classInfo.html', avgHWGrade=avgHWGrade, avgExamGrade=avgExamGrade, totalGrade=totalGrade, sec_no=section[2], isStudent=True, isEnrolled=True, isTA=False,
                                   isProf=False, courseInfo=courseInfo, professor=professor)

        # if student is not enrolled AND is not a TA, return standard student view.
        return render_template('classInfo.html', isStudent=True, isEnrolled=False, isTA=False, isProf=False,
                               courseInfo=courseInfo)
    else:

        # user must be a professor.
        if isProfForClass(current_user.email, class_id):
            # Professor Teaches this class, give them main professor control view.
            return render_template('classInfo.html', isStudent=False, isEnrolled=True, isTA=False, isProf=True,
                                   courseInfo=courseInfo)

        # Professor does not teach this class, return standard course view.
        return render_template('classInfo.html', isStudent=False, isEnrolled=False, isTA=False, isProf=True,
                               courseInfo=courseInfo)


# logic for assignments page, displays assignments to enrolled students and professor.
# redirects to dashboard for other users.
@app.route('/classInfo/<class_id>/Assignments')
@login_required
def classInfoAssignments(class_id):
    courseInfo = get_class_info(class_id)

    if not courseInfo:
        return redirect(url_for('dashboard'))

    user_type = get_user_type(current_user.email)

    if user_type == 'student':

        if isEnrolled(current_user.email, class_id):
            section = get_student_section(current_user.email, class_id)
            assignments = get_homework(class_id, section[2])
            assign_grades = get_homework_grades(current_user.email, class_id, section[2])

            returnAssigns = []
            flag = False

            if assignments:
                if assign_grades:
                    for assignment in assignments:
                        for grade in assign_grades:
                            if grade[3] == assignment[2]:
                                # if the grade is for assignment 2
                                returnAssigns.append((grade[3], assignment[3], grade[4]))
                                Flag = True
                        if Flag:
                            Flag = False
                        else:
                            returnAssigns.append((assignment[2], assignment[3], '-'))
                else:
                    for assignment in assignments:
                        returnAssigns.append((assignment[2], assignment[3], "-"))
            return render_template('assignments.html', courseInfo=courseInfo, assignments=returnAssigns, isStudent=True,
                                   isProf=False)
        else:
            return redirect(url_for('dashboard'))
    else:
        taughtClasses = get_taught_classes(current_user.email)
        if taughtClasses[0][0] == class_id:
            sections = get_sections(class_id)
            total_assignments = []
            for section in sections:
                assignments = get_homework(class_id, section[1])
                total_assignments.append((section[1], assignments))
            return render_template('assignments.html', courseInfo=courseInfo, total_assignments=total_assignments,
                                   isStudent=False,
                                   isProf=True)

        return redirect(url_for('dashboard'))


@app.route('/classInfo/<class_id>/Assignments/<sec_no>/<assignment_no>', methods=['POST', 'GET'])
@login_required
def gradeAssignments(class_id, sec_no, assignment_no):
    if not isProfForClass(current_user.email, class_id):
        return redirect(url_for(dashboard))

    courseInfo = get_class_info(class_id)

    if request.method == 'POST':
        email = request.form["grade button"]
        grade = request.form['gradeToChange']
        change_hw_grade(email, class_id, sec_no, assignment_no, grade)

    grades = get_student_HW_grades(class_id, sec_no, assignment_no)
    return render_template('gradeAssignments.html', courseInfo=courseInfo, sec_no=sec_no, assignment_no=assignment_no,
                           grades=grades)


@app.route('/classInfo/<class_id>/Exams')
@login_required
def classInfoExams(class_id):
    courseInfo = get_class_info(class_id)

    if not courseInfo:
        return redirect(url_for('dashboard'))

    user_type = get_user_type(current_user.email)

    if user_type == 'student':

        if isEnrolled(current_user.email, class_id):
            section = get_student_section(current_user.email, class_id)
            assignments = get_exams(class_id, section[2])
            assign_grades = get_exam_grades(current_user.email, class_id, section[2])
            returnAssigns = []
            flag = False

            if assignments:
                if assign_grades:
                    for assignment in assignments:
                        for grade in assign_grades:
                            if grade[3] == assignment[2]:
                                # if the grade is for assignment 2
                                returnAssigns.append((grade[3], assignment[3], grade[4]))
                                Flag = True
                        if Flag:
                            Flag = False
                        else:
                            returnAssigns.append((assignment[2], assignment[3], "-"))
                else:
                    for assignment in assignments:
                        returnAssigns.append((assignment[2], assignment[3], "-"))
            return render_template('exams.html', courseInfo=courseInfo, assignments=returnAssigns, isStudent=True,
                                   isProf=False)
        else:
            return redirect(url_for('dashboard'))
    else:
        taughtClasses = get_taught_classes(current_user.email)
        if taughtClasses[0][0] == class_id:
            sections = get_sections(class_id)
            total_assignments = []
            for section in sections:
                assignments = get_exams(class_id, section[1])
                total_assignments.append((section[1], assignments))
            return render_template('exams.html', courseInfo=courseInfo, total_assignments=total_assignments,
                                   isStudent=False, isProf=True)

        return redirect(url_for('dashboard'))


@app.route('/classInfo/<class_id>/Exams/<sec_no>/<assignment_no>', methods=['POST', 'GET'])
@login_required
def gradeExams(class_id, sec_no, assignment_no):
    if not isProfForClass(current_user.email, class_id):
        return redirect(url_for(dashboard))

    courseInfo = get_class_info(class_id)

    if request.method == 'POST':
        email = request.form["grade button"]
        grade = request.form['gradeToChange']
        change_exam_grade(email, class_id, sec_no, assignment_no, grade)

    grades = get_student_exam_grades(class_id, sec_no, assignment_no)
    return render_template('gradeExams.html', courseInfo=courseInfo, sec_no=sec_no, assignment_no=assignment_no,
                           grades=grades)


@app.route('/classInfo/<class_id>/createAssignment', methods=['POST', 'GET'])
@login_required
def createAssignment(class_id):
    if not isProfForClass(current_user.email, class_id):
        return redirect(url_for('dashboard'))

    sections = get_sections(class_id)
    return render_template('createAssignment.html', sections=sections, class_id=class_id)


@app.route('/classInfo/<class_id>/createAssignment/<sec_no>/<types>', methods=['POST', 'GET'])
@login_required
def createAssignments(class_id, sec_no, types):
    if not isProfForClass(current_user.email, class_id):
        return redirect(url_for('dashboard'))

    if types == 'False':
        types = False
    else:
        types = True

    if not types:
        details = request.form.get('assignmentDetails')
        addHomework(class_id, sec_no, details)
    else:
        details = request.form.get('examDetails')
        addExam(class_id, sec_no, details)

    return redirect(url_for('createAssignment', class_id=class_id))


@app.route('/classInfo/<class_id>/Enroll', methods=['POST', 'GET'])
@login_required
def classEnroll(class_id):
    courseInfo = get_class_info(class_id)
    if get_user_type(current_user.email) == "professor":
        return redirect(url_for('dashboard'))

    if isEnrolled(current_user.email, class_id):
        return redirect(url_for('dashboard'))

    sections = get_sections(class_id)
    return render_template('classEnroll.html', courseInfo=courseInfo, class_id=class_id, sections=sections)


@app.route('/classInfo/<class_id>/Enroll/<sec_no>', methods=['POST', 'GET'])
@login_required
def enrollingClass(class_id, sec_no):
    if get_user_type(current_user.email) == "professor":
        return redirect(url_for('dashboard'))

    if isEnrolled(current_user.email, class_id):
        return redirect(url_for('dashboard'))

    if canEnroll(current_user.email, class_id, sec_no):
        enrollUser(current_user.email, class_id, sec_no)

    return redirect(url_for('dashboard'))


@app.route('/classInfo/<class_id>/Posts', methods=['POST', 'GET'])
@login_required
def displayPosts(class_id):
    courseInfo = get_class_info(class_id)

    if request.method == 'POST':
        if isEnrolled(current_user.email, class_id) or isTAforClass(current_user.email, class_id) or isProfForClass(
                current_user.email, class_id):
            content = request.form.get('PostTextArea')
            if content != "":
                addPost(class_id, current_user.email, content)

    if isEnrolled(current_user.email, class_id) or isTAforClass(current_user.email, class_id) or isProfForClass(
            current_user.email, class_id):
        posts = get_posts(class_id)

        rposts = []
        for post in posts:
            comments = get_comments(post)
            rcomments = []
            for comm in comments:
                rcomments.append((comm[2], get_name(comm[3]), comm[4]))
            rposts.append((post[1], get_name(post[2]), post[3], rcomments))

        return render_template('posts.html', posts=rposts, courseInfo=courseInfo)
    else:
        return redirect(url_for('dashboard'))


@app.route('/userProfile', methods=['GET', 'POST'])
@login_required
def userProfile():
    userType = get_user_type(current_user.email)
    wentThrough = False
    shouldFlash = False

    if request.method == "POST":
        wentThrough = False
        shouldFlash = True
        if request.form['oldP'] == "" or request.form['newP'] == '' or request.form['newPC'] == '':
            flash("One or more invalid passwords")
        else:
            connection = sql.connect('database.db')
            cursor = connection.execute('SELECT * FROM User WHERE email = ?', (current_user.email,))
            row = cursor.fetchone()

            current_password = row[1]
            given_password = request.form['oldP']

            if comparePasswords(given_password, current_password):
                if request.form['newP'] == request.form['newPC']:
                    new_password = hash.new('md4', request.form['newPC'].encode()).hexdigest()
                    updatePassword(current_user.email, new_password)
                    wentThrough = True
                    flash('Updated password!')
                else:
                    flash('Confirmed Password does not match.')
                    wentThrough = False
            else:
                flash("Incorrect Password")
                wentThrough = False

    if request.method == 'GET':
        shouldFlash = False

    if userType == 'student':
        studentInfo = get_student_info(current_user.email)
        userInfo = get_user_info(current_user.email)
        zipcodeInfo = getZipcodeInfo(studentInfo[3])
        return render_template('userInfo.html', userInfo=userInfo, studentInfo=studentInfo, isStudent=True,
                               shouldFlash=shouldFlash, wentThrough=wentThrough, zipcodeInfo=zipcodeInfo)
    else:
        userInfo = get_user_info(current_user.email)
        profInfo = get_professor_info(current_user.email)
        return render_template('userInfo.html', userInfo=userInfo, profInfo=profInfo, isStudent=False,
                               shouldFlash=shouldFlash, wentThrough=wentThrough)


@app.route('/classInfo/<class_id>/Posts/<post_no>', methods=['POST'])
@login_required
def comment(class_id, post_no):
    if request.method == 'POST':
        theComment = request.form.get(post_no)

        if theComment != "":
            addComment(current_user.email, class_id, post_no, theComment)

        return redirect(url_for("displayPosts", class_id=class_id))


@app.route('/classSearch')
@login_required
def classSearch():
    classes = get_all_classes()
    first, second, third = [classes[start::3] for start in range(3)]
    num_classes = get_num_of_classes()
    return render_template('classSearch.html', first=first, second=second, third=third, num_classes=num_classes)


def get_posts(course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Posts WHERE course_id = ? ORDER BY post_no', (course_id,))
    result = cursor.fetchall()

    return result


def comparePasswords(given_password, current_password):
    given_password = hash.new('md4', given_password.encode()).hexdigest()
    if given_password == current_password:
        return True
    return False


def get_comments(post):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Comments WHERE course_id = ? AND post_no = ? ORDER BY comment_no',
                                (post[0], post[1],))
    result = cursor.fetchall()

    return result


def addComment(email, course_id, post_no, comment_contents):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT MAX(comment_no) FROM Comments WHERE course_id = ? AND post_no = ? ORDER BY post_no DESC',
        (course_id, post_no,))
    result = cursor.fetchone()

    if result[0]:
        comment_no = int(result[0] + 1)
    else:
        comment_no = 1

        post_no = int(post_no)

    connection.execute(
        'INSERT INTO Comments (course_id, post_no, comment_no, student_email, comment_content) VALUES (?,?,?,?,?);',
        (course_id, post_no, comment_no, email, comment_contents,))
    connection.commit()


def get_name(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT name FROM User WHERE email = ?', (email,))
    result = cursor.fetchone()
    return result[0]


def addPost(course_id, email, content):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT MAX(post_no) FROM Posts WHERE course_id = ?', (course_id,))
    result = cursor.fetchone()

    if result[0]:
        post_no = result[0] + 1
    else:
        post_no = 1

    connection.execute('INSERT INTO Posts (course_id, post_no, student_email, post_content) VALUES (?,?,?,?);',
                       (course_id, post_no, email, content,))
    connection.commit()


def isTAforClass(email, course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM TA_Teaching_Teams WHERE student_email = ?', (email,))
    result = cursor.fetchone()

    if result:
        tt_id = result[1]
    else:
        return False

    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Courses WHERE course_id = ?', (course_id,))
    result = cursor.fetchone()

    class_tt_id = result[3]

    if tt_id == class_tt_id:
        return True

    return False


def getZipcodeInfo(zipcode):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Zipcodes WHERE zipcode = ?', (zipcode,))
    result = cursor.fetchone()
    return result


def isProfForClass(email, course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Prof_Teaching_Teams WHERE prof_email = ?', (email,))
    result = cursor.fetchone()

    if result:
        tt_id = result[1]
    else:
        return False

    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Courses WHERE course_id = ?', (course_id,))
    result = cursor.fetchone()

    class_tt_id = result[3]

    if tt_id == class_tt_id:
        return True

    return False


def get_student_section(email, course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Enrolls WHERE student_email = ? AND course_id = ?', (email, course_id,))
    result = cursor.fetchone()

    return result


def updatePassword(email, newPassword):
    connection = sql.connect('database.db')
    connection.execute('UPDATE User SET password_hashed = ? WHERE email = ?', (newPassword, email))
    connection.commit()


def enrollUser(email, course_id, sec_no):
    connection = sql.connect('database.db')
    connection.execute('INSERT INTO Enrolls VALUES(?,?,?)', (email, course_id, sec_no,))
    connection.commit()

    assignments = get_homework(course_id, sec_no)
    for assignment in assignments:
        connection.execute(
            'INSERT OR IGNORE INTO Homework_Grades(student_email, course_id, sec_no, hw_no, grade) VALUES (?,?,?,?,?)',
            (email, course_id, sec_no, assignment[2], None))

    assignments = get_exams(course_id, sec_no)
    for assignment in assignments:
        connection.execute(
            'INSERT OR IGNORE INTO Exam_Grades(student_email, course_id, sec_no, exam_no, grade) VALUES (?,?,?,?,?)',
            (email, course_id, sec_no, assignment[2], None))


def canEnroll(email, course_id, sec_no):
    if get_user_type(email) == "professor":
        return False

    if isEnrolled(email, course_id):
        return False

    if isTAforClass(email, course_id):
        return False

    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT max_limit FROM Sections WHERE course_id = ? AND sec_no = ?',
                                (course_id, sec_no,))
    result = cursor.fetchone()
    max_Enrolled = result[0]

    cursor = connection.execute('SELECT COUNT(student_email) FROM Enrolls WHERE course_id = ? AND section_no = ?',
                                (course_id, sec_no,))
    result = cursor.fetchone()
    enrolled = result[0]

    if enrolled <= max_Enrolled:
        return True
    return False


def get_avg_hw_grade(email, course_id):
    section = get_student_section(email, course_id)
    section = section[2]

    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT AVG(grade) FROM Homework_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
        (email, course_id, section,))
    result = cursor.fetchone()[0]
    return result


def get_avg_exam_grade(email, course_id):
    section = get_student_section(email, course_id)
    section = section[2]

    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT AVG(grade) FROM Exam_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
        (email, course_id, section,))
    result = cursor.fetchone()[0]

    return result


def get_total_grade(email, course_id):
    section = get_student_section(email, course_id)
    section = section[2]

    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT SUM(grade) FROM Exam_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
        (email, course_id, section,))
    sumExamPoints = cursor.fetchone()[0]

    cursor = connection.execute(
        'SELECT COUNT(grade) FROM Exam_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
        (email, course_id, section,))
    totalExamPoints = cursor.fetchone()[0]

    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT SUM(grade) FROM Homework_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
        (email, course_id, section,))
    sumHWPoints = cursor.fetchone()[0]

    cursor = connection.execute(
        'SELECT COUNT(grade) FROM Homework_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
        (email, course_id, section,))
    totalHWPoints = cursor.fetchone()[0]

    if not sumHWPoints:
        sumHWPoints = 0
    if not sumExamPoints:
        sumExamPoints = 0
    if not totalHWPoints:
        totalHWPoints = 0
    if not totalExamPoints:
        totalExamPoints = 0

    if totalExamPoints + totalHWPoints == 0:
        return None

    totalGrade = (sumExamPoints + sumHWPoints) / (totalExamPoints + totalHWPoints)
    return totalGrade


def get_professor_contact(teaching_team_ID):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Prof_Teaching_Teams WHERE teaching_team_id = ?', (teaching_team_ID,))
    result = cursor.fetchone()

    cursor = connection.execute('SELECT * FROM Professors WHERE email = ?', (result[0],))
    result = cursor.fetchone()

    return result


def get_all_classes():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Courses')
    result = cursor.fetchall()

    return result


def get_num_of_classes():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT COUNT(course_id) FROM Courses')
    result = cursor.fetchone()

    return result[0]


def get_student_HW_grades(class_id, sec_no, assignment_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Homework_Grades WHERE course_id = ? AND sec_no = ? AND hw_no = ?',
                                (class_id, sec_no, assignment_no,))
    result = cursor.fetchall()
    return result


def get_student_exam_grades(class_id, sec_no, assignment_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Exam_Grades WHERE course_id = ? AND sec_no = ? AND exam_no = ?',
                                (class_id, sec_no, assignment_no,))
    result = cursor.fetchall()
    return result


def get_sections(course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Sections WHERE course_id = ?', (course_id,))
    result = cursor.fetchall()
    return result


def get_exams(course_id, sec_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Exams WHERE course_id = ? AND sec_no = ?', (course_id, sec_no,))
    result = cursor.fetchall()

    return result


def get_exam_grades(email, course_id, sec_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Exam_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
                                (email, course_id, sec_no,))
    result = cursor.fetchall()

    return result


def get_homework(course_id, sec_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Homework WHERE course_id = ? AND sec_no = ?', (course_id, sec_no,))
    result = cursor.fetchall()

    return result


def get_homework_grades(email, course_id, sec_no):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * FROM Homework_Grades WHERE student_email = ? AND course_id = ? AND sec_no = ?',
        (email, course_id, sec_no,))
    result = cursor.fetchall()

    return result


def get_enrolled_classes(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Enrolls WHERE student_email = ?', (email,))
    result = cursor.fetchall()

    classes = []

    for row in result:
        class_info = get_class_info(row[1])
        classes.append(class_info)

    return classes


def get_class_info(course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Courses WHERE course_id = ?', (course_id,))
    result = cursor.fetchone()
    return result


def get_user_info(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM User WHERE email = ?', (email,))
    result = cursor.fetchone()
    return result


def get_student_info(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Students WHERE email = ?', (email,))
    result = cursor.fetchone()
    return result


def get_professor_info(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Professors WHERE email = ?', (email,))
    result = cursor.fetchone()
    return result


def get_user_type(email):
    connection = sql.connect('database.db')

    cursor = connection.execute('SELECT * FROM Students WHERE email = ?', (email,))
    result = cursor.fetchone()
    if result:
        return "student"

    cursor = connection.execute('SELECT * FROM Professors WHERE email = ?', (email,))
    result = cursor.fetchone()
    if result:
        return "professor"

    return None


def get_Prof_TeachingTeams(email):
    connection = sql.connect('database.db')

    cursor = connection.execute('SELECT * FROM Prof_Teaching_Teams WHERE prof_email = ?', (email,))
    result = cursor.fetchone()
    return result


def get_taught_classes(email):
    connection = sql.connect('database.db')

    cursor = connection.execute('SELECT * FROM Prof_Teaching_Teams WHERE prof_email = ?', (email,))
    result = cursor.fetchone()

    if result:
        cursor = connection.execute('SELECT * FROM Courses WHERE teaching_team_id = ?', (result[1],))
        result = cursor.fetchall()
        return result

    return None


def get_TA_classes(email):
    connection = sql.connect('database.db')

    cursor = connection.execute('SELECT * FROM TA_Teaching_Teams WHERE student_email = ?', (email,))
    result = cursor.fetchone()

    if result:
        cursor = connection.execute('SELECT * FROM Courses WHERE teaching_team_id = ?', (result[1],))
        result = cursor.fetchall()
        return result


def isEnrolled(email, classID):
    connection = sql.connect('database.db')

    cursor = connection.execute('SELECT * FROM Enrolls WHERE student_email = ? AND course_id = ?', (email, classID,))
    result = cursor.fetchone()

    return result


def dropCourse(email, course_id, sec_no):
    connection = sql.connect('database.db')

    cursor = connection.execute('SELECT * FROM Enrolls WHERE student_email = ? AND course_id = ? AND section_no = ?',
                                (email, course_id, sec_no,))
    result = cursor.fetchone()

    if not result:
        return False

    dropDate = getDropDate(course_id)

    if dropDate:
        dropDate = datetime.strptime(dropDate, "%m/%d/%y")
        # currentDate = datetime.today()

        # This date is used to test the dropDate
        currentDate = datetime.strptime("4/5/04", "%m/%d/%y")

        if currentDate <= dropDate:
            # user is enrolled and within drop deadline, can drop!
            connection.execute('DELETE FROM Enrolls WHERE student_email = ? AND course_id = ? AND section_no = ?',
                               (email, course_id, sec_no,))
            connection.commit()

            connection.execute("DELETE FROM Posts WHERE student_email = ? AND course_id = ?", (email, course_id,))
            connection.commit()

            connection.execute("DELETE FROM Comments WHERE student_email = ? AND course_id = ?", (email, course_id,))
            connection.commit()
            return True
        else:
            return False


def getDropDate(course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Courses WHERE course_id = ?', (course_id,))
    result = cursor.fetchone()

    if result:
        return str(result[4])


def get_students_in_course_section(course_id, sec_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT student_email FROM Enrolls WHERE course_id = ? AND section_no = ?',
                                (course_id, sec_no,))
    result = cursor.fetchall()
    return result


def addHomework(course_id, sec_no, details):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT MAX(hw_no) FROM Homework WHERE course_id = ? AND sec_no = ?',
                                (course_id, sec_no,))
    result = cursor.fetchone()

    if result[0]:
        hw_no = int(result[0]) + 1
    else:
        hw_no = 1

    sec_no = int(sec_no)

    connection.execute('INSERT INTO Homework (course_id, sec_no, hw_no, hw_details) VALUES (?,?,?,?);',
                       (course_id, sec_no, hw_no, details,))

    connection.commit()

    students = get_students_in_course_section(course_id, sec_no)
    for student in students:
        connection.execute(
            'INSERT INTO Homework_Grades (student_email, course_id, sec_no, hw_no, grade) VALUES (?,?,?,?,?);',
            (student[0], course_id, sec_no, hw_no, None,))
        connection.commit()


def addExam(course_id, sec_no, details):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT MAX(exam_no) FROM Exams WHERE course_id = ? AND sec_no = ?',
                                (course_id, sec_no,))
    result = cursor.fetchone()

    if result[0]:
        exam_no = int(result[0]) + 1
    else:
        exam_no = 1

    sec_no = int(sec_no)

    connection.execute('INSERT INTO Exams (course_id, sec_no, exam_no, exam_details) VALUES (?,?,?,?);',
                       (course_id, sec_no, exam_no, details,))

    connection.commit()

    students = get_students_in_course_section(course_id, sec_no)
    for student in students:
        connection.execute(
            'INSERT INTO Exam_Grades (student_email, course_id, sec_no, exam_no, grade) VALUES (?,?,?,?,?);',
            (student[0], course_id, sec_no, exam_no, None,))
        connection.commit()


def change_hw_grade(email, class_id, sec_no, assignment_no, grade):
    connection = sql.connect('database.db')
    connection.execute(
        'UPDATE Homework_Grades SET grade = ? WHERE student_email = ? AND course_id = ? AND sec_no = ? AND hw_no = ?;',
        (grade, email, class_id, sec_no, assignment_no,))
    connection.commit()


def change_exam_grade(email, class_id, sec_no, assignment_no, grade):
    connection = sql.connect('database.db')
    connection.execute(
        'UPDATE Exam_Grades SET grade = ? WHERE student_email = ? AND course_id = ? AND sec_no = ? AND exam_no = ?;',
        (grade, email, class_id, sec_no, assignment_no,))
    connection.commit()


if __name__ == "__main__":
    app.run()
