from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text()

# Hide/remove the Student test navigation button from the authenticated teacher workspace.
# Keep the actual student access/test flow intact; only remove the teacher-side navigation button.
pattern = re.compile(r'<button[^>]*onClick=\{\(\)=>setActiveTab\("student"\)\}[^>]*>.*?Student test</button>', re.S)
updated, count = pattern.subn('', s, count=1)
if count == 0:
    # Support spacing/formatting variants produced by the finalizer.
    pattern2 = re.compile(r'<button[^>]*setActiveTab\("student"\)[^>]*>.*?Student\s*test.*?</button>', re.S)
    updated, count = pattern2.subn('', s, count=1)
if count == 0:
    raise SystemExit('Student test navigation button not found')

p.write_text(updated)
print('student-test navigation removed from authenticated teacher workspace')
