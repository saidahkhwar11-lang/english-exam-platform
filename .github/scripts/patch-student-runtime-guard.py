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

# Empty content is now a valid state on teacher/home screens. Later layout patches can
# change the exact JSX wrapper, so do not fail deployment if no matching panel wrapper exists.
# Direct question reads are already clamped above; optional-chain the remaining common reads.
s = s.replace('current[safeCurrentQuestion].id', 'current[safeCurrentQuestion]?.id')
s = s.replace('current[safeCurrentQuestion].prompt', 'current[safeCurrentQuestion]?.prompt')
s = s.replace('current[safeCurrentQuestion].type', 'current[safeCurrentQuestion]?.type')
s = s.replace('current[safeCurrentQuestion].options', 'current[safeCurrentQuestion]?.options')
s = s.replace('current[safeCurrentQuestion].hint', 'current[safeCurrentQuestion]?.hint')
s = s.replace('current[safeCurrentQuestion].expectedText', 'current[safeCurrentQuestion]?.expectedText')

p.write_text(s)
print('student runtime guard applied safely for loaded and empty exam states')
