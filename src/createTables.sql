CREATE TABLE IF NOT EXISTS User (
    email TEXT,
    password_hashed TEXT,
    name TEXT,
    age int,
    gender CHAR,

    PRIMARY KEY (email)
);

CREATE TABLE IF NOT EXISTS Students (
    email TEXT,
    phone TEXT,
    major TEXT,
    zipcode int,

    PRIMARY KEY (email),
    FOREIGN KEY (email) REFERENCES User (email),
    FOREIGN KEY (major) REFERENCES Departments (dept_id),
    FOREIGN KEY (zipcode) REFERENCES Zipcodes (zipcode)
);

CREATE TABLE IF NOT EXISTS Zipcodes (
    zipcode int,
    city TEXT,
    state TEXT,

    PRIMARY KEY(zipcode)
);

CREATE TABLE IF NOT EXISTS Professors(
    email TEXT,
    office_address TEXT,
    department TEXT,
    title TEXT,

    PRIMARY KEY (email),
    FOREIGN KEY (email) REFERENCES User (email),
    FOREIGN KEY (department) REFERENCES Departments(dept_id)
);

CREATE TABLE IF NOT EXISTS Departments(
    dept_id TEXT,
    dept_name TEXT,
    dept_head TEXT,

    PRIMARY KEY (dept_id),
    FOREIGN KEY (dept_head) REFERENCES User (email)
);

CREATE TABLE IF NOT EXISTS Courses(
    course_id TEXT,
    course_name TEXT,
    course_desc TEXT,
    teaching_team_id int,
    late_drop_deadline TEXT,

    PRIMARY KEY (course_id),
    FOREIGN KEY (teaching_team_id) REFERENCES Prof_Teaching_Teams (teaching_team_id)
);

CREATE TABLE IF NOT EXISTS Sections(
    course_id TEXT,
    sec_no int,
    max_limit int,

    PRIMARY KEY (course_id, sec_no),
    FOREIGN KEY (course_id) REFERENCES Courses (course_id)
);

CREATE TABLE IF NOT EXISTS Enrolls (
    student_email TEXT,
    course_id TEXT,
    section_no int,

    PRIMARY KEY(student_email, course_id),
    FOREIGN KEY(student_email) REFERENCES User (email),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
);

CREATE TABLE IF NOT EXISTS Prof_Teaching_Teams (
    prof_email TEXT,
    teaching_team_id int,

    PRIMARY KEY (prof_email),
    FOREIGN KEY (prof_email) REFERENCES User (email)
);

CREATE TABLE IF NOT EXISTS TA_Teaching_Teams (
    student_email TEXT,
    teaching_team_id int,

    PRIMARY KEY (student_email),
    FOREIGN KEY (student_email) REFERENCES User (email)
);

CREATE TABLE IF NOT EXISTS Homework(
    course_id TEXT,
    sec_no INT,
    hw_no INT,
    hw_details TEXT,

    PRIMARY KEY (course_id, sec_no, hw_no),
    FOREIGN KEY (course_id) REFERENCES Sections (course_id),
    FOREIGN KEY (sec_no) REFERENCES Sections (sec_no)
);

CREATE TABLE IF NOT EXISTS Homework_Grades(
    student_email TEXT,
    course_id TEXT,
    sec_no INT,
    hw_no INT,
    grade INT,

    PRIMARY KEY (student_email, course_id, sec_no, hw_no),
    FOREIGN KEY (student_email) REFERENCES Students (email),
    FOREIGN KEY (course_id) REFERENCES Sections (course_id),
    FOREIGN KEY (sec_no) REFERENCES Sections (sec_no)
);

CREATE TABLE IF NOT EXISTS Exams(
    course_id TEXT,
    sec_no INT,
    exam_no INT,
    exam_details TEXT,

    PRIMARY KEY (course_id, sec_no, exam_no),
    FOREIGN KEY (course_id) REFERENCES Sections (course_id),
    FOREIGN KEY (sec_no) REFERENCES Sections (sec_no)
);

CREATE TABLE IF NOT EXISTS Exam_Grades(
    student_email TEXT,
    course_id TEXT,
    sec_no INT,
    exam_no INT,
    grade INT,

    PRIMARY KEY (student_email, course_id, sec_no, exam_no),
    FOREIGN KEY (student_email) REFERENCES Students (email),
    FOREIGN KEY (course_id) REFERENCES Sections (course_id),
    FOREIGN KEY (sec_no) REFERENCES Sections (sec_no)
);

CREATE TABLE IF NOT EXISTS Posts (
    course_id TEXT,
    post_no INT,
    student_email TEXT NOT NULL,
    post_content TEXT,

    PRIMARY KEY (course_id, post_no),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (student_email) REFERENCES User (email)
);

CREATE TABLE IF NOT EXISTS Comments(
    course_id TEXT,
    post_no INT,
    comment_no INT,
    student_email TEXT,
    comment_content TEXT,

    PRIMARY KEY (course_id, post_no, comment_no),
    FOREIGN KEY (course_id) REFERENCES Posts (course_id) ON DELETE CASCADE,
    FOREIGN KEY (post_no) REFERENCES Posts (post_no) ON DELETE CASCADE,
    FOREIGN KEY (student_email) REFERENCES User (email)
);
