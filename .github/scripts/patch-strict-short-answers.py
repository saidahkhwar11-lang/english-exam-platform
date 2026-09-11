from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

repls = [
(
    'type Question = { id: number; skill: string; prompt: string; options: string[]; answer: number; marks: number; hint?: string };',
    'type Question = { id: number; skill: string; prompt: string; options: string[]; answer: number; marks: number; hint?: string; responseType?: "choice" | "short"; expectedText?: string };'
),
(
    '  const [answers, setAnswers] = useState<Record<number, number>>({});',
    '  const [answers, setAnswers] = useState<Record<number, number | string>>({});'
),
(
    '  const answered = Object.keys(answers).length;',
    '  const answered = current.filter((q) => { const value = answers[q.id]; return q.responseType === "short" ? typeof value === "string" && value.trim().length > 0 : value !== undefined; }).length;'
),
(
    '  const score = useMemo(() => current.reduce((sum, q) => sum + (answers[q.id] === q.answer ? q.marks : 0), 0), [answers, current]);',
    '  const score = useMemo(() => current.reduce((sum, q) => { const value = answers[q.id]; const correct = q.responseType === "short" ? (typeof value === "string" && value.trim() === (q.expectedText || "").trim()) : value === q.answer; return sum + (correct ? q.marks : 0); }, 0), [answers, current]);'
),
(
    "qs.push({id:idx+1,skill:'Vocabulary',prompt,options:[ans,'—'],answer:0,marks:1});",
    "qs.push({id:idx+1,skill:'Vocabulary',prompt,options:[],answer:0,marks:1,responseType:'short',expectedText:ans});"
),
]

for old, new in repls:
    if old not in s:
        raise SystemExit(f'missing expected strict-answer source: {old[:120]}')
    s = s.replace(old, new, 1)

old_ui = '<div className="single-answer-list">{q.options.map((option, optionIndex) => { const state=submitted ? optionIndex===q.answer?"correct":selected===optionIndex?"wrong":"" : selected===optionIndex?"selected":""; return <button key={option} disabled={submitted} onClick={() => setAnswers((old)=>({...old,[q.id]:optionIndex}))} className={`answer ${state}`}><span>{String.fromCharCode(65+optionIndex)}</span>{option}</button>; })}</div>'
new_ui = '<div className="single-answer-list">{q.responseType === "short" ? <div className="short-answer-wrap"><input className={`short-answer-input ${submitted ? (typeof selected === "string" && selected.trim() === (q.expectedText || "").trim() ? "correct" : "wrong") : ""}`} type="text" value={typeof selected === "string" ? selected : ""} disabled={submitted} autoComplete="off" spellCheck={false} onChange={(e) => setAnswers((old)=>({...old,[q.id]:e.target.value}))} placeholder="Type your answer exactly" />{submitted && <small className="short-answer-feedback">Correct answer: <b>{q.expectedText}</b></small>}</div> : q.options.map((option, optionIndex) => { const state=submitted ? optionIndex===q.answer?"correct":selected===optionIndex?"wrong":"" : selected===optionIndex?"selected":""; return <button key={option} disabled={submitted} onClick={() => setAnswers((old)=>({...old,[q.id]:optionIndex}))} className={`answer ${state}`}><span>{String.fromCharCode(65+optionIndex)}</span>{option}</button>; })}</div>'
if old_ui not in s:
    raise SystemExit('missing student answer UI source')
s = s.replace(old_ui, new_ui, 1)

p.write_text(s)

css = Path('app/globals.css')
c = css.read_text()
if '.short-answer-input' not in c:
    c += '''\n.short-answer-wrap{display:flex;flex-direction:column;gap:9px}.short-answer-input{width:100%;border:2px solid #cbd5e1;border-radius:14px;padding:14px 16px;font-size:1rem;background:#fff;color:#0f172a;outline:none;transition:.18s}.short-answer-input:focus{border-color:#0891b2;box-shadow:0 0 0 3px rgba(8,145,178,.12)}.short-answer-input.correct{border-color:#16a34a;background:#f0fdf4}.short-answer-input.wrong{border-color:#dc2626;background:#fef2f2}.short-answer-feedback{color:#475569}.short-answer-feedback b{color:#0f172a}\n'''
    css.write_text(c)

print('strict short-answer autocorrection applied: exact spelling required; outer spaces ignored')
