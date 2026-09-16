from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# Exact exam-content isolation intentionally removed the old built-in question fallback.
# Support both shapes so this safety patch remains compatible with the current build.
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

# Clamp render-time access when a previous preview/session had more questions.
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

p.write_text(s)
print('student exam runtime guard applied compatibly with exact exam content')
