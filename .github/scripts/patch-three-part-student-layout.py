from pathlib import Path
p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")
anchor='  const hasReadingPassage = Boolean(examContent?.passages[level]?.trim());'
if s.count(anchor)!=1: raise RuntimeError("Reading passage visibility anchor changed")
s=s.replace(anchor,anchor+'\n  const showSectionReading = hasReadingPassage && (!examContent?.wordBank || current[safeCurrentQuestion]?.skill === "Reading Comprehension");',1)
# Change only the student exam layout expressions, leaving existing reading-only exams alone.
s=s.replace('student-exam-grid ${hasReadingPassage ?','student-exam-grid ${showSectionReading ?',1)
s=s.replace('{hasReadingPassage && <section className="reading-panel">','{showSectionReading && <section className="reading-panel">',1)
s=s.replace('(!hasReadingPassage || !textMaximized)','(!showSectionReading || !textMaximized)')
old='<input className={`short-answer-input ${submitted ? (answerFeedback[String(q.id)] ? "correct" : "wrong") : ""}`} type="text" value={typeof selected === "string" ? selected : ""} disabled={submitted} autoComplete="off" spellCheck={false} onChange={(e) => setAnswers((old)=>({...old,[q.id]:e.target.value}))} placeholder={q.skill === "Vocabulary" ? "Choose a word from the box" : "Type your answer exactly"} />'
if old not in s:
    # Fail rather than silently publishing an unchanged input.
    raise RuntimeError("Student short-answer input anchor changed; dropdown not installed")
new='''{q.skill === "Vocabulary" && examContent?.wordBank?.length
  ? <select className="short-answer-input" value={typeof selected === "string" ? selected : ""} disabled={submitted} onChange={(e) => setAnswers(old => ({...old,[q.id]:e.target.value}))} aria-label="Choose the correct word from the word box">
      <option value="">Choose a word from the box</option>
      {examContent.wordBank.map((word) => <option key={word} value={word}>{word}</option>)}
    </select>
  : '''+old+'''}'''
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("Reading passage restricted to Reading section; vocabulary uses word-bank dropdown")
