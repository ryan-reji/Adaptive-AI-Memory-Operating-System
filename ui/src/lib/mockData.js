// Mock data shaped to match the API contract you should confirm with Member 4.
// Field names here are a reasonable starting guess — once the contract call happens,
// only this file (and api.js's response mapping) should need to change.

export const mockMemories = [
  {
    id: "m1",
    text: "Discussed the SMOTE + StackingClassifier approach for the PIU severity prediction paper with Amaan and Ayesha.",
    source: "vscode",
    sourceLabel: "VS Code — piu_pipeline.py",
    project: "PIU Research Paper",
    timestamp: "2026-08-19T14:22:00Z",
    importance: 0.91,
    status: "kept",
  },
  {
    id: "m2",
    text: "Read through the CNS lecture deck on the CIA triad and attack lifecycle stages.",
    source: "pdf",
    sourceLabel: "PDF — CNS_Lecture_Wk6.pdf",
    project: "CNS Coursework",
    timestamp: "2026-08-18T09:05:00Z",
    importance: 0.42,
    status: "summarized",
  },
  {
    id: "m3",
    text: "Compared Supersonic Broadband vs Specific Net Pvt Ltd speed test results for gaming latency.",
    source: "browser",
    sourceLabel: "Browser — speedtest.net",
    project: "Personal",
    timestamp: "2026-08-14T20:11:00Z",
    importance: 0.18,
    status: "archived",
  },
  {
    id: "m4",
    text: "Fixed the Razorpay paise/rupee double-multiplication bug in the billing controller.",
    source: "vscode",
    sourceLabel: "VS Code — billingController.js",
    project: "HMS Mini Project",
    timestamp: "2026-05-02T11:40:00Z",
    importance: 0.76,
    status: "kept",
  },
  {
    id: "m5",
    text: "Drafted the Two Truths & A Lie Bible trivia set, volume 2, checking each false statement for subtlety.",
    source: "files",
    sourceLabel: "Word — TwoTruths_Vol2.docx",
    project: "Bible Trivia",
    timestamp: "2026-06-10T16:00:00Z",
    importance: 0.33,
    status: "summarized",
  },
];

export const mockTimeline = [
  { date: "2026-08-19", projects: ["PIU Research Paper"], count: 6 },
  { date: "2026-08-18", projects: ["CNS Coursework"], count: 3 },
  { date: "2026-08-14", projects: ["Personal"], count: 2 },
  { date: "2026-05-02", projects: ["HMS Mini Project"], count: 9 },
  { date: "2026-06-10", projects: ["Bible Trivia"], count: 4 },
];

export const mockProjects = [
  { id: "p1", name: "PIU Research Paper", memoryCount: 34, lastActive: "2026-08-19" },
  { id: "p2", name: "CNS Coursework", memoryCount: 21, lastActive: "2026-08-18" },
  { id: "p3", name: "HMS Mini Project", memoryCount: 58, lastActive: "2026-05-02" },
  { id: "p4", name: "Bible Trivia", memoryCount: 12, lastActive: "2026-06-10" },
];

export const mockSettings = {
  captureEnabled: true,
  sources: {
    browser: true,
    files: true,
    vscode: true,
    email: false,
  },
  forgettingPolicy: "balanced", // "aggressive" | "balanced" | "retain-all"
  sensitiveDataFilter: true,
};

export function mockForget(id) {
  const idx = mockMemories.findIndex((m) => m.id === id);
  if (idx !== -1) mockMemories.splice(idx, 1);
  return { id, deleted: true };
}

export function mockSearch(query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return mockMemories
    .filter(
      (m) =>
        m.text.toLowerCase().includes(q) ||
        m.project.toLowerCase().includes(q) ||
        m.sourceLabel.toLowerCase().includes(q)
    )
    .sort((a, b) => b.importance - a.importance);
}
