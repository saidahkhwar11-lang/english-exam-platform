from pathlib import Path

s = Path('app/page.tsx').read_text()
for needle in ['const current =', 'const q =', 'single-answer-list', 'Reading Text', 'Question {', 'student-layout', 'exam-shell']:
    i = s.find(needle)
    print('\n===== NEEDLE', needle, 'INDEX', i, '=====')
    if i >= 0:
        print(s[max(0, i-1800):i+4200])
raise SystemExit('SPELLING_LAYOUT_STRUCTURE_CAPTURE')
