from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False); password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(30),default="recruiter"); created_at=db.Column(db.DateTime,default=datetime.utcnow)
    jobs=db.relationship("Job",backref="owner",cascade="all, delete-orphan")
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)

class Job(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    title=db.Column(db.String(150),nullable=False); department=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(100),nullable=False); employment_type=db.Column(db.String(60),nullable=False)
    description=db.Column(db.Text,nullable=False); required_skills=db.Column(db.Text,nullable=False)
    preferred_skills=db.Column(db.Text,default=""); experience_required=db.Column(db.String(60),default="0 years")
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    screenings=db.relationship("ScreeningResult",backref="job",cascade="all, delete-orphan")

class Resume(db.Model):
    id=db.Column(db.Integer,primary_key=True); filename=db.Column(db.String(255),nullable=False)
    candidate_name=db.Column(db.String(120),nullable=False); email=db.Column(db.String(150),default="")
    phone=db.Column(db.String(60),default=""); extracted_text=db.Column(db.Text,nullable=False)
    skills=db.Column(db.Text,default=""); education=db.Column(db.Text,default="")
    experience=db.Column(db.Text,default=""); projects=db.Column(db.Text,default="")
    certifications=db.Column(db.Text,default=""); uploaded_at=db.Column(db.DateTime,default=datetime.utcnow)
    screenings=db.relationship("ScreeningResult",backref="resume",cascade="all, delete-orphan")

class ScreeningResult(db.Model):
    id=db.Column(db.Integer,primary_key=True); job_id=db.Column(db.Integer,db.ForeignKey("job.id"),nullable=False)
    resume_id=db.Column(db.Integer,db.ForeignKey("resume.id"),nullable=False)
    similarity_score=db.Column(db.Float,default=0); skill_score=db.Column(db.Float,default=0)
    experience_score=db.Column(db.Float,default=0); final_score=db.Column(db.Float,default=0)
    matched_skills=db.Column(db.Text,default=""); missing_skills=db.Column(db.Text,default="")
    recommendation=db.Column(db.String(50),default="Low Match"); ai_summary=db.Column(db.Text,default="")
    strengths=db.Column(db.Text,default=""); weaknesses=db.Column(db.Text,default="")
    interview_questions=db.Column(db.Text,default=""); created_at=db.Column(db.DateTime,default=datetime.utcnow)
