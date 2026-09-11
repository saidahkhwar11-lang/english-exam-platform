from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text()

# Prevent the student answer view from crashing if the active question index is
# briefly stale while an exam/session/level is changing, or if a malformed saved
# exam has no readable questions. Keep all normal question rendering unchanged.
patterns = [
    (
        'const q=current[currentQuestion], selected=answers[q.id];',
        'const safeQuestionIndex = Math.min(currentQuestion, Math.max(0, current.length - 1)); const q=current[safeQuestionIndex]; if (!q) return <div className="question-empty-state"><b>Test questions are still loading.</b><small>Please wait a moment and try again.</small></div>; const selected=answers[q.id];'
    ),
    (
        'const q = current[currentQuestion], selected = answers[q.id];',
        'const safeQuestionIndex = Math.min(currentQuestion, Math.max(0, current.length - 1)); const q = current[safeQuestionIndex]; if (!q) return <div className="question-empty-state"><b>Test questions are still loading.</b><small>Please wait a moment and try again.</small></div>; const selected = answers[q.id];'
    ),
]

changed = False
for old, new in patterns:
    if old in s:
        s = s.replace(old, new, 1)
        changed = True
        break

if not changed:
    # Tolerate formatting changes introduced by previous build patches.
    rx = re.compile(r'const\s+q\s*=\s*current\[currentQuestion\]\s*,\s*selected\s*=\s*answers\[q\.id\]\s*;')
    repl = 'const safeQuestionIndex = Math.min(currentQuestion, Math.max(0, current.length - 1)); const q = current[safeQuestionIndex]; if (!q) return <div className="question-empty-state"><b>Test questions are still loading.</b><small>Please wait a moment and try again.</small></div>; const selected = answers[q.id];'
    s, n = rx.subn(repl, s, count=1)
    changed = n == 1

if not changed:
    raise SystemExit('Student question renderer anchor not found; refusing unsafe runtime patch.')

# Clamp an already-open question index whenever the active question list changes.
anchor = '  const total = current.reduce((sum, q) => sum + q.marks, 0);'
if anchor in s and 'currentQuestion >= current.length' not in s:
    guard = '''  useEffect(() => {\n    if (current.length && currentQuestion >= current.length) setCurrentQuestion(0);\n  }, [current.length, currentQuestion]);\n'''
    s = s.replace(anchor, guard + anchor, 1)

p.write_text(s)

css = Path('app/globals.css')
c = css.read_text()
if '.question-empty-state' not in c:
    c += '\n.question-empty-state{display:flex;min-height:220px;flex-direction:column;align-items:center;justify-content:center;gap:8px;text-align:center;color:#334155}.question-empty-state b{font-size:1.05rem;color:#0f172a}.question-empty-state small{color:#64748b}\n'
    css.write_text(c)

print('student exam runtime guard applied')
