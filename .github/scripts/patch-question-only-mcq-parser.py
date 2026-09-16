from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Word tables may expose a question number / option letter in one cell and its text
# in the next cell. The core parser expects `1. question` and `A. option` lines.
# Normalize both inline choices and split table cells before parsing.
pattern = r'const normalizeLines = \(text: string\) => .*?;'
replacement = r'''const normalizeLines = (text: string) => {
  const raw = text
    .replace(/\r/g, "")
    .replace(/\t+/g, "\n")
    .replace(/\u00a0/g, " ")
    .replace(/\s+([A-D])[.)]\s+(?=\S)/g, "\n$1. ")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const lines: string[] = [];
  for (let i = 0; i < raw.length; i++) {
    const line = raw[i];
    if (/^\d+[.)]?$/.test(line) && i + 1 < raw.length) {
      lines.push(line.replace(/[.)]$/, "") + ". " + raw[++i]);
      continue;
    }
    if (/^[A-D][.)]?$/.test(line) && i + 1 < raw.length) {
      lines.push(line.charAt(0).toUpperCase() + ". " + raw[++i]);
      continue;
    }
    lines.push(line);
  }
  return lines;
};'''

s2, n = re.subn(pattern, lambda _m: replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Question-only MCQ parser anchor not found; refusing silent patch')

# Question-only quizzes should not manufacture a reading passage from headings.
needle = "const passage=passageLines.join('\\n\\n');"
if needle in s2:
    s2 = s2.replace(needle, "const passage = qs.length && passageLines.some(line => /reading|passage|text/i.test(line)) ? passageLines.join('\\n\\n') : '';", 1)

p.write_text(s2, encoding='utf-8')
print('question-only MCQ Word-table parser applied: split number/letter cells normalized')
