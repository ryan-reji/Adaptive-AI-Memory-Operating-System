// Turns raw /memories/ records (activity evidence shape) into
// display-friendly fields for MemoryCard, Dashboard, and Timeline.
//
// The backend strips sensitive fields (content, path, source_path,
// old_path, raw, any *_path field) — so this only ever reads fields
// confirmed present in the real API: browser {browser, title, sessions},
// vscode {editor, project, file, sessions}, file {file_name, file_type}.

const SOURCE_LABELS = {
  browser: "Browser",
  vscode: "VS Code",
  file: "File",
};

export function toDisplayMemory(record) {
  const { source_type, details = {}, timestamp, ai_processed, status } = record;

  let text = "";
  let project = "General";
  let sourceLabel = SOURCE_LABELS[source_type] || source_type;

  if (source_type === "browser") {
    text = details.title || "Browsing activity";
    sourceLabel = details.browser || "Browser";
  } else if (source_type === "vscode") {
    text = details.file ? `Worked on ${details.file}` : "VS Code activity";
    project = details.project || "General";
    sourceLabel = "VS Code";
  } else if (source_type === "file") {
    text = details.file_name ? `File activity: ${details.file_name}` : "File activity";
  } else {
    text = "Activity captured";
  }

  return {
    id: record.id,
    text,
    source: source_type,
    sourceLabel,
    project,
    timestamp,
    processed: !!ai_processed,
    status: status || "active",
  };
}

export function groupByDate(records) {
  const byDate = {};
  for (const r of records) {
    const date = r.timestamp.slice(0, 10);
    if (!byDate[date]) byDate[date] = { date, count: 0, projects: new Set() };
    byDate[date].count += 1;
    const d = toDisplayMemory(r);
    byDate[date].projects.add(d.project);
  }
  return Object.values(byDate)
    .map((e) => ({ ...e, projects: [...e.projects] }))
    .sort((a, b) => b.date.localeCompare(a.date));
}

export function groupByProject(records) {
  const byProject = {};
  for (const r of records) {
    const d = toDisplayMemory(r);
    if (!byProject[d.project]) {
      byProject[d.project] = { id: d.project, name: d.project, memoryCount: 0, lastActive: d.timestamp };
    }
    byProject[d.project].memoryCount += 1;
    if (d.timestamp > byProject[d.project].lastActive) {
      byProject[d.project].lastActive = d.timestamp;
    }
  }
  return Object.values(byProject).sort((a, b) => b.lastActive.localeCompare(a.lastActive));
}