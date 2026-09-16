from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Normalize DOCX/table and inline A-D option boundaries before the existing
# Exam Platform parser runs. Using a callable replacement is intentional:
# Python re.sub otherwise interprets TypeScript regex escapes such as \u00a0.
pattern = r'const normalizeLines = \(text: string\) => .*?;'
replacement = r'''const normalizeLines = (text: string) => text
    .replace(/\r/g, "")
    .replace(/\t+/g, "\n")
    .replace(/\u00a0/g, " ")
    .replace(/\s+([A-D])[.)]\s+(?=\S)/g, "\n$1. ")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);'''

s2, n = re.subn(pattern, lambda _m: replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Question-only MCQ parser anchor not found; refusing silent patch')

# Question-only quizzes should not manufacture a reading passage from headings.
needle = "const passage=passageLines.join('\\n\\n');"
if needle in s2:
    s2 = s2.replace(needle, "const passage = qs.length && passageLines.some(line => /reading|passage|text/i.test(line)) ? passageLines.join('\\n\\n') : '';", 1)

p.write_text(s2, encoding='utf-8')
print('question-only MCQ parser normalization applied')
