from flask import Flask, render_template, request, redirect, session
from models import db, Admin, Student, Company, JobPosition, Application,Placement
from flask import jsonify
from flask import flash

app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.before_request
def setup_db():

    if not hasattr(app, "db_initialized"):

        with app.app_context():

            db.create_all()

            if not Admin.query.filter_by(username="admin").first():

                admin = Admin(
                    username="admin",
                    password="admin123"
                )

                db.session.add(admin)
                db.session.commit()

        app.db_initialized = True
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")       
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if not admin:
            flash("Admin does not exist")
            return redirect("/admin/login")

        if admin.password != password:
            flash("Incorrect password")
            return redirect("/admin/login")

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

    return render_template(
        "admin_applications.html",
        applications=applications
    )
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
        email = request.form["email"]
        password = request.form["password"]
        website = request.form["website"]

        existing = Company.query.filter_by(email=email).first()

        if existing:
            flash("Company email already exists")
            return redirect("/company/register")

        company = Company(
            name=name,
            email=email,
            password=password,
            website=website,
            approval_status="Pending"
        )

        db.session.add(company)
        db.session.commit()

        flash("Registration successful. Wait for admin approval.")

        return render_template("company_register_success.html")

    return render_template("company_register.html")
@app.route("/company/login", methods=["GET", "POST"])
def company_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        company = Company.query.filter_by(email=email).first()

        if not company:
            flash("Company does not exist")
            return redirect("/company/login")

        if company.password != password:
            flash("Invalid password")
            return redirect("/company/login")

        if company.approval_status == "Pending":
            flash("Your company registration is waiting for admin approval")
            return redirect("/company/login")

        if company.approval_status == "Rejected":
            flash("Your company registration was rejected by admin")
            return redirect("/company/login")

        if company.approval_status == "Blacklisted":
            flash("Your company account has been blacklisted")
            return redirect("/company/login")

        # Approved
        session["company"] = company.id
        return redirect("/company/dashboard")

    return render_template("company_login.html")
@app.route("/company/dashboard")
def company_dashboard():

    company_id = session.get("company")

    company = Company.query.get(company_id)

    jobs = JobPosition.query.filter_by(company_id=company_id).all()

    applications = Application.query.join(JobPosition).filter(
        JobPosition.company_id == company_id
    ).all()

    return render_template(
        "company_dashboard.html",
        company=company,
        jobs=jobs,
        applications=applications
    )
