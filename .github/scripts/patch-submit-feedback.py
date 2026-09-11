from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Store per-question correctness once, during submit. This restores feedback
# without re-running answer checking during the submitted render.
state_anchor = '  const [finalScore, setFinalScore] = useState<number | null>(null);'
if state_anchor not in s:
    raise SystemExit('final score state anchor not found')
if 'const [answerFeedback, setAnswerFeedback]' not in s:
    s = s.replace(state_anchor, state_anchor + '\n  const [answerFeedback, setAnswerFeedback] = useState<Record<string, boolean>>({});', 1)

loop_anchors = [
    '      let calculated = 0;\n      for (const [index, q] of current.entries()) {',
    '      let calculated = 0;\n      for (const q of current) {',
]
loop_anchor = next((a for a in loop_anchors if a in s), None)
if not loop_anchor:
    raise SystemExit('submit loop anchor not found')
loop_replacement = loop_anchor.replace('      let calculated = 0;', '      let calculated = 0;\n      const feedback: Record<string, boolean> = {};', 1)
s = s.replace(loop_anchor, loop_replacement, 1)

correct_anchor = '''        if (correct) calculated += Number(q.marks) || 0;\n      }\n      setFinalScore(calculated);'''
if correct_anchor not in s:
    raise SystemExit('feedback calculation anchor not found')
s = s.replace(correct_anchor, '''        feedback[String(q.id)] = correct;\n        if (correct) calculated += Number(q.marks) || 0;\n      }\n      setAnswerFeedback(feedback);\n      setFinalScore(calculated);''', 1)

# Restore safe green/red feedback for spelling fields using only the cached map.
s = s.replace('const correct=false; return <label key={q.id}', 'const correct=Boolean(answerFeedback[String(q.id)]); return <label key={q.id}', 1)
s = s.replace('const correct=false; return <div key={q.id}', 'const correct=Boolean(answerFeedback[String(q.id)]); return <div key={q.id}', 1)
s = s.replace('className={submitted ? "submitted-answer" : ""} placeholder="Write the word"', 'className={submitted ? (correct ? "correct" : "wrong") : ""} placeholder="Write the word"', 1)
s = s.replace('className={submitted ? "submitted-answer" : ""} placeholder="Vocabulary word"', 'className={submitted ? (correct ? "correct" : "wrong") : ""} placeholder="Vocabulary word"', 1)

# Show the correct spelling answer only for responses that are actually wrong
# under the cached submit-time rule (Part 1 strict; Part 2 typo-tolerant).
s = s.replace('</label>})}</div>', '{submitted && !correct && <small className="short-answer-feedback">Correct answer: <b>{expected}</b></small>}</label>})}</div>', 1)
s = s.replace('</div>})}</div>\n            </section>', '{submitted && !correct && <small className="short-answer-feedback">Correct answer: <b>{expected}</b></small>}</div>})}</div>\n            </section>', 1)

# Normal short-answer tests also use cached feedback, avoiding answerMatches in render.
s = s.replace('className={`short-answer-input ${submitted ? "submitted-answer" : ""}`}', 'className={`short-answer-input ${submitted ? (answerFeedback[String(q.id)] ? "correct" : "wrong") : ""}`}', 1)

# Clear stale feedback when a new attempt/exam/level begins.
s = s.replace('setSubmitted(false); setCurrentQuestion(0);', 'setSubmitted(false); setAnswerFeedback({}); setFinalScore(null); setCurrentQuestion(0);')
s = s.replace('setAnswers({}); setSubmitted(false);', 'setAnswers({}); setSubmitted(false); setAnswerFeedback({}); setFinalScore(null);')

p.write_text(s, encoding='utf-8')
print('safe post-submit answer feedback applied')
