from pathlib import Path

page = Path('app/page.tsx')
source = page.read_text(encoding='utf-8')
anchor = '<span>Teacher test with answer key</span>'
if source.count(anchor) != 1:
    raise SystemExit('Teacher upload section not found; no changes applied')

replacement = '''<div className="flex flex-wrap items-center justify-between gap-2"><span>Teacher test with answer key</span><a className="secondary-button inline-flex items-center gap-2" href="/english-exam-platform/Sample-English-Exam-Template.docx" download="Sample-English-Exam-Template.docx"><FileText size={16} /> Download sample template</a></div><p className="text-sm leading-6 text-slate-600">Use numbered questions with A–C or A–D choices, with or without a reading passage. The Answer Key may be numbered (1. B, 2. C) or list one letter per line in question order.</p>'''
page.write_text(source.replace(anchor, replacement, 1), encoding='utf-8')
print('Teacher exam template download and format guide added')
