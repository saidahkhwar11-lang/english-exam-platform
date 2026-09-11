from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# Dedicated spelling-test renderer. This is intentionally isolated from normal
# reading/MCQ exams. It detects the uploaded spelling format from its source text.
anchor = '  const currentQuestions = examContent?.questions?.[studentLevel] || [];'
if anchor not in s:
    raise SystemExit('currentQuestions anchor not found')
insert = '''  const isSpellingTest = Boolean(examContent?.sourceText && /Part\\s*1\\s*[–-]\\s*Listen\\s*&\\s*Spell/i.test(examContent.sourceText) && /Part\\s*2\\s*[–-]\\s*Vocabulary\\s*in\\s*Context/i.test(examContent.sourceText));\n  const spellingQuestions = examContent?.questions?.[studentLevel] || [];\n  const spellingPart1 = isSpellingTest ? spellingQuestions.slice(0, 10) : [];\n  const spellingPart2 = isSpellingTest ? spellingQuestions.slice(10, 20) : [];\n\n'''
if 'const isSpellingTest =' not in s:
    s = s.replace(anchor, insert + anchor, 1)

# Insert a special student rendering branch immediately before the normal student test UI.
# The existing submitExam function remains the single submission/marking path.
student_anchor = '  if (access === "student" && joinedSession) {'
if student_anchor not in s:
    raise SystemExit('student render anchor not found')
branch = r'''  if (access === "student" && joinedSession && isSpellingTest) {
    return <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mx-auto max-w-[1500px]">
        <div className="mb-4 rounded-2xl border border-blue-100 bg-white px-5 py-4 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div><h1 className="text-2xl font-bold text-slate-900">{examContent?.title || "Spelling Test"}</h1><p className="mt-1 text-sm text-slate-500">{studentName} · {studentId}</p></div>
            <div className="rounded-xl bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-800">Spelling Test · /20</div>
          </div>
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4"><h2 className="text-xl font-bold text-slate-900">Part 1 – Listen &amp; Spell /10</h2><p className="mt-1 text-sm text-slate-600">Listen carefully. Write each word in the same numbered order you hear it.</p></div>
            <div className="space-y-3">{spellingPart1.map((q, i) => <label key={q.id || i} className="flex items-center gap-3"><span className="w-7 text-right font-bold text-slate-700">{i+1}.</span><input spellCheck={false} autoComplete="off" value={studentAnswers[q.id] || ""} onChange={e=>setStudentAnswers(a=>({...a,[q.id]:e.target.value}))} className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-blue-500" placeholder="Type the word" /></label>)}</div>
          </section>
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4"><h2 className="text-xl font-bold text-slate-900">Part 2 – Vocabulary in Context /10</h2><p className="mt-1 text-sm text-slate-600">Use the vocabulary from Part 1 to complete each sentence.</p></div>
            <div className="space-y-4">{spellingPart2.map((q, i) => <div key={q.id || i} className="rounded-xl border border-slate-200 p-3"><div className="mb-2 text-sm font-medium leading-6 text-slate-800"><span className="mr-2 font-bold">{i+1}.</span>{q.prompt}</div><input spellCheck={false} autoComplete="off" value={studentAnswers[q.id] || ""} onChange={e=>setStudentAnswers(a=>({...a,[q.id]:e.target.value}))} className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500" placeholder="Type the vocabulary word" /></div>)}</div>
          </section>
        </div>
        <div className="mt-5 flex justify-center"><button type="button" onClick={submitExam} disabled={studentSubmitted} className="rounded-xl bg-blue-700 px-10 py-3 font-bold text-white shadow-sm disabled:opacity-50">{studentSubmitted ? "Submitted" : "Submit Spelling Test"}</button></div>
      </div>
    </main>;
  }

'''
if 'Submit Spelling Test' not in s:
    s = s.replace(student_anchor, branch + student_anchor, 1)

# Part 1 marking: exact spelling and exact numbered position, but case-insensitive.
# Preserve trimming of accidental surrounding whitespace.
old = 'const normalizeStrictAnswer = (value: string) => value.trim();'
if old in s:
    s = s.replace(old, 'const normalizeStrictAnswer = (value: string) => value.trim();', 1)

p.write_text(s)
print('dedicated spelling-test two-column student layout applied')
