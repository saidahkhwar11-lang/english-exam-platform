from pathlib import Path

page = Path("app/page.tsx")
source = page.read_text(encoding="utf-8")

# Make the existing automatic sharing behavior obvious to teachers.
old_label = '{personalCopyDraft ? "Save my copy" : editingPersonalExamId ? "Save changes to my library" : "Save Exam"}'
new_label = '{personalCopyDraft ? "Save my copy" : editingPersonalExamId ? "Save changes to my library" : "Save & share with grade"}'
if old_label not in source:
    raise SystemExit("Save button label anchor not found; refusing unsafe change")
source = source.replace(old_label, new_label, 1)

# Shared-library cards already represent exams available to the selected grade.
# Show an explicit status so creators do not look for a second Share button.
old_card = '<div><strong>{item.name}</strong><small>{item.assessmentType} · {item.timeAllowed} · {item.creatorEmail || "Teacher"}</small></div>'
new_card = '<div><strong>{item.name}</strong><small>{item.assessmentType} · {item.timeAllowed} · {item.creatorEmail || "Teacher"}</small><small className="mt-1 block font-semibold text-emerald-700">✓ Shared with {item.grade} library</small></div>'
if old_card not in source:
    raise SystemExit("Shared exam card anchor not found; refusing unsafe change")
source = source.replace(old_card, new_card, 1)

page.write_text(source, encoding="utf-8")
print("Shared grade status clarified on exam cards and save action")
