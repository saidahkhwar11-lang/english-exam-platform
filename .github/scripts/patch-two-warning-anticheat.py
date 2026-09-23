from pathlib import Path

page = Path('app/page.tsx')
source = page.read_text(encoding='utf-8')
changes = {
    'if (next >= 1) { setLocked(true); setWarning(""); }': 'if (next >= 2) { setLocked(true); setWarning(""); }',
    'Violations: {violations}/1': 'Violations: {violations}/2',
    'The test locks immediately after a violation and requires teacher approval to continue.': 'This is your first warning. The test locks on the second violation and requires teacher approval to continue.',
}
for old, new in changes.items():
    if old not in source:
        raise SystemExit('Anti-cheating rule changed; refusing silent patch')
    source = source.replace(old, new, 1)
page.write_text(source, encoding='utf-8')
print('Two-warning anti-cheating rule restored; tracker result handling unchanged')
