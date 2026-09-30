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

# Word paragraphs + tables: preserve all text nodes in document order rather than p-only.
old='''const htmlExamText = (html: string) => {
  const parsed = new DOMParser().parseFromString(html, "text/html");
  return Array.from(parsed.body.querySelectorAll("p")).map((paragraph) => {
    const copy = paragraph.cloneNode(true) as HTMLElement;
    copy.querySelectorAll("br").forEach(br => br.replaceWith("\\n"));
    return (copy.textContent || "").trim();
  }).filter(Boolean).join("\\n\\n");
};'''
new='''const htmlExamText = (html: string) => {
  const parsed = new DOMParser().parseFromString(html, "text/html");
  const blocks = Array.from(parsed.body.querySelectorAll("p, li, td, th"));
  return blocks.map((block) => {
    const copy = block.cloneNode(true) as HTMLElement;
    copy.querySelectorAll("br").forEach(br => br.replaceWith("\\n"));
    return (copy.textContent || "").replace(/\\u00a0/g, " ").trim();
  }).filter(Boolean).join("\\n");
};'''
if old in s:
    s=s.replace(old,new,1)

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
