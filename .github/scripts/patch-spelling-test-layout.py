from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text()

# Detect spelling tests from the exact currently loaded/session exam only.
current_candidates = [
    '  const current = examContent?.questions[level] || [];',
    '  const current = examContent?.questions[level] || questions[level];',
]
current_anchor = next((x for x in current_candidates if x in s), None)
if not current_anchor:
    raise SystemExit('current question list anchor not found')
insert = '''  const isSpellingTest = /spelling/i.test(joinedSession?.examName || examName || "") || Boolean(examContent?.sourceText && /Part\\s*1\\s*[–-]\\s*Listen\\s*&\\s*Spell/i.test(examContent.sourceText) && /Part\\s*2\\s*[–-]\\s*Vocabulary\\s*in\\s*Context/i.test(examContent.sourceText));\n  const spellingPart1 = isSpellingTest ? current.slice(0, 10) : [];\n  const spellingPart2 = isSpellingTest ? current.slice(10, 20) : [];\n  const spellingCloseEnough = (value: string, expected: string) => {\n    const a = value.trim().toLowerCase();\n    const b = expected.trim().toLowerCase();\n    if (a === b) return true;\n    if (Math.abs(a.length - b.length) > 1) return false;\n    let i = 0, j = 0, edits = 0;\n    while (i < a.length && j < b.length) {\n      if (a[i] === b[j]) { i++; j++; continue; }\n      if (++edits > 1) return false;\n      if (a.length > b.length) i++;\n      else if (b.length > a.length) j++;\n      else { i++; j++; }\n    }\n    if (i < a.length || j < b.length) edits++;\n    return edits <= 1;\n  };\n'''
if 'const isSpellingTest =' not in s:
    s = s.replace(current_anchor, current_anchor + '\n' + insert, 1)

old_score = '  const score = useMemo(() => current.reduce((sum, q) => { const value = answers[q.id]; const correct = q.responseType === "short" ? (typeof value === "string" && value.trim() === (q.expectedText || "").trim()) : value === q.answer; return sum + (correct ? q.marks : 0); }, 0), [answers, current]);'
new_score = '  const score = useMemo(() => current.reduce((sum, q, index) => { const value = answers[q.id]; const expected = q.expectedText || ""; const correct = q.responseType === "short" ? (typeof value === "string" && (isSpellingTest ? (index < 10 ? value.trim().toLowerCase() === expected.trim().toLowerCase() : spellingCloseEnough(value, expected)) : value.trim() === expected.trim())) : value === q.answer; return sum + (correct ? q.marks : 0); }, 0), [answers, current, isSpellingTest]);'
if old_score in s:
    s = s.replace(old_score, new_score, 1)
elif new_score not in s:
    raise SystemExit('score anchor not found')

old_stat = '<div className="student-top-stat"><FileText size={18}/><span>Question</span><b>{currentQuestion + 1} / {current.length}</b></div>'
new_stat = '<div className="student-top-stat"><FileText size={18}/><span>{isSpellingTest ? "Questions" : "Question"}</span><b>{isSpellingTest ? `All ${current.length}` : `${currentQuestion + 1} / ${current.length}`}</b></div>'
if old_stat in s:
    s = s.replace(old_stat, new_stat, 1)
elif new_stat not in s:
    raise SystemExit('question top stat anchor not found')

