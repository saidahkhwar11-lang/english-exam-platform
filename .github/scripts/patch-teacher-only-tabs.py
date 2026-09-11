from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()
old = '''<nav className="tabs"><button onClick={()=>setActiveTab("teacher")} className={activeTab==="teacher"?"active":""}><FileText size={18}/>Teacher workspace</button><button onClick={()=>setActiveTab("student")} className={activeTab==="student"?"active":""}><GraduationCap size={18}/>Student test</button></nav>'''
new = '''<nav className="tabs"><button onClick={()=>setActiveTab("teacher")} className={activeTab==="teacher"?"active":""}><FileText size={18}/>Teacher workspace</button>{access !== "teacher" && <button onClick={()=>setActiveTab("student")} className={activeTab==="student"?"active":""}><GraduationCap size={18}/>Student test</button>}</nav>'''
if old not in s:
    raise SystemExit('teacher/student tabs anchor not found')
s = s.replace(old, new, 1)
p.write_text(s)
print('student-test tab hidden inside authenticated teacher workspace')
