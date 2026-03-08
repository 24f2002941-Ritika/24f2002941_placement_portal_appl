from flask import Flask, render_template, request, redirect, session
from models import db, Admin, Student, Company, JobPosition, Application

app = Flask(__name__)
app.secret_key = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route("/")
def home():
    return redirect("/admin/login")


@app.route("/admin/login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username, password=password).first()

        if admin:
            session["admin"] = admin.id
            return redirect("/admin/dashboard")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():

    students = Student.query.count()
    companies = Company.query.count()
    jobs = JobPosition.query.count()
    applications = Application.query.count()

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        jobs=jobs,
        applications=applications
    )


@app.route("/admin/students")
def admin_students():

    students = Student.query.all()
    return render_template("admin_students.html", students=students)


@app.route("/admin/companies")
def admin_companies():

    companies = Company.query.all()
    return render_template("admin_companies.html", companies=companies)


@app.route("/admin/company/<int:id>/approve")
def approve_company(id):

    company = Company.query.get(id)
    company.approval_status = "Approved"

    db.session.commit()

    return redirect("/admin/companies")


@app.route("/admin/company/<int:id>/reject")
def reject_company(id):

    company = Company.query.get(id)
    company.approval_status = "Rejected"

    db.session.commit()

    return redirect("/admin/companies")


@app.route("/admin/company/<int:id>/deactivate")
def deactivate_company(id):

    company = Company.query.get(id)
    company.approval_status = "Blacklisted"

    db.session.commit()

    return redirect("/admin/companies")


@app.route("/admin/jobs")
def admin_jobs():

    jobs = JobPosition.query.all()
    return render_template("admin_jobs.html", jobs=jobs)


@app.route("/admin/job/<int:id>/approve")
def approve_job(id):

    job = JobPosition.query.get(id)
    job.status = "Approved"

    db.session.commit()

    return redirect("/admin/jobs")


@app.route("/admin/job/<int:id>/reject")
def reject_job(id):

    job = JobPosition.query.get(id)
    job.status = "Rejected"

    db.session.commit()

    return redirect("/admin/jobs")


@app.route("/admin/applications")
def admin_applications():

    applications = Application.query.all()
    return render_template("admin_applications.html", applications=applications)


@app.route("/admin/search_students", methods=["GET","POST"])
def search_students():

    students = []

    if request.method == "POST":
        query = request.form["query"]

        students = Student.query.filter(
            Student.name.contains(query)
        ).all()

    return render_template("search_students.html", students=students)


@app.route("/admin/search_companies", methods=["GET","POST"])
def search_companies():

    companies = []

    if request.method == "POST":

        query = request.form["query"]

        companies = Company.query.filter(
            Company.name.contains(query)
        ).all()

    return render_template("search_companies.html", companies=companies)


if __name__ == "__main__":
    app.run(debug=True)