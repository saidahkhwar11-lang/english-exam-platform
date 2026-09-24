"""Preserve uploaded reading passage paragraphs in the final built exam UI."""
from pathlib import Path

page = Path('app/page.tsx')
s = page.read_text()

helper = '''// Keep paragraph breaks from Word and text exams; old saved exams retain sourceText.
const readingSource = (rawText: string) => {
  const lines = rawText.replace(/\\r\\n?/g, "\\n").split("\\n");
  const header = lines.findIndex(line => /^reading\\s+(passage|text)$/i.test(line.trim()));
  if (header < 0) return { title: "", passage: "" };
  const titleIndex = lines.findIndex((line, index) => index > header && !!line.trim());
  if (titleIndex < 0) return { title: "", passage: "" };
  const questionIndex = lines.findIndex((line, index) => index > titleIndex && /^questions?$/i.test(line.trim()));
  const afterHeader = lines.slice(titleIndex + 1, questionIndex < 0 ? undefined : questionIndex).join("\\n");
  const firstQuestion = afterHeader.search(/^\\s*[0-9]{1,3}[.)]\\s+\\S/m);
  const passage = (firstQuestion < 0 ? afterHeader : afterHeader.slice(0, firstQuestion)).trim();
  return { title: lines[titleIndex].trim(), passage };
};
const passageParagraphs = (value: string) => value.replace(/\\r\\n?/g, "\\n")
  .split(/\\n\\s*\\n/).map(p => p.trim()).filter(Boolean);
const htmlExamText = (html: string) => {
  const parsed = new DOMParser().parseFromString(html, "text/html");
  return Array.from(parsed.body.querySelectorAll("p")).map((paragraph) => {
    const copy = paragraph.cloneNode(true) as HTMLElement;
    copy.querySelectorAll("br").forEach(br => br.replaceWith("\\n"));
    return (copy.textContent || "").trim();
  }).filter(Boolean).join("\\n\\n");
};
const extractPdfPageText = (items: Array<{str?: string; hasEOL?: boolean; transform?: number[]; height?: number}>) => {
  const lines: string[] = []; let current = ""; let previousY: number | undefined; let height = 12;
  const finish = () => { if (current.trim()) lines.push(current.trim()); current = ""; };
  for (const item of items) {
    const y = item.transform?.[5];
    if (y !== undefined && previousY !== undefined && Math.abs(y - previousY) > 2) {
      finish();
      if (previousY - y > Math.max(height, item.height || 12) * 1.55) lines.push("");
    }
    const word = item.str || "";
    if (word) current += (current && !/\\s$/.test(current) && !/^\\s/.test(word) ? " " : "") + word;
    if (item.hasEOL) finish();
    if (y !== undefined) previousY = y;
    if (item.height) height = item.height;
  }
  finish(); return lines.join("\\n");
};

'''
anchor = 'const passages: Record<Level, string> = {'
assert s.count(anchor) == 1, 'passage helper anchor missing or repeated'
s = s.replace(anchor, helper + anchor, 1)

old = '''    const hasRealPassage=preamble.some(line=>/reading\\s*(text|passage)|passage/i.test(line)) || preamble.join(' ').length>350;
    const passage=hasRealPassage?preamble.join('\\n\\n'):'';'''
new = '''    const originalReading = readingSource(rawText);
    const hasRealPassage=Boolean(originalReading.passage) || preamble.join(' ').length>350;
    const passage=originalReading.passage || (hasRealPassage ? preamble.join('\\n\\n') : '');'''
assert s.count(old) == 1, 'parser passage anchor missing or repeated'
s = s.replace(old, new, 1)

old_pdf = "pages.push(tc.items.map((x:any)=>x.str||'').join(' '));"
new_pdf = "pages.push(extractPdfPageText(tc.items as Array<{str?:string;hasEOL?:boolean;transform?:number[];height?:number}>));"
assert s.count(old_pdf) == 1, 'PDF extraction anchor missing or repeated'
s = s.replace(old_pdf, new_pdf, 1)

old_docx = "else if (ext==='docx') { const {default:mammoth}=await import('mammoth/mammoth.browser'); const result=await mammoth.extractRawText({arrayBuffer:await file.arrayBuffer()}); text=result.value; }"
new_docx = "else if (ext==='docx') { const {default:mammoth}=await import('mammoth/mammoth.browser'); const bytes=await file.arrayBuffer(); const [raw, formatted]=await Promise.all([mammoth.extractRawText({arrayBuffer:bytes}), mammoth.convertToHtml({arrayBuffer:bytes})]); text=raw.value; docxReading=readingSource(htmlExamText(formatted.value)); }"
assert s.count(old_docx) == 1, 'Word extraction anchor missing or repeated'
s = s.replace(old_docx, new_docx, 1)
old_process = "      const ext=file.name.split('.').pop()?.toLowerCase(); let text='';"
assert s.count(old_process) == 1, 'file processing anchor missing or repeated'
s = s.replace(old_process, old_process + " let docxReading={title:'',passage:''};", 1)
old_content = '      const content=parseTeacherTest(text,file.name); setExamContent(content);'
new_content = '''      const content=parseTeacherTest(text,file.name);
      if (docxReading.passage) {
        content.title=docxReading.title;
        content.passages={basic:docxReading.passage,standard:docxReading.passage,advanced:docxReading.passage};
      }
      setExamContent(content);'''
assert s.count(old_content) == 1, 'saved exam content anchor missing or repeated'
s = s.replace(old_content, new_content, 1)

old_reading = '  const hasReadingPassage = Boolean(examContent?.passages[level]?.trim());'
new_reading = '''  const sourceReading = examContent?.sourceText ? readingSource(examContent.sourceText) : {title:"",passage:""};
  const readingText = examContent?.passages[level] || sourceReading.passage || "";
  const readingTitle = examContent?.title || sourceReading.title || "Exam not loaded";
  const hasReadingPassage = Boolean(readingText.trim());'''
assert s.count(old_reading) == 1, 'reading visibility anchor missing or repeated'
s = s.replace(old_reading, new_reading, 1)

old_display = '<h2>{examContent?.title || "Exam not loaded"}</h2><p>{examContent?.passages[level] || ""}</p>'
new_display = '<h2>{readingTitle}</h2>{passageParagraphs(readingText).map((paragraph, index) => <p key={index}>{paragraph}</p>)}'
assert s.count(old_display) == 1, 'reading display anchor missing or repeated'
s = s.replace(old_display, new_display, 1)
page.write_text(s)

css = Path('app/globals.css')
css.write_text(css.read_text() + '\n.reading-scroll p{white-space:pre-wrap;margin:0 0 1.15em}.reading-scroll p:last-child{margin-bottom:0}\n')
print('Reading paragraphs preserved in uploaded and previously saved Word exams')
