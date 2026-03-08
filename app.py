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
@app.route("/company/register", methods=["GET","POST"])
def company_register():

    if request.method == "POST":

        name = request.form["name"]
        hr = request.form["hr"]
        website = request.form["website"]

        company = Company(
            name=name,
            hr_contact=hr,
            website=website,
            approval_status="Pending"
        )

        db.session.add(company)
        db.session.commit()

        return redirect("/company/login")

    return render_template("company_register.html")
@app.route("/company/login", methods=["GET","POST"])
def company_login():

    if request.method == "POST":

        name = request.form["name"]

        company = Company.query.filter_by(name=name).first()

        if company and company.approval_status == "Approved":
            session["company"] = company.id
            return redirect("/company/dashboard")

    return render_template("company_login.html")


@app.route("/company/dashboard")
def company_dashboard():

    company_id = session.get("company")

    company = Company.query.get(company_id)

    jobs = JobPosition.query.filter_by(company_id=company_id).all()

    return render_template(
        "company_dashboard.html",
        company=company,
        jobs=jobs
    )
@app.route("/company/job/create", methods=["GET","POST"])
def create_job():

    company_id = session.get("company")

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        eligibility = request.form["eligibility"]
        salary = request.form["salary"]

        job = JobPosition(
            job_title=title,
            job_description=description,
            eligibility=eligibility,
            salary=salary,
            status="Pending",
            company_id=company_id
        )

        db.session.add(job)
        db.session.commit()

        return redirect("/company/dashboard")

    return render_template("create_job.html")
@app.route("/company/job/<int:id>/close")
def close_job(id):

    job = JobPosition.query.get(id)

    job.status = "Closed"

    db.session.commit()

    return redirect("/company/dashboard")
@app.route("/company/job/<int:id>/applications")
def view_applications(id):

    applications = Application.query.filter_by(job_id=id).all()

    return render_template(
        "company_applications.html",
        applications=applications
    )
@app.route("/company/application/<int:id>/<status>")
def update_application(id, status):

    application = Application.query.get(id)

    application.status = status

    db.session.commit()

    return redirect("/company/dashboard")
@app.route("/company/job/close/<int:id>")
def close_job(id):

    job = JobPosition.query.get(id)

    job.status = "Closed"

    db.session.commit()

    return redirect("/company/dashboard")
@app.route("/company/job/applications/<int:id>")
def job_applications(id):

    applications = Application.query.filter_by(job_id=id).all()

    return render_template(
        "company_applications.html",
        applications=applications
    )
@app.route("/company/application/shortlist/<int:id>")
def shortlist_student(id):

    application = Application.query.get(id)

    application.status = "Shortlisted"

    db.session.commit()

    return redirect(request.referrer)


@app.route("/company/application/reject/<int:id>")
def reject_student(id):

    application = Application.query.get(id)

    application.status = "Rejected"

    db.session.commit()

    return redirect(request.referrer)
if __name__ == "__main__":
    app.run(debug=True)