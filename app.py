import os, json
from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,flash,session
from werkzeug.utils import secure_filename
from config import Config
from models import db,User,Job,Resume,ScreeningResult
from services.resume_parser import parse_resume
from services.skill_extractor import extract_skills
from services.matcher import screen
from services.gemini_service import generate_insights

app=Flask(__name__); app.config.from_object(Config); db.init_app(app)
os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True); os.makedirs(os.path.join(app.root_path,"database"),exist_ok=True)

def login_required(f):
    @wraps(f)
    def w(*a,**kw):
        if "user_id" not in session: flash("Please log in first.","warning"); return redirect(url_for("login"))
        return f(*a,**kw)
    return w
def seed():
    db.create_all()
    admin=User.query.filter_by(email="admin@hiresense.ai").first()
    if not admin:
        admin=User(name="Demo Recruiter",email="admin@hiresense.ai"); admin.set_password("Admin@123"); db.session.add(admin); db.session.commit()
    if Job.query.count()==0:
        data=[
        ("Python Developer","IT","Mumbai","Full Time","Build Python web applications and REST services.","Python, Flask, SQL, Git, REST API","Docker, AWS","2 years"),
        ("Data Analyst","Analytics","Remote","Full Time","Analyze business data and create dashboards.","Python, SQL, Excel, Pandas, Power BI","Tableau","1 year"),
        ("Frontend Developer","IT","Bangalore","Full Time","Build responsive modern web interfaces.","HTML, CSS, JavaScript, React, Git","Node.js","3 years"),
        ("Software Tester","QA","Mumbai","Full Time","Test web applications and automate regression testing.","Testing, Selenium, SQL, Python","Git","1 year"),
        ("Data Scientist","Data","Remote","Full Time","Build machine learning models and analyze data.","Python, Pandas, NumPy, Scikit-learn, Machine Learning","TensorFlow","2 years")]
        for x in data: db.session.add(Job(user_id=admin.id,title=x[0],department=x[1],location=x[2],employment_type=x[3],description=x[4],required_skills=x[5],preferred_skills=x[6],experience_required=x[7]))
        db.session.commit()
@app.route("/")
def index(): return render_template("index.html")
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=User.query.filter_by(email=request.form.get("email","").lower().strip()).first()
        if u and u.check_password(request.form.get("password","")): session["user_id"]=u.id; session["user_name"]=u.name; return redirect(url_for("dashboard"))
        flash("Invalid email or password.","danger")
    return render_template("login.html")
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").lower().strip(); p=request.form.get("password","")
        if not name or not email or len(p)<6: flash("Enter all fields; password must be at least 6 characters.","danger")
        elif User.query.filter_by(email=email).first(): flash("Email already registered.","danger")
        else:
            u=User(name=name,email=email); u.set_password(p); db.session.add(u); db.session.commit(); flash("Registration successful.","success"); return redirect(url_for("login"))
    return render_template("register.html")
@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("index"))
@app.route("/dashboard")
@login_required
def dashboard():
    avg=db.session.query(db.func.avg(ScreeningResult.final_score)).scalar() or 0
    return render_template("dashboard.html",jobs=Job.query.count(),resumes=Resume.query.count(),screenings=ScreeningResult.query.count(),avg=round(avg,1),recent=ScreeningResult.query.order_by(ScreeningResult.created_at.desc()).limit(6).all())
@app.route("/jobs")
@login_required
def jobs(): return render_template("jobs.html",jobs=Job.query.order_by(Job.created_at.desc()).all())
@app.route("/jobs/create",methods=["GET","POST"])
@login_required
def create_job():
    if request.method=="POST":
        fields=["title","department","location","employment_type","description","required_skills","experience_required"]
        if not all(request.form.get(x,"").strip() for x in fields): flash("Please complete all required fields.","danger")
        else:
            j=Job(user_id=session["user_id"],title=request.form["title"],department=request.form["department"],location=request.form["location"],employment_type=request.form["employment_type"],description=request.form["description"],required_skills=request.form["required_skills"],preferred_skills=request.form.get("preferred_skills",""),experience_required=request.form["experience_required"])
            db.session.add(j); db.session.commit(); flash("Job created.","success"); return redirect(url_for("jobs"))
    return render_template("job_form.html",job=None)
@app.route("/jobs/<int:id>")
@login_required
def job_detail(id): return render_template("job_detail.html",job=Job.query.get_or_404(id))
@app.route("/jobs/<int:id>/edit",methods=["GET","POST"])
@login_required
def edit_job(id):
    j=Job.query.get_or_404(id)
    if request.method=="POST":
        for f in ["title","department","location","employment_type","description","required_skills","preferred_skills","experience_required"]: setattr(j,f,request.form.get(f,"").strip())
        db.session.commit(); flash("Job updated.","success"); return redirect(url_for("job_detail",id=id))
    return render_template("job_form.html",job=j)
@app.route("/jobs/<int:id>/delete",methods=["POST"])
@login_required
def delete_job(id): db.session.delete(Job.query.get_or_404(id)); db.session.commit(); flash("Job deleted.","success"); return redirect(url_for("jobs"))
@app.route("/resumes")
@login_required
def resumes(): return render_template("resumes.html",resumes=Resume.query.order_by(Resume.uploaded_at.desc()).all())
@app.route("/resumes/upload",methods=["GET","POST"])
@login_required
def upload_resume():
    if request.method=="POST":
        f=request.files.get("resume_file")
        if not f or not f.filename: flash("Choose a PDF or DOCX file.","danger")
        elif "." not in f.filename or f.filename.rsplit(".",1)[1].lower() not in app.config["ALLOWED_EXTENSIONS"]: flash("Only PDF and DOCX files are allowed.","danger")
        else:
            name=secure_filename(f.filename); path=os.path.join(app.config["UPLOAD_FOLDER"],name)
            try:
                f.save(path); d=parse_resume(path,name); skills=", ".join(extract_skills(d["extracted_text"]))
                r=Resume(filename=name,candidate_name=d["candidate_name"],email=d["email"],phone=d["phone"],extracted_text=d["extracted_text"],skills=skills,education=d["education"],experience=d["experience"],projects=d["projects"],certifications=d["certifications"])
                db.session.add(r); db.session.commit(); flash("Resume uploaded and parsed successfully.","success"); return redirect(url_for("resume_detail",id=r.id))
            except Exception as e:
                if os.path.exists(path): os.remove(path)
                flash("Could not process this resume. Please try another readable file.","danger")
    return render_template("upload_resume.html")
@app.route("/resumes/<int:id>")
@login_required
def resume_detail(id): return render_template("resume_detail.html",resume=Resume.query.get_or_404(id))
@app.route("/screening")
@login_required
def screening(): return render_template("screening.html",jobs=Job.query.all(),resumes=Resume.query.all())
@app.route("/screening/run",methods=["POST"])
@login_required
def run_screening():
    j=Job.query.get_or_404(request.form.get("job_id",type=int)); r=Resume.query.get_or_404(request.form.get("resume_id",type=int))
    data=screen(j,r,app.config["SCREENING_WEIGHTS"]); ai=generate_insights(j,r,data)
    result=ScreeningResult(job_id=j.id,resume_id=r.id,**data,**ai); db.session.add(result); db.session.commit()
    return redirect(url_for("screening_result",id=result.id))
@app.route("/screening/<int:id>")
@login_required
def screening_result(id): return render_template("screening_result.html",result=ScreeningResult.query.get_or_404(id))
@app.route("/candidates")
@login_required
def candidates():
    jid=request.args.get("job_id",type=int); q=ScreeningResult.query
    if jid:q=q.filter_by(job_id=jid)
    return render_template("candidates.html",results=q.order_by(ScreeningResult.final_score.desc()).all(),jobs=Job.query.all(),selected=jid)
@app.route("/candidates/<int:id>")
@login_required
def candidate_detail(id):
    r=Resume.query.get_or_404(id); return render_template("candidate_detail.html",resume=r,results=ScreeningResult.query.filter_by(resume_id=id).order_by(ScreeningResult.final_score.desc()).all())
@app.route("/analytics")
@login_required
def analytics():
    rec=db.session.query(ScreeningResult.recommendation,db.func.count(ScreeningResult.id)).group_by(ScreeningResult.recommendation).all()
    jobs=db.session.query(Job.title,db.func.avg(ScreeningResult.final_score)).join(ScreeningResult,Job.id==ScreeningResult.job_id).group_by(Job.id).all()
    return render_template("analytics.html",rec_labels=[x[0] for x in rec],rec_counts=[x[1] for x in rec],job_labels=[x[0] for x in jobs],job_scores=[round(x[1],1) for x in jobs])
@app.route("/report/<int:id>")
@login_required
def report(id): return render_template("report.html",result=ScreeningResult.query.get_or_404(id))
@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    u=User.query.get(session["user_id"])
    if request.method=="POST":
        u.name=request.form.get("name",u.name).strip()
        p=request.form.get("password","")
        if p: u.set_password(p)
        db.session.commit(); session["user_name"]=u.name; flash("Profile updated.","success")
    return render_template("profile.html",user=u)
@app.errorhandler(413)
def too_large(e): return render_template("500.html",message="File is larger than the 5 MB limit."),413
@app.errorhandler(404)
def not_found(e): return render_template("404.html"),404
@app.errorhandler(500)
def server_error(e): return render_template("500.html",message="Something went wrong. Please try again."),500
with app.app_context(): seed()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT",5000)),debug=False)
