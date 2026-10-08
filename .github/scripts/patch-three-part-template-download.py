from pathlib import Path
p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")
anchor='href="/english-exam-platform/Multi-Text-Reading-Exam-Template.docx"'
if s.count(anchor)!=1:
 raise RuntimeError("Existing multi-text template link missing; refusing unsafe UI change")
link='<a className="secondary-button inline-flex items-center gap-2" href="/english-exam-platform/Three-Part-English-Exam-Template.docx" download="Three-Part-English-Exam-Template.docx"><FileText size={16} /> Three-part exam template</a>'
# Insert after the existing multi-text template button, without altering old links.
end=s.find('</a>',s.index(anchor))
if end<0:raise RuntimeError("Template link closing tag missing")
end+=len('</a>')
s=s[:end]+link+s[end:]
p.write_text(s,encoding="utf-8")
print("Three-part Word template download added beside existing teacher templates")
