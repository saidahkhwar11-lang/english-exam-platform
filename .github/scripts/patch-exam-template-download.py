from pathlib import Path

page = Path('app/page.tsx')
source = page.read_text(encoding='utf-8')
anchor = '<span>Teacher test with answer key</span>'
if source.count(anchor) != 1:
    raise SystemExit('Teacher upload section not found; no changes applied')

replacement = '''<div className="flex flex-wrap items-center justify-between gap-2"><span>Teacher test with answer key</span><a className="secondary-button inline-flex items-center gap-2" href="/english-exam-platform/Sample-English-Exam-Template.docx" download="Sample-English-Exam-Template.docx"><FileText size={16} /> Download sample template</a></div><p className="text-sm leading-6 text-slate-600">Edit the sample in Word. Use numbered questions, A–C or A–D choices, and a numbered Answer Key. For a question-only exam, remove the Reading Passage heading and text before uploading.</p>'''
page.write_text(source.replace(anchor, replacement, 1), encoding='utf-8')
print('Teacher exam template download and format guide added')
