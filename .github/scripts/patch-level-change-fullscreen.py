from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

old = '''  const approveLevelChange = async () => {
    if (!levelApprovalTarget) return;
    setApprovalError("");
    try {
      await verifyTeacherCredentials(approvalEmail, approvalPassword);
      chooseLevel(levelApprovalTarget);
      setLevelApprovalTarget(null); setApprovalPassword(""); setApprovalError("");
    } catch (error) { setApprovalError(error instanceof Error ? error.message : "Unable to approve level change."); }
  };'''

new = '''  const approveLevelChange = async () => {
    if (!levelApprovalTarget) return;
    setApprovalError("");
    try {
      // Fullscreen must be restored from the teacher's Approve click itself.
      // Request it before the async credential check so browser user-activation is preserved.
      if (!document.fullscreenElement) await document.documentElement.requestFullscreen();
      await verifyTeacherCredentials(approvalEmail, approvalPassword);
      fullscreenStarted.current = true;
      chooseLevel(levelApprovalTarget);
      setLevelApprovalTarget(null); setApprovalPassword(""); setApprovalError("");
    } catch (error) {
      setApprovalError(
        error instanceof Error
          ? error.message
          : "Fullscreen and teacher approval are required to change level.",
      );
    }
  };'''

if old not in s:
    if new in s:
        print('level-change fullscreen patch already applied')
    else:
        raise SystemExit('Could not locate approveLevelChange block')
else:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding='utf-8')
    print('level-change fullscreen restoration applied')
