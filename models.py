from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Company(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    email = db.Column(db.String(200), unique=True)

    password = db.Column(db.String(200))

    hr_contact = db.Column(db.String(100))

    website = db.Column(db.String(200))

    approval_status = db.Column(db.String(50))

    jobs = db.relationship('JobPosition', backref='company', lazy=True)
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True)

    password = db.Column(db.String(200))

    education = db.Column(db.String(200))

    skills = db.Column(db.String(200))

    resume = db.Column(db.String(200))

    applications = db.relationship('Application', backref='student', lazy=True)

class JobPosition(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    job_title = db.Column(db.String(200))

    job_description = db.Column(db.Text)

    eligibility = db.Column(db.String(200))

    salary = db.Column(db.Integer)

    deadline = db.Column(db.String(100))

    status = db.Column(db.String(50))

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_date = db.Column(db.String(100))
    status = db.Column(db.String(50))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job_position.id'))

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salary = db.Column(db.Integer)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
