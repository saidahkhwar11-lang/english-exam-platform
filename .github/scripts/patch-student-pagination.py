from pathlib import Path
import re

path = Path('app/page.tsx')
text = path.read_text(encoding='utf-8')

old = '''      const studentsResponse = await fetch("https://firestore.googleapis.com/v1/projects/assessment-follow-up/databases/(default)/documents/students?pageSize=2000", { headers: { Authorization: `Bearer ${authResult.idToken}` } });
      const studentsResult = await studentsResponse.json() as { documents?: Array<{ name: string; fields?: Record<string, { stringValue?: string }> }> };
      const classIds = new Set(ownClasses.map((item) => item.id));
      const ownStudents = (studentsResult.documents || []).map((doc) => ({ id: doc.name.split("/").pop() || "", classId: doc.fields?.classId?.stringValue || "", studentId: doc.fields?.studentId?.stringValue || "", name: doc.fields?.name?.stringValue || "" })).filter((student) => classIds.has(student.classId));
'''

new = '''      const allStudentDocs: Array<{ name: string; fields?: Record<string, { stringValue?: string }> }> = [];
      let studentPageToken = "";
      do {
        const studentUrl = new URL("https://firestore.googleapis.com/v1/projects/assessment-follow-up/databases/(default)/documents/students");
        studentUrl.searchParams.set("pageSize", "500");
        if (studentPageToken) studentUrl.searchParams.set("pageToken", studentPageToken);
        const studentsResponse = await fetch(studentUrl.toString(), { headers: { Authorization: `Bearer ${authResult.idToken}` } });
        const studentsResult = await studentsResponse.json() as { documents?: Array<{ name: string; fields?: Record<string, { stringValue?: string }> }>; nextPageToken?: string };
        if (!studentsResponse.ok) throw new Error("Unable to load tracker students.");
        allStudentDocs.push(...(studentsResult.documents || []));
        studentPageToken = studentsResult.nextPageToken || "";
      } while (studentPageToken);
      const classIds = new Set(ownClasses.map((item) => item.id));
      const ownStudents = allStudentDocs.map((doc) => ({ id: doc.name.split("/").pop() || "", classId: doc.fields?.classId?.stringValue || "", studentId: doc.fields?.studentId?.stringValue || "", name: doc.fields?.name?.stringValue || "" })).filter((student) => classIds.has(student.classId));
'''

if old not in text:
    raise SystemExit('Expected student-loading block was not found; refusing to make an unsafe patch.')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Patched Firestore student pagination successfully.')
