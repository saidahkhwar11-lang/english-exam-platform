from pathlib import Path
import re
p=Path('app/page.tsx')
s=p.read_text(encoding='utf-8')
# Do not silently claim success if the active compiled source still exposes
# teacher email input on the locked student's screen.
unlock_inputs=re.findall(r'<label[^>]*>\s*<span>\s*(?:Teacher\s+)?Email\s*</span>\s*<input[^>]*value=\{approvalEmail\}[^>]*>\s*</label>',s,flags=re.I)
for field in unlock_inputs:
    s=s.replace(field,'')
# Ensure teacher identity is resolved from the active class session, not
# supplied by the student. Old sessions lacking teacherEmail must be reset.
if 'teacherEmail: email.trim().toLowerCase(), examContent' not in s:
    raise RuntimeError('Cannot guarantee teacher identity is read from the active session.')
if 'await verifyTeacherCredentials(joinedSession.teacherEmail, unlockPassword);' not in s:
    raise RuntimeError('Password-only verification call missing.')
if 'className="student-submit-success"' not in s or 'if (access === "student" && submitted)' not in s:
    raise RuntimeError('Student submission privacy screen missing.')
if re.search(r'<input[^>]*value=\{approvalEmail\}',s):
    raise RuntimeError('Teacher email field still visible; refusing deployment.')
p.write_text(s,encoding='utf-8')
print('Privacy and password-only unlock source safeguards verified.')