# Preserve normal exam UI and switch spelling tests to a single-page two-column layout.
if 'className="spelling-test-grid"' not in s:
    pattern = re.compile(r'          <div className=\{`student-exam-grid \$\{textMaximized \? "text-is-max" : ""\}`\}>.*?          \{!textMaximized && <div className="question-dots">.*?</div>\}\n', re.S)
    m = pattern.search(s)
    if not m:
        raise SystemExit('student exam grid block not found')
    normal_block = m.group(0)
    spelling_block = '''          {isSpellingTest ? <div className="spelling-test-grid">
            <section className="spelling-part-card">
              <div className="spelling-section-head"><div><small>PART 1</small><h2>Listen &amp; Spell</h2></div><b>/10</b></div>
              <p className="spelling-instruction">Listen carefully. Write each word in the same numbered order you hear it.</p>
              <div className="spelling-word-list">{spellingPart1.map((q,index)=>{ const value=answers[q.id]; const expected=q.expectedText || ""; const correct=typeof value === "string" && value.trim().toLowerCase() === expected.trim().toLowerCase(); return <label key={q.id} className="spelling-word-row"><span>{index+1}.</span><input type="text" value={typeof value === "string" ? value : ""} disabled={submitted} autoComplete="off" spellCheck={false} onChange={(e)=>setAnswers((old)=>({...old,[q.id]:e.target.value}))} className={submitted ? (correct ? "correct" : "wrong") : ""} placeholder="Write the word" /></label>})}</div>
            </section>
            <section className="spelling-part-card">
              <div className="spelling-section-head"><div><small>PART 2</small><h2>Vocabulary in Context</h2></div><b>/10</b></div>
              <p className="spelling-instruction">Use the vocabulary from Part 1 to complete each sentence.</p>
              <div className="spelling-context-list">{spellingPart2.map((q,index)=>{ const value=answers[q.id]; const expected=q.expectedText || ""; const correct=typeof value === "string" && spellingCloseEnough(value, expected); return <div key={q.id} className="spelling-context-row"><p><b>{index+1}.</b> {q.prompt}</p><input type="text" value={typeof value === "string" ? value : ""} disabled={submitted} autoComplete="off" spellCheck={false} onChange={(e)=>setAnswers((old)=>({...old,[q.id]:e.target.value}))} className={submitted ? (correct ? "correct" : "wrong") : ""} placeholder="Vocabulary word" /></div>})}</div>
            </section>
          </div> : <>
''' + normal_block + '''          </>}
          {isSpellingTest && <div className="spelling-submit-row">{!submitted ? <button className="primary-button" disabled={answered!==current.length} onClick={()=>setSubmitted(true)}><CheckCircle2 size={18}/> Submit Spelling Test</button> : <div className="result"><CheckCircle2 size={22}/><div><b>{score} / {total}</b><small>Submitted</small></div></div>}</div>}
'''
    s = s[:m.start()] + spelling_block + s[m.end():]

p.write_text(s)

css = Path('app/globals.css')
c = css.read_text()
if '.spelling-test-grid' not in c:
    c += '''\n/* Dedicated spelling test: all 20 responses on one page */\n.spelling-test-grid{display:grid;grid-template-columns:1fr 1.15fr;gap:18px;margin-top:16px;align-items:start}.spelling-part-card{background:#fff;border:1px solid #dbe3ef;border-radius:18px;padding:20px;box-shadow:0 8px 22px rgba(15,35,64,.05)}.spelling-section-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;border-bottom:1px solid #e2e8f0;padding-bottom:12px;margin-bottom:10px}.spelling-section-head small{font-size:.72rem;font-weight:800;letter-spacing:.08em;color:#1d4ed8}.spelling-section-head h2{font-size:1.25rem;margin:2px 0 0;color:#0f172a}.spelling-section-head>b{color:#1d4ed8}.spelling-instruction{font-size:.9rem;color:#64748b;margin:0 0 14px}.spelling-word-list{display:grid;gap:9px}.spelling-word-row{display:grid;grid-template-columns:30px 1fr;align-items:center;gap:8px}.spelling-word-row>span{font-weight:800;color:#475569;text-align:right}.spelling-word-row input,.spelling-context-row input{width:100%;border:1.5px solid #cbd5e1;border-radius:10px;padding:10px 12px;font-size:.95rem;outline:none;background:#fff;color:#0f172a}.spelling-word-row input:focus,.spelling-context-row input:focus{border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,.1)}.spelling-context-list{display:grid;gap:10px}.spelling-context-row{border:1px solid #e2e8f0;border-radius:12px;padding:11px 12px;background:#f8fafc}.spelling-context-row p{margin:0 0 8px;color:#1e293b;line-height:1.45;font-size:.9rem}.spelling-word-row input.correct,.spelling-context-row input.correct{border-color:#16a34a;background:#f0fdf4}.spelling-word-row input.wrong,.spelling-context-row input.wrong{border-color:#dc2626;background:#fef2f2}.spelling-submit-row{display:flex;justify-content:center;margin:20px 0 4px}.spelling-submit-row .primary-button{min-width:220px}.spelling-submit-row .result{min-width:180px}@media(max-width:900px){.spelling-test-grid{grid-template-columns:1fr}.spelling-part-card{padding:16px}}\n'''
    css.write_text(c)

print('spelling-test mode applied compatibly with exact exam-session content')
