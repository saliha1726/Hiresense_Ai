import re, fitz, docx
def extract_text_from_pdf(path):
    with fitz.open(path) as d: return "\n".join(p.get_text() for p in d)
def extract_text_from_docx(path):
    d=docx.Document(path); return "\n".join(p.text for p in d.paragraphs)
def extract_email(t):
    m=re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",t); return m.group(0) if m else "Not provided"
def extract_phone(t):
    m=re.search(r"(?:\+?\d[\d\s().-]{8,}\d)",t); return m.group(0).strip() if m else "Not provided"
def extract_candidate_name(t,filename):
    for line in t.splitlines()[:8]:
        s=line.strip()
        if 1<len(s.split())<=4 and not re.search(r"@|resume|curriculum|phone|linkedin",s,re.I): return s.title()
    return re.sub(r"[_-]+"," ",filename.rsplit(".",1)[0]).title()
def section(t,heads):
    lines=t.splitlines(); out=[]; take=False
    allheads=["education","experience","employment","projects","skills","certifications","summary"]
    for line in lines:
        s=line.strip(); low=s.lower()
        if any(h in low for h in heads) and len(s)<40: take=True; continue
        if take and any(h in low for h in allheads) and len(s)<40: break
        if take and s: out.append(s)
    return "\n".join(out[:25]) or "Not clearly detected."
def parse_resume(path,filename):
    raw=extract_text_from_pdf(path) if filename.lower().endswith(".pdf") else extract_text_from_docx(path)
    if not raw.strip(): raise ValueError("No readable text was found in the file.")
    return dict(candidate_name=extract_candidate_name(raw,filename),email=extract_email(raw),phone=extract_phone(raw),
      extracted_text=raw,education=section(raw,["education","qualification"]),experience=section(raw,["experience","employment"]),
      projects=section(raw,["projects"]),certifications=section(raw,["certifications","courses"]))
