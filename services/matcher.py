import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from services.skill_extractor import extract_skills
def text_similarity(a,b):
    try: return round(float(cosine_similarity(TfidfVectorizer(stop_words="english").fit_transform([a,b]))[0,1])*100,2)
    except Exception: return 0.0
def skill_match(required,resume_skills):
    req=[x.strip().lower() for x in required.split(",") if x.strip()]
    got={x.lower() for x in resume_skills}
    matched=[x for x in req if x in got]; missing=[x for x in req if x not in got]
    return (round(len(matched)/len(req)*100,2) if req else 100.0), matched, missing
def experience_score(required,text):
    m=re.search(r"\d+",required or "0"); need=int(m.group()) if m else 0
    years=[int(x) for x in re.findall(r"(\d+)\s*(?:\+\s*)?(?:years?|yrs?)",text,re.I)]
    have=max(years,default=0)
    if need<=0:return 100.0
    if not years:return 50.0
    return round(min(have/need,1)*100,2)
def recommendation(s):
    return "Strong Match" if s>=80 else "Good Match" if s>=65 else "Potential Match" if s>=50 else "Low Match"
def screen(job,resume,weights=None):
    w=weights or {"similarity":.6,"skills":.3,"experience":.1}
    sim=text_similarity(f"{job.title} {job.description} {job.required_skills} {job.preferred_skills}",resume.extracted_text)
    skills=extract_skills(resume.extracted_text); ss,matched,missing=skill_match(job.required_skills,skills)
    es=experience_score(job.experience_required,resume.extracted_text)
    final=round(sim*w["similarity"]+ss*w["skills"]+es*w["experience"],2)
    return dict(similarity_score=sim,skill_score=ss,experience_score=es,final_score=final,
                matched_skills=", ".join(matched),missing_skills=", ".join(missing),recommendation=recommendation(final))
