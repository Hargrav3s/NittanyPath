import hashlib as h
import sqlite3 as sql
import pandas as pd

def populate():

    connection = sql.connect('database.db')

    with open('createTables.sql') as sql_file:
        sql_as_string = sql_file.read()
        connection.executescript(sql_as_string)

    students_data = pd.read_csv('Students_TA.csv')
    professors_data = pd.read_csv('Professors.csv')
    post_data = pd.read_csv("Posts_Comments.csv")

    # Student File Extraction

    for col, row in students_data.iterrows():

        name = row['Full Name']
        email = row['Email']
        age = int(row['Age'])
        zip_code = int(row['Zip'])
        phone = int(row['Phone'])
        gender = row['Gender']
        city = row['City']
        state = row['State']
        hashed_password = h.new('md4', row['Password'].encode()).hexdigest()
        street = row['Street']
        major = row['Major']

        #############################################################################################################################################################

        # Adds zip codes into database
        connection.execute('INSERT or IGNORE INTO Zipcodes (zipcode, city, state) VALUES (?,?,?);', (zip_code, city, state))
        connection.commit()

        #############################################################################################################################################################

        # Adds students into User Database and Student database
        connection.execute(
            'INSERT or IGNORE INTO User (email, password_hashed, name, age, gender) VALUES (?,?,?,?,?);',
            (email, hashed_password, name, age, gender))
        connection.commit()

        connection.execute(
            'INSERT or IGNORE INTO Students (email, phone, major, zipcode) VALUES (?,?,?,?);',
            (email, phone, major, zip_code))
        connection.commit()

        #############################################################################################################################################################

        # Adds Course into database
        connection.execute('INSERT or IGNORE INTO Courses (course_id, course_name, course_desc) VALUES (?,?,?);',
                        (row['Courses 1'], row['Course 1 Name'], row['Course 1 Details']))
        connection.commit()

        connection.execute('INSERT or IGNORE INTO Courses (course_id, course_name, course_desc) VALUES (?,?,?);',
                        (row['Courses 2'], row['Course 2 Name'], row['Course 2 Details']))
        connection.commit()

        connection.execute('INSERT or IGNORE INTO Courses (course_id, course_name, course_desc) VALUES (?,?,?);',
                        (row['Courses 3'], row['Course 3 Name'], row['Course 3 Details']))
        connection.commit()

        #############################################################################################################################################################

        # Adds Section into database

        connection.execute('INSERT or IGNORE INTO Sections (course_id, sec_no, max_limit) VALUES (?,?,?);',
                        (row['Courses 1'], row['Course 1 Section'], row['Course 1 Section Limit']))
        connection.commit()

        connection.execute('INSERT or IGNORE INTO Sections (course_id, sec_no, max_limit) VALUES (?,?,?);',
                        (row['Courses 2'], row['Course 2 Section'], row['Course 2 Section Limit']))
        connection.commit()

        connection.execute('INSERT or IGNORE INTO Sections (course_id, sec_no, max_limit) VALUES (?,?,?);',
                        (row['Courses 3'], row['Course 3 Section'], row['Course 3 Section Limit']))
        connection.commit()

        #############################################################################################################################################################

        # Adds Enrolled data to database
        connection.execute('INSERT or IGNORE INTO Enrolls (student_email, course_id, section_no) VALUES (?,?,?)',
                        (email, row['Courses 1'], row['Course 1 Section']))
        connection.commit()

        connection.execute('INSERT or IGNORE INTO Enrolls (student_email, course_id, section_no) VALUES (?,?,?)',
                        (email, row['Courses 2'], row['Course 2 Section']))
        connection.commit()

        connection.execute('INSERT or IGNORE INTO Enrolls (student_email, course_id, section_no) VALUES (?,?,?)',
                        (email, row['Courses 3'], row['Course 3 Section']))
        connection.commit()

        #############################################################################################################################################################

        # Adds Homework data to database
        if not (str(row['Course 1 HW_No']) == 'nan'):
            connection.execute('INSERT or IGNORE INTO Homework (course_id, sec_no, hw_no, hw_details) VALUES (?,?,?,?);', (
                row['Courses 1'], row['Course 1 Section'], row['Course 1 HW_No'], row['Course 1 HW_Details']))
            connection.commit()

        if not (str(row['Course 2 HW_No']) == 'nan'):
            connection.execute('INSERT or IGNORE INTO Homework (course_id, sec_no, hw_no, hw_details) VALUES (?,?,?,?);', (
                row['Courses 2'], row['Course 2 Section'], row['Course 2 HW_No'], row['Course 2 HW_Details']))
            connection.commit()

        if not (str(row['Course 3 HW_No']) == 'nan'):
            connection.execute('INSERT or IGNORE INTO Homework (course_id, sec_no, hw_no, hw_details) VALUES (?,?,?,?);', (
                row['Courses 3'], row['Course 3 Section'], row['Course 3 HW_No'], row['Course 3 HW_Details']))
            connection.commit()

        #############################################################################################################################################################

        # Adds Exams data to database
        if not (str(row['Course 1 EXAM_No']) == 'nan'):
            connection.execute('INSERT or IGNORE INTO Exams (course_id, sec_no, exam_no, exam_details) VALUES (?,?,?,?);', (
                row['Courses 1'], row['Course 1 Section'], row['Course 1 EXAM_No'], row['Course 1 Exam_Details']))
            connection.commit()

        if not (str(row['Course 2 EXAM_No']) == 'nan'):
            connection.execute('INSERT or IGNORE INTO Exams (course_id, sec_no, exam_no, exam_details) VALUES (?,?,?,?);', (
                row['Courses 2'], row['Course 2 Section'], row['Course 2 EXAM_No'], row['Course 2 Exam_Details']))
            connection.commit()

        if not (str(row['Course 3 EXAM_No']) == 'nan'):
            connection.execute('INSERT or IGNORE INTO Exams (course_id, sec_no, exam_no, exam_details) VALUES (?,?,?,?);', (
                row['Courses 3'], row['Course 3 Section'], row['Course 3 EXAM_No'], row['Course 3 Exam_Details']))
            connection.commit()

        #############################################################################################################################################################

        # Adds Homework grades data to database
        if not (str(row['Course 1 HW_No']) == 'nan'):
            connection.execute(
                'INSERT or IGNORE INTO Homework_Grades (student_email, course_id, sec_no, hw_no, grade) VALUES (?,?,?,?,?);',
                (email, row['Courses 1'], row['Course 1 Section'], row['Course 1 HW_No'], row['Course 1 HW_Grade']))
            connection.commit()

        if not (str(row['Course 2 HW_No']) == 'nan'):
            connection.execute(
                'INSERT or IGNORE INTO Homework_Grades (student_email, course_id, sec_no, hw_no, grade) VALUES (?,?,?,?,?);',
                (email, row['Courses 2'], row['Course 2 Section'], row['Course 2 HW_No'], row['Course 2 HW_Grade']))
            connection.commit()

        if not (str(row['Course 3 HW_No']) == 'nan'):
            connection.execute(
                'INSERT or IGNORE INTO Homework_Grades (student_email, course_id, sec_no, hw_no, grade) VALUES (?,?,?,?,?);',
                (email, row['Courses 3'], row['Course 3 Section'], row['Course 3 HW_No'], row['Course 3 HW_Grade']))
            connection.commit()

        #############################################################################################################################################################

        # Adds Exam grades data to database
        if not (str(row['Course 1 EXAM_No']) == 'nan'):
            connection.execute(
                'INSERT or IGNORE INTO Exam_Grades (student_email, course_id, sec_no, exam_no, grade) VALUES (?,?,?,?,?);',
                (email, row['Courses 1'], row['Course 1 Section'], row['Course 1 EXAM_No'], row['Course 1 EXAM_Grade']))
            connection.commit()

        if not (str(row['Course 2 EXAM_No']) == 'nan'):
            connection.execute(
                'INSERT or IGNORE INTO Exam_Grades (student_email, course_id, sec_no, exam_no, grade) VALUES (?,?,?,?,?);',
                (email, row['Courses 2'], row['Course 2 Section'], row['Course 2 EXAM_No'], row['Course 2 EXAM_Grade']))
            connection.commit()

        if not (str(row['Course 3 EXAM_No']) == 'nan'):
            connection.execute(
                'INSERT or IGNORE INTO Exam_Grades (student_email, course_id, sec_no, exam_no, grade) VALUES (?,?,?,?,?);',
                (email, row['Courses 3'], row['Course 3 Section'], row['Course 3 EXAM_No'], row['Course 3 EXAM_Grade']))
            connection.commit()

        # They are apart of a teaching team
        if not (str(row['Teaching Team ID']) == 'nan'):
            connection.execute('INSERT or IGNORE INTO TA_Teaching_Teams (student_email, teaching_team_id) VALUES (?,?)',
                            (email, row['Teaching Team ID']))
            connection.commit()

    # Professor File Extraction

    for col, row in professors_data.iterrows():
        email = row['Email']
        hashed_password = h.new('md4', row['Password'].encode()).hexdigest()
        name = row['Name']
        age = int(row['Age'])
        gender = row['Gender']
        d_id = row['Department']
        office = row['Office']
        dname = row['Department Name']
        title = row['Title']
        t_id = int(row['Teaching Team ID'])

        connection.execute(
            'INSERT or IGNORE INTO User (email, password_hashed, name, age, gender) VALUES (?,?,?,?,?);',
            (email, hashed_password, name, age, gender))
        connection.commit()

        connection.execute(
            'INSERT or IGNORE INTO Professors (email, office_address, department, title) VALUES (?,?,?,?);',
            (email, office, d_id, title))
        connection.commit()

        #############################################################################################################################################################

        connection.execute('INSERT or IGNORE INTO Prof_Teaching_Teams (prof_email, teaching_team_id) VALUES (?,?);',
                        (email, t_id))
        connection.commit()

        #############################################################################################################################################################

        if title == "Head":
            connection.execute('INSERT or IGNORE INTO Departments (dept_id, dept_name, dept_head) VALUES (?,?,?);',
                            (d_id, dname, email))
            connection.commit()

        #############################################################################################################################################################

        connection.execute('UPDATE Courses SET teaching_team_id = ? WHERE course_id = ?', (t_id, row['Teaching']))
        connection.commit()

        #############################################################################################################################################################

    # Post_Comment Processing
    for col, row in post_data.iterrows():

        first = 1
        first1 = 1

        # Update course drop deadline
        connection.execute('UPDATE Courses SET late_drop_deadline = ? WHERE course_id = ?',
                        (row['Drop Deadline'], row['Courses']))
        connection.commit()

        #############################################################################################################################################################

        if str(row['Post 1 By']) != 'nan':
            connection.execute(
                'INSERT or IGNORE INTO Posts (course_id, post_no, student_email, post_content) VALUES (?,?,?,?);',
                (row['Courses'], 1, row['Post 1 By'], row['Post 1']))
            connection.commit()

        #############################################################################################################################################################

        if str(row['Comment 1 By']) != 'nan':
            connection.execute(
                'INSERT or IGNORE INTO Comments (course_id, post_no, comment_no, student_email, comment_content) VALUES (?,?,?,?,?);',
                (row['Courses'], 1, 1, row['Comment 1 By'], row['Comment 1']))
            connection.commit()

    connection.close()

if __name__ == "__main__":
    populate()