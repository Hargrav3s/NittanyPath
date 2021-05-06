# CMPSC 431w NittanyPath-v1

This is the final prototype for my implementation of the NittanyPath Database Management System (DBMS).

This web application will serve as a login portal and interactive DBMS for students, 
teaching assistants (TAs), and faculty.

In this final prototype, I have fully implement the following features:
>1. A dynamic login and logout system.
>2. HTML url maps that fluently lead around the website.
>3. A dashboard for all types of users.
>4. A dynamic class information page which changes based on the type of user, if they're a TA, 
>enrolled, or the professor for the course
>5. A profile page where users can see their stored data and update their password.
>6. A class search page where students can enroll in classes.
>7. An assignments and exams page where students can see graded and ungraded assignments,
>professors will see the assignments for each section.
>8. A posts and comments page where students, TAs, and Professors can post questions and respond with comments. 
>9. A drop course option for enrolled students, allowing them to drop a given course. All posts and comments made by
>that student are immediately deleted as well as all comments attached to a post.
>10. An assignment and exam grader for professors. Professors can change grades of all assignments and exams.
>11. An assignment and exam creator for professors. Professors can create assignments and exams for a section of a class they 
>teach.
>
In this document, I will walk you through the steps to get a working copy of my project on your system, as well as explain 
its features.
## Getting Started
Within this zip folder is the entire project. The only thing you need to do is open the project through PyCharm professional.
However, if for some reason that fails, you only need these files:
- createTables.sql
- app.py
- database.db
- PopulateScript.py
- Students_TA.csv
- Professors.csv
- The entire templates folder

The templates folder contains all HTML pages used for this project. Each encoded with bootstrap logic and components.
### Prerequisites
All you need is the latest version of docker installed.

## Installation
Open a terminal and clone the repository into your system.
Then change into the repositories' directory.
Run the following command:
>docker build --tag nittanypath

Then the following command
>docker run -p 5000:5000 nittanypath

This will run the application in a docker container and is viewable at 0.0.0.0:5000.


## How the Project Works / How it was Made
The first step to this project was to create all of the SQL tables. I choose SQLite as the class
had previous practice with this package earlier in another assignment.

Using an SQL script file, I wrote the SQL statements of each table in that file and ran the script a few times,
dropping and modifying tables as need be until I had them how I believe was correct.

Once fully satisfied, I ran the script to get my empty tables. The next step was to populate them using the data given
in the .csv files.

I choose to use a Python script involving the Pandas library as the teaching assistance gave a nod to it's ease of use.
After sorting through online documentation, I was able to quickly read the .cvs files and obtain the rows of data.

The only thing to note here is how I stored the passwords. I choose the simple yet effective md4 hash function as a test,
but I would like to change this to a more secure design in the near future.

Finally, the main part of the project is displaying the data to the user in a meaningful way. 
This is done through a series of HTML pages run on Python using Flask.

Starting with the Front page, the user can click a button to navigate to the log-in page. Once there, the user
can enter an email and password. If the user enters no email, no password, or enters an incorrect password,
the message "incorrect username or password" is displayed to the user.

## Once Logged In
With a correct username and password from the database, the user is displayed a dashboard. This dashboard will appear different
for every user. Professors will see classes they teach, students will see class they are enrolled in, and TA's will see a mix of
classes they're taking and classes they are teaching in.

Users are displayed a nav bar at the top that allows them to get back to the dashboard, look up classes, access their profile, 
and logout. 

##Class Information
When a user clicks on a class info link, they will see different information based upon if they're enrolled or not, are a TA
for the class, or if they're the professor who teaches.

An enrolled student will see their average grades as well as button to navigate to individual grades, a post board, and a
drop class button that drops the class if the drop out criteria is met.

A TA will only see the posts page, where they can respond to users posts and comments.

A student who is not enrolled in the class will see a general information page for the course where they can choose to enroll.

Finally, a professor who is teaching the class, will see a hub where they can grade and create assignments of all students in
the course, as well as post to the posts hub.

Teachers who are not teaching the course will see a general information page but will not be able to enroll.

## Assignments Page
The assignments page is where enrolled students can see their grades and teaching professors can grade.

Professors will be able to click on an assignment for a given section and change all the grades for each student in that section.

All other users who try and access this page will be rerouted to the dashboard.

## Exams Page
This page is virtually the same as the assignments page but contains exams instead of assignments.

Users interact exactly the same with this page as the assignments page.
## Posts Page
This page allows students enrolled in the class (regardless of section), TAs, and teaching professors to post questions
and respond to those questions with comments. 

Any user stated above can do so and all other users who try and access this
page are rerouted to dashboard.
## Create Assignment Page
This page is exclusively for teaching professors. Professors who are teaching a class may create assignments and exams as they wish.

Once the professor adds the assignment or exam, all students in that section are given a NULL grade until the professor assigns a grade.
## How it works
Using a sqlite database with all the user, student, professor, class, etc. data is accessed when app.py is running and is transmitted
to urls using flask. Using custom built functions, my program updates and retrieves data to and from the database.

The database was built with a series of CREATE TABLE SQL statements found in createTable.sql. From their, I populate the database using
my PopulateScript.py which uses pandas to access the pre-made .csv files. From their, app.py uses flask to render my HTML pages found in
templates to display the database contents securely to users.
## Closing Remarks
Over 200 hours was poured into this project. I have had no prior knowledge to any of these materials, but despite that, this was a
welcoming challenge to take on for my junior year as a computer science student.

I have learned valuable tools that will continue to live on and show up in my career years down the road.

Please enjoy this fun project!
## Built With

* [PyCharm Professional IDE](https://www.jetbrains.com/pycharm/) - Used to create, design, and test project.
* [flask](https://palletsprojects.com/p/flask/) - Used to render HTML pages.
* [flask_login](https://flask-login.readthedocs.io/en/latest/) - Used to log users in and out.
* [flask_SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - Used to create a User class for flask_login.
* [SQLite3](https://www.sqlite.org/index.html) - Used for SQL database gets and requests.
* [Pandas](https://pandas.pydata.org/) - Used for data extraction of .csv files.
* [bootstrap](https://getbootstrap.com/) - Used for HTML components.


## Author
**Tyler Hargraves**

