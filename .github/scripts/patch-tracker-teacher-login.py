from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()
start = s.index('  const loadTeacherWorkspace = async (idToken: string, teacherEmail: string) => {')
end = s.index('\n\n  useEffect(() => {\n    const restore = async () => {', start)
new = r'''  const runTrackerQuery = async (idToken: string, structuredQuery: Record<string, unknown>) => {
    const response = await fetch("https://firestore.googleapis.com/v1/projects/assessment-follow-up/databases/(default)/documents:runQuery", {
      method: "POST",
      headers: { Authorization: `Bearer ${idToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({ structuredQuery }),
    });
    if (!response.ok) throw new Error("Tracker access failed. Please use the same email and password you use in the Assessment Tracker.");
    const rows = await response.json() as Array<{ document?: { name: string; fields?: Record<string, { stringValue?: string; integerValue?: string }> } }>;
    return rows.flatMap((row) => row.document ? [row.document] : []);
  };

  const loadTeacherWorkspace = async (idToken: string, teacherEmail: string) => {
    const normalizedEmail = teacherEmail.trim().toLowerCase();

    // IMPORTANT: mirror the Assessment Tracker's ownership query exactly.
    // Do not list every class and filter in the browser: Firestore rules correctly
    // reject that for ordinary teachers. Query only the signed-in teacher's classes.
    const classDocs = await runTrackerQuery(idToken, {
      from: [{ collectionId: "classes" }],
      where: { fieldFilter: { field: { fieldPath: "teacherEmail" }, op: "EQUAL", value: { stringValue: normalizedEmail } } },
    });

    const ownClasses = classDocs.map((doc) => ({
      id: doc.name.split("/").pop() || "",
      gradeLevel: doc.fields?.gradeLevel?.stringValue || `Grade ${doc.fields?.grade?.integerValue || ""}`,
      section: doc.fields?.section?.stringValue || "",
    }));

    const classIds = ownClasses.map((item) => item.id).filter(Boolean);
    const studentGroups = await Promise.all(classIds.map((classId) => runTrackerQuery(idToken, {
      from: [{ collectionId: "students" }],
      where: { fieldFilter: { field: { fieldPath: "classId" }, op: "EQUAL", value: { stringValue: classId } } },
    })));
    const assessmentGroups = await Promise.all(classIds.map((classId) => runTrackerQuery(idToken, {
      from: [{ collectionId: "assessments" }],
      where: { fieldFilter: { field: { fieldPath: "classId" }, op: "EQUAL", value: { stringValue: classId } } },
    })));

    const ownStudents = studentGroups.flat().map((doc) => ({
      id: doc.name.split("/").pop() || "",
      classId: doc.fields?.classId?.stringValue || "",
      studentId: doc.fields?.studentId?.stringValue || "",
      name: doc.fields?.name?.stringValue || "",
    }));
    const ownAssessments = assessmentGroups.flat().map((doc) => ({
      id: doc.name.split("/").pop() || "",
      classId: doc.fields?.classId?.stringValue || "",
      title: doc.fields?.title?.stringValue || "",
      type: doc.fields?.type?.stringValue || "",
      max: Number(doc.fields?.max?.integerValue || 20),
    })).filter((item) => item.type !== "Diagnostic");

    setTeacherClasses(ownClasses); setTeacherStudents(ownStudents); setTeacherAssessments(ownAssessments);
    if (ownClasses[0]?.gradeLevel) setSelectedGrade(ownClasses[0].gradeLevel);
    setSelectedAssessmentId((old) => old || ownAssessments[0]?.id || "");
    setEmail(normalizedEmail); setUnlockEmail(normalizedEmail); setApprovalEmail(normalizedEmail);
    await loadSavedExamLibrary(normalizedEmail);
    setAccess("teacher"); setActiveTab("teacher");
  };'''
s = s[:start] + new + s[end:]
p.write_text(s)
print('Assessment Tracker teacher login/data query aligned without writing tracker data')
