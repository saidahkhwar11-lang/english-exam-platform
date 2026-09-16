from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# The core parser expects each A/B/C/D option on its own line. Word table cells can
# arrive as tabs or as one continuous line. Normalize those boundaries before the
# existing parser runs. This is deliberately limited to the Exam Platform parser.
pattern = r'const normalizeLines = \(text: string\) => .*?;'
replacement = r'''const normalizeLines = (text: string) => text
    .replace(/\r/g, "")
    .replace(/\t+/g, "\n")
    .replace(/\u00a0/g, " ")
    .replace(/\s+([A-D])[.)]\s+(?=\S)/g, "\n$1. ")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);'''

s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Question-only MCQ parser anchor not found; refusing silent patch')

# Keep question-only tests truly passage-free. The existing parser already builds
# questions and answer keys; this prevents headings/instructions before Q1 from
# being treated as a reading passage when the file is clearly a quiz.
needle = "const passage=passageLines.join('\\n\\n');"
if needle in s2:
    s2 = s2.replace(needle, "const passage = qs.length && passageLines.some(line => /reading|passage|text/i.test(line)) ? passageLines.join('\\n\\n') : '';", 1)

p.write_text(s2, encoding='utf-8')
print('question-only MCQ parser normalization applied')
