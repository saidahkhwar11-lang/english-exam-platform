from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()
anchor = '  const isSpellingTest = current.length > 0 && current.every((q) => q.responseType === "short" && /Spelling Part [12]/i.test(q.skill || ""));'
if anchor not in s:
    raise SystemExit('Spelling MCQ patch must run first')
s = s.replace(anchor, anchor + '\n  const hasReadingPassage = Boolean(examContent?.passages[level]?.trim());', 1)
s = s.replace('className={`student-exam-grid ${textMaximized ? "text-is-max" : ""}`}', 'className={`student-exam-grid ${hasReadingPassage ? (textMaximized ? "text-is-max" : "") : "without-passage"}`}', 1)
start = '<section className="reading-panel"><div className="panel-title">'
if start not in s:
    raise SystemExit('Reading panel anchor missing')
s = s.replace(start, '{hasReadingPassage && <section className="reading-panel"><div className="panel-title">', 1)
end = '<p>{examContent?.passages[level] || ""}</p></div></section>'
if end not in s:
    raise SystemExit('Reading panel end anchor missing')
s = s.replace(end, '<p>{examContent?.passages[level] || ""}</p></div></section>}', 1)
s = s.replace('current.length > 0 && !textMaximized && <section className="question-panel"', 'current.length > 0 && (!hasReadingPassage || !textMaximized) && <section className="question-panel"', 1)
s = s.replace('{!textMaximized && <div className="question-dots">', '{(!hasReadingPassage || !textMaximized) && <div className="question-dots">', 1)
p.write_text(s)

c = Path('app/globals.css')
css = c.read_text()
css += '\n.student-exam-grid.without-passage{grid-template-columns:minmax(0,1fr);min-height:0}.student-exam-grid.without-passage .question-panel{min-height:480px}\n'
c.write_text(css)
print('Empty reading panel hidden and question area expanded')
