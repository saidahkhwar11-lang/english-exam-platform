from pathlib import Path

p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")

# Anti-cheating unlock: teacher enters password only.
# Reuse the teacher email already authenticated in the platform/session.
old='''await verifyTeacherCredentials(approvalEmail, approvalPassword);'''
new='''await verifyTeacherCredentials(teacherEmail || approvalEmail, approvalPassword);'''
if old not in s:
    raise SystemExit("teacher credential verification anchor missing")
s=s.replace(old,new)

# Hide/remove the email field anywhere in the approval modal while preserving password verification.
patterns=[
    '''<label className="field"><span>Teacher email</span><input type="email" value={approvalEmail} onChange={(e)=>setApprovalEmail(e.target.value)} /></label>''',
    '''<label className="field"><span>Email</span><input type="email" value={approvalEmail} onChange={(e)=>setApprovalEmail(e.target.value)} /></label>''',
]
for old_field in patterns:
    s=s.replace(old_field,'')

# If a specific unlock/approval email input remains, hide it at render time.
s=s.replace('''<input type="email" value={approvalEmail} onChange={(e)=>setApprovalEmail(e.target.value)} />''','''<input type="hidden" value={teacherEmail || approvalEmail} readOnly />''')

p.write_text(s,encoding="utf-8")
print("Anti-cheating teacher approval now asks for password only")
