"""Add multi-text reading exams: Text 1 questions, Text 2 questions, Text 3 questions, etc."""
from pathlib import Path

p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")

helper=r'''
type MultiReadingSection = { id:number; title:string; passage:string; questionCount:number };

const multiReadingSource = (rawText:string): MultiReadingSection[] => {
  const normalized=(rawText||"").replace(/\r\n?/g,"\n");
  const lines=normalized.split("\n");
  const starts:number[]=[];
  lines.forEach((line,index)=>{
    const v=line.trim();
    if (/^(?:reading\s+)?(?:text|passage)\s*\d+\b/i.test(v)) starts.push(index);
  });
  if (starts.length < 2) return [];
  return starts.map((start,sectionIndex)=>{
    const end=starts[sectionIndex+1] ?? lines.length;
    const block=lines.slice(start,end);
    const heading=block[0].trim();
    const number=Number(heading.match(/(\d+)/)?.[1] || sectionIndex+1);
    const firstQuestion=block.findIndex((line,index)=>index>0 && /^\s*\d{1,3}[.)]\s+\S/.test(line));
    const questionLines=block.filter(line=>/^\s*\d{1,3}[.)]\s+\S/.test(line));
    let passageLines=block.slice(1,firstQuestion<0?block.length:firstQuestion);
    passageLines=passageLines.filter(line=>!/^questions?\s*:?$/i.test(line.trim()));
    const titleLine=passageLines.findIndex(line=>Boolean(line.trim()));
    let title="Text "+number;
    if(titleLine>=0 && passageLines[titleLine].trim().length<100){
      title=passageLines[titleLine].trim();
      passageLines=passageLines.slice(titleLine+1);
    }
    return {id:number,title,passage:passageLines.join("\n").trim(),questionCount:questionLines.length};
  }).filter(section=>section.passage && section.questionCount>0);
};

const readingQuestionSections = (rawText:string, fallbackPassage:string, questionCount:number) => {
  const sections=multiReadingSource(rawText);
  if(sections.length<2) return [{id:1,title:"Reading Text",passage:fallbackPassage,start:0,end:questionCount}];
  let cursor=0;
  return sections.map((section,index)=>{
    const remaining=questionCount-cursor;
    const count=index===sections.length-1?remaining:Math.min(section.questionCount,remaining);
    const item={...section,start:cursor,end:cursor+count};
    cursor+=count;
    return item;
  }).filter(section=>section.end>section.start);
};
'''
anchor='const passages: Record<Level, string> = {'
if 'const multiReadingSource =' not in s:
    if anchor not in s: raise SystemExit("multi-text helper anchor missing")
    s=s.replace(anchor,helper+"\n"+anchor,1)

# Derive section boundaries from the uploaded source. One-text exams keep old behavior.
old='''  const sourceReading = examContent?.sourceText ? readingSource(examContent.sourceText) : {title:"",passage:""};
  const readingText = examContent?.passages[level] || sourceReading.passage || "";
  const readingTitle = examContent?.title || sourceReading.title || "Exam not loaded";
  const hasReadingPassage = Boolean(readingText.trim());'''
new='''  const sourceReading = examContent?.sourceText ? readingSource(examContent.sourceText) : {title:"",passage:""};
  const readingText = examContent?.passages[level] || sourceReading.passage || "";
  const readingTitle = examContent?.title || sourceReading.title || "Exam not loaded";
  const readingSections = readingQuestionSections(examContent?.sourceText || "", readingText, current.length);
  const hasMultipleReadingTexts = readingSections.length > 1;
  const hasReadingPassage = Boolean(readingText.trim()) || hasMultipleReadingTexts;\n  const activeReadingSection = hasMultipleReadingTexts ? (readingSections.find((section) => currentQuestion >= section.start && currentQuestion < section.end) || readingSections[0]) : null;\n  const visibleReadingTitle = activeReadingSection?.title || readingTitle;\n  const visibleReadingText = activeReadingSection?.passage || readingText;'''
if old in s:
    s=s.replace(old,new,1)
elif 'const readingSections = readingQuestionSections' not in s:
    raise SystemExit("reading state anchor missing")

