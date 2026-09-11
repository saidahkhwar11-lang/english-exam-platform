from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()
old = "pdfjs.getDocument({data:new Uint8Array(await file.arrayBuffer()),disableWorker:true}).promise"
new = "pdfjs.getDocument({data:new Uint8Array(await file.arrayBuffer())}).promise"
if old not in s:
    raise SystemExit('pdfjs getDocument anchor not found')
s = s.replace(old, new, 1)
p.write_text(s)
print('pdfjs TypeScript compatibility fix applied')
