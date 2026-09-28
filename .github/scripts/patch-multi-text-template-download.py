from pathlib import Path
p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")
anchor='''<a className="secondary-button inline-flex items-center gap-2" href="/english-exam-platform/Sample-English-Exam-Template.docx" download="Sample-English-Exam-Template.docx"><FileText size={16} /> Download sample template</a>'''
replacement=anchor+'''<a className="secondary-button inline-flex items-center gap-2" href="/english-exam-platform/Multi-Text-Reading-Exam-Template.docx" download="Multi-Text-Reading-Exam-Template.docx"><FileText size={16} /> Multi-text reading template</a>'''
if 'Multi-Text-Reading-Exam-Template.docx' not in s:
    if anchor not in s: raise SystemExit("sample template button not found")
    s=s.replace(anchor,replacement,1)
old='''Use numbered questions with A–C or A–D choices, with or without a reading passage. The Answer Key may be numbered (1. B, 2. C) or list one letter per line in question order.'''
new='''Use numbered questions with A–C or A–D choices. For a reading exam with several passages, use the Multi-text reading template: Text 1 + its questions, then Text 2 + its questions, then Text 3, and keep one Answer Key at the end.'''
if old in s:s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("Multi-text teacher template download added")
