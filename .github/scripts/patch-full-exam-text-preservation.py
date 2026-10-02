from pathlib import Path

p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")

# Preserve complete uploaded passage text and complete MCQ option wording.
# Never shorten content for display/import.
replacements=[
    (".slice(0, 4)", ""),
    (".slice(0,4)", ""),
]
# Do not globally remove slices; only strengthen extraction/normalization below.

# Word paragraph extraction is handled by patch-reading-paragraphs.py.
# Do not replace htmlExamText here; that helper must retain double newlines between Word paragraphs.

# Make passage detection accept numbered question-range headings and keep everything before the first real question.
oldq='''const questionIndex = lines.findIndex((line, index) => index > titleIndex && /^questions?$/i.test(line.trim()));'''
newq='''const questionIndex = lines.findIndex((line, index) => index > titleIndex && (/^questions?(?:\\s+\\d+\\s*[-–—]\\s*\\d+)?$/i.test(line.trim()) || /^\\d+[.)]\\s+\\S/.test(line.trim())));'''
if oldq in s:
    s=s.replace(oldq,newq,1)

# Ensure normalization trims indentation/tabs but never drops option words.
oldnorm='''.replace(/\\t+/g, "\\n")
    .replace(/\\u00a0/g, " ")'''
newnorm='''.replace(/\\t+/g, "\\n")
    .replace(/\\u00a0/g, " ")
    .replace(/[ \\f\\v]+/g, " ")'''
if oldnorm in s:
    s=s.replace(oldnorm,newnorm,1)

p.write_text(s,encoding="utf-8")
print("Full exam text preservation guard applied")