# For multi-text exams, hide the old single-passage panel; each passage is inserted
# directly before its own question group below.
old_display='<h2>{readingTitle}</h2>{passageParagraphs(readingText).map((paragraph, index) => <p key={index}>{paragraph}</p>)}'
new_display='<h2>{visibleReadingTitle}</h2>{passageParagraphs(visibleReadingText).map((paragraph, index) => <p key={index}>{paragraph}</p>)}{hasMultipleReadingTexts && <p className="multi-reading-note">Text {activeReadingSection?.id || 1} of {readingSections.length} · Questions {(activeReadingSection?.start || 0) + 1}–{activeReadingSection?.end || current.length}</p>}'
if old_display in s:
    s=s.replace(old_display,new_display,1)

# Insert the correct text immediately before the first question belonging to it.
map_anchor='{current.map((q, index) => <article'
if map_anchor in s and 'readingSections.find((section) => section.start === index)' not in s:
    s=s.replace(map_anchor,'{current.map((q, index) => <>{readingSections.find((section) => section.start === index) && (() => { const section=readingSections.find((item) => item.start === index)!; return <div className="multi-reading-text"><div className="multi-reading-text-head"><strong>{section.title}</strong><span>Questions {section.start + 1}–{section.end}</span></div>{passageParagraphs(section.passage).map((paragraph, paragraphIndex) => <p key={paragraphIndex}>{paragraph}</p>)}</div>; })()}<article',1)
    close_anchor='</article>)}'
    if close_anchor not in s: raise SystemExit("question map closing anchor missing")
    s=s.replace(close_anchor,'</article></>)}',1)
elif 'readingSections.find((section) => section.start === index)' not in s:
    print("Question renderer has changed; continuing without altering the current renderer")


# Prevent a following Text/Passage section from becoming extra answer choices.
old_question_block='''      const q0=qStarts[qi]; const next=qi+1<qStarts.length?qStarts[qi+1].idx:body.length;
      const block=body.slice(q0.idx+1,next);'''
new_question_block='''      const q0=qStarts[qi]; const next=qi+1<qStarts.length?qStarts[qi+1].idx:body.length;
      const rawBlock=body.slice(q0.idx+1,next);
      const nextTextBoundary=rawBlock.findIndex((line)=>/^(?:reading\\s+)?(?:text|passage)\\s*\\d+\\b/i.test(line.trim()));
      const block=nextTextBoundary>=0?rawBlock.slice(0,nextTextBoundary):rawBlock;'''
if old_question_block in s:
    s=s.replace(old_question_block,new_question_block,1)


# The source parser can miss MCQ choices after a passage boundary. Reclassify any
# parsed question with A-D lines in its source block as MCQ.
mcq_guard='''      const choiceLines=block.filter((line)=>/^[A-H][.)]\\s+\\S/i.test(line.trim()));
      if(choiceLines.length>=2){
        const choices=choiceLines.map((line)=>line.trim().replace(/^[A-H][.)]\\s+/i,""));
        const letters=choiceLines.map((line)=>line.trim().match(/^([A-H])[.)]/i)?.[1]?.toUpperCase() || "");
        const answerLetter=(answerMap[q0.num]||"").toUpperCase();
        const answerIndex=Math.max(0,letters.indexOf(answerLetter));
        parsed.push({prompt:q0.prompt,type:"mcq",options:choices,answerIndex,marks:1});
        continue;
      }'''
if mcq_guard not in s:
    anchor='''      const block=nextTextBoundary>=0?rawBlock.slice(0,nextTextBoundary):rawBlock;'''
    if anchor in s:
        s=s.replace(anchor,anchor+"\n"+mcq_guard,1)

p.write_text(s,encoding="utf-8")

css=Path("app/globals.css")
style='''
.multi-reading-note{margin:0!important;color:#52677a;font-weight:600}.multi-reading-text{margin:0 0 1.25rem;border:1px solid #bae6fd;border-radius:16px;background:#f8fcff;padding:1.25rem 1.4rem}.multi-reading-text-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:.8rem;color:#0d2340}.multi-reading-text-head span{font-size:.78rem;font-weight:800;color:#0e7490;background:#cffafe;border-radius:999px;padding:.3rem .65rem}.multi-reading-text p{white-space:pre-wrap;margin:0 0 1em;line-height:2;color:#334155}.multi-reading-text p:last-child{margin-bottom:0}
'''
if '.multi-reading-text{' not in css.read_text(encoding="utf-8"):
    css.write_text(css.read_text(encoding="utf-8")+style,encoding="utf-8")
print("Multi-text reading support applied")
