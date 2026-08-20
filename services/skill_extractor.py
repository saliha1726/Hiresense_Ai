import re
SKILLS=["Python","Java","JavaScript","React","HTML","CSS","SQL","MySQL","MongoDB","Flask","Django","Node.js","C","C++","Machine Learning","Deep Learning","Artificial Intelligence","NLP","Data Science","Pandas","NumPy","Scikit-learn","TensorFlow","Power BI","Tableau","Excel","Git","GitHub","Docker","Kubernetes","AWS","Azure","Linux","Cybersecurity","Networking","Cloud Computing","REST API","Testing","Selenium"]
def extract_skills(text):
    low=text.lower(); found=[]
    for skill in SKILLS:
        if re.search(r"(?<![a-z0-9])"+re.escape(skill.lower())+r"(?![a-z0-9])",low):
            found.append(skill)
    return sorted(set(found))
