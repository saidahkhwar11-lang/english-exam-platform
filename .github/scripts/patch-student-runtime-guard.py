from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# Exact exam-content isolation intentionally removed the old built-in question fallback.
current_candidates = [
    '  const current = examContent?.questions[level] || [];',
    '  const current = examContent?.questions[level] || questions[level];',
]
current_anchor = next((x for x in current_candidates if x in s), None)
if not current_anchor:
    raise SystemExit('Current question-list anchor not found; refusing unsafe runtime patch.')

if 'const safeCurrentQuestion =' not in s:
    s = s.replace(
        current_anchor,
        current_anchor + '\n  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));',
        1,
    )

# Clamp all direct question access.
if 'current[currentQuestion]' in s:
    s = s.replace('current[currentQuestion]', 'current[safeCurrentQuestion]')
elif 'current[safeCurrentQuestion]' not in s:
    raise SystemExit('No current question access found; refusing unsafe runtime patch.')

reset_guard = '''\n  useEffect(() => {\n    if (current.length > 0 && currentQuestion !== safeCurrentQuestion) {\n      setCurrentQuestion(safeCurrentQuestion);\n    }\n  }, [current.length, safeCurrentQuestion, currentQuestion]);\n'''
if 'currentQuestion !== safeCurrentQuestion' not in s:
    s = s.replace(
        '  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));',
        '  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));' + reset_guard,
        1,
    )

# Critical empty-content guard: after removing the built-in sample fallback, current can
# legitimately be [] on the home/teacher screen. Never render current[0].id in that state.
question_panel_anchor = '{!textIsMaximized && (\n              <section className="question-panel">'
if question_panel_anchor in s:
    s = s.replace(
        question_panel_anchor,
        '{!textIsMaximized && current.length > 0 && (\n              <section className="question-panel">',
        1,
    )
elif '{!textIsMaximized && current.length > 0 && (' not in s:
    raise SystemExit('Question panel empty-content guard anchor not found; refusing unsafe runtime patch.')

p.write_text(s)
print('student runtime guard applied: safe index plus empty exam-content render protection')