@app.route("/company/job/create", methods=["GET","POST"])
def create_job():

    company_id = session.get("company")

    company = Company.query.get(company_id)

    if company.approval_status != "Approved":
        return "Company not approved yet"

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        eligibility = request.form["eligibility"]
        salary = request.form["salary"]
        deadline = request.form["deadline"]

        job = JobPosition(
            job_title=title,
            job_description=description,
            eligibility=eligibility,
            salary=salary,
            deadline=deadline,
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
@app.route("/company/job/applications/<int:job_id>")
def view_applications(job_id):

    company_id = session.get("company")

    job = JobPosition.query.get(job_id)

    if job.company_id != company_id:
        return "Unauthorized"

    applications = Application.query.filter_by(job_id=job_id).all()

    return render_template(
        "company_applications.html",
        job=job,
        applications=applications
    )
@app.route("/company/application/<int:id>/<status>")
def update_application_status(id, status):

    application = Application.query.get(id)

    if not application:
        return "Application not found"

    application.status = status

    if status == "Placed":

        existing = Placement.query.filter_by(
            student_id=application.student_id,
            company_id=application.job.company_id
        ).first()

        if not existing:

            placement = Placement(
                student_id=application.student_id,
                company_id=application.job.company_id,
                salary=application.job.salary
            )

            db.session.add(placement)

    db.session.commit()

    return redirect(request.referrer)
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
@app.route("/company/application/select/<int:id>")
def select_student(id):

    application = Application.query.get(id)

    application.status = "Selected"

    db.session.commit()

    return redirect(request.referrer)

@app.route("/student/register", methods=["GET","POST"])
def student_register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        education = request.form["education"]
        skills = request.form["skills"]

        resume = request.files["resume"]
        resume_path = "static/resumes/" + resume.filename
        resume.save(resume_path)

        student = Student(
            name=name,
            email=email,
            password=password,
            education=education,
            skills=skills,
            resume=resume_path
        )

        db.session.add(student)
        db.session.commit()
        flash("Student registered successfully")
        return render_template("student_register_success.html")
        

    return render_template("student_register.html")
@app.route("/student/login", methods=["GET","POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(email=email).first()

        if not student:
            flash("Student does not exist")
            return redirect("/student/login")

        if student.password != password:
            flash("Incorrect password")
            return redirect("/student/login")

        session["student"] = student.id

        return redirect("/student/dashboard")

    return render_template("student_login.html")
@app.route("/student/dashboard", methods=["GET"])
def student_dashboard():

    query = request.args.get("q")

    if query:

        jobs = JobPosition.query.filter(
            JobPosition.status == "Approved",
            JobPosition.job_title.contains(query)
        ).all()

    else:

        jobs = JobPosition.query.filter_by(status="Approved").all()

    return render_template(
        "student_dashboard.html",
        jobs=jobs
    )
@app.route("/company/job/delete/<int:id>")
def delete_job(id):

    job = JobPosition.query.get(id)

    db.session.delete(job)

    db.session.commit()

    return redirect("/company/dashboard")
@app.route("/company/job/edit/<int:id>", methods=["GET","POST"])
def edit_job(id):

    job = JobPosition.query.get(id)

    if request.method == "POST":

        job.job_title = request.form["title"]
        job.job_description = request.form["description"]
        job.eligibility = request.form["eligibility"]
        job.salary = request.form["salary"]

        db.session.commit()

        return redirect("/company/dashboard")

    return render_template("edit_job.html", job=job)
from datetime import datetime

@app.route("/student/apply/<int:job_id>")
def apply_job(job_id):

    student_id = session.get("student")

    existing = Application.query.filter_by(
        student_id=student_id,
        job_id=job_id
    ).first()

    if existing:
        return "Already applied"

    application = Application(
        student_id=student_id,
        job_id=job_id,
        status="Applied",
        application_date=datetime.now()
    )

    db.session.add(application)
    db.session.commit()

    return redirect("/student/applications")
@app.route("/student/job/<int:job_id>")
def student_job_details(job_id):

    job = JobPosition.query.get(job_id)

    return render_template(
        "student_job_details.html",
        job=job
    )
@app.route("/student/applications")
def student_applications():

    student_id = session.get("student")

    applications = Application.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_applications.html",
        applications=applications
    )
@app.route("/student/placements")
def student_placements():

    student_id = session.get("student")

    if not student_id:
        return redirect("/student/login")

    placements = Placement.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_placements.html",
        placements=placements
    )
@app.route("/student/profile", methods=["GET","POST"])
def student_profile():

    student_id = session.get("student")

    student = Student.query.get(student_id)

    if request.method == "POST":

        student.education = request.form["education"]
        student.skills = request.form["skills"]

        resume = request.files["resume"]

        if resume.filename != "":
            path = "static/resumes/" + resume.filename
            resume.save(path)
            student.resume = path

        db.session.commit()

        return redirect("/student/dashboard")

    return render_template("student_profile.html", student=student)
@app.route("/api/students")
def api_students():

    students = Student.query.all()

    data = []

    for s in students:
        data.append({
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "skills": s.skills
        })

    return jsonify(data)
@app.route("/api/students/<int:id>")
def api_student(id):

    s = Student.query.get(id)

    data = {
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "skills": s.skills
    }

    return jsonify(data)

@app.route("/api/companies")
def api_companies():

    companies = Company.query.all()

    data = []

    for c in companies:
        data.append({
            "id": c.id,
            "name": c.name,
            "website": c.website,
            "status": c.approval_status
        })

    return jsonify(data)
if __name__ == "__main__":
    app.run(debug=True)