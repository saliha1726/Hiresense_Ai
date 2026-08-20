import os
def generate_insights(job,resume,data):
    key=os.getenv("GEMINI_API_KEY","")
    if key:
        try:
            from google import genai
            client=genai.Client(api_key=key)
            prompt=f"""Analyze this resume for the job. Give a concise summary, strengths, weaknesses and 3 interview questions.
Job: {job.title}; Required skills: {job.required_skills}
Candidate: {resume.candidate_name}; Score: {data['final_score']}%
Matched: {data['matched_skills']}; Missing: {data['missing_skills']}
Resume: {resume.extracted_text[:5000]}"""
            text=client.models.generate_content(model="gemini-2.0-flash",contents=prompt).text
            return {"ai_summary":text,"strengths":"Gemini-generated strengths are included above.","weaknesses":"Gemini-generated weaknesses are included above.","interview_questions":"See the Gemini analysis above."}
        except Exception: pass
    return {"ai_summary":f"{resume.candidate_name} has a {data['recommendation']} profile for {job.title}, with an overall score of {data['final_score']}%.",
            "strengths":f"Matched skills: {data['matched_skills'] or 'No required skills detected.'}",
            "weaknesses":f"Missing skills: {data['missing_skills'] or 'No required skill gaps detected.'}",
            "interview_questions":"1. Explain a project using your strongest skill.\n2. How would you improve your missing skills?\n3. Describe how you solve a difficult technical problem."}
