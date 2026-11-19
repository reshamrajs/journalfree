// JournalFree front end. No framework, no build step: edit and refresh.
// Change REPO after you push to GitHub so the "suggest" links work.
const REPO = "https://github.com/reshamrajs/journalfree";
const MAX_COMPARE = 3;
const SPEED_RANK = { Fast: 0, Moderate: 1, Slow: 2 };

const $ = (sel) => document.querySelector(sel);
const state = { journals: [], subjects: new Set(), compare: new Set() };

const els = {
  q: $("#q"), publisher: $("#publisher"), quartile: $("#quartile"), speed: $("#speed"),
  sort: $("#sort"), verified: $("#verified"), subjects: $("#subjects"),
  list: $("#list"), count: $("#count"), compare: $("#compare"),
  compareTable: $("#compare-table"), tpl: $("#card-tpl"),
};

async function init() {
  $("#suggest").href = `${REPO}/issues/new?template=journal-correction.yml`;
  $("#source").href = REPO;
  try {
    const res = await fetch("journals.json");
    if (!res.ok) throw new Error(res.status);
    state.journals = await res.json();
  } catch (err) {
    els.count.textContent = "Could not load journals.json. Run: python scripts/build_data.py";
    return;
  }
  buildFilters();
  readUrl();
  for (const el of [els.q, els.publisher, els.quartile, els.speed, els.sort, els.verified]) {
    el.addEventListener("input", render);
  }
  $("#clear-compare").addEventListener("click", () => { state.compare.clear(); render(); });
  render();
}

function buildFilters() {
  const publishers = [...new Set(state.journals.map((j) => j.publisher))].sort();
  for (const p of publishers) els.publisher.add(new Option(p, p));

  const subjects = [...new Set(state.journals.flatMap((j) => j.subjects))].sort();
  for (const s of subjects) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = s;
    b.setAttribute("aria-pressed", "false");
    b.addEventListener("click", () => {
      state.subjects.has(s) ? state.subjects.delete(s) : state.subjects.add(s);
      render();
    });
    els.subjects.append(b);
  }
}

// Filters live in the URL so a filtered view can be shared as a link.
function readUrl() {
  const p = new URLSearchParams(location.search);
  els.q.value = p.get("q") ?? "";
  els.publisher.value = p.get("publisher") ?? "";
  els.quartile.value = p.get("quartile") ?? "";
  els.speed.value = p.get("speed") ?? "";
  els.sort.value = p.get("sort") ?? "if";
  els.verified.checked = p.get("verified") === "1";
  for (const s of (p.get("subject") ?? "").split(",").filter(Boolean)) state.subjects.add(s);
}

function writeUrl() {
  const p = new URLSearchParams();
  if (els.q.value) p.set("q", els.q.value);
  if (els.publisher.value) p.set("publisher", els.publisher.value);
  if (els.quartile.value) p.set("quartile", els.quartile.value);
  if (els.speed.value) p.set("speed", els.speed.value);
  if (els.sort.value !== "if") p.set("sort", els.sort.value);
  if (els.verified.checked) p.set("verified", "1");
  if (state.subjects.size) p.set("subject", [...state.subjects].join(","));
  const qs = p.toString();
  history.replaceState(null, "", qs ? `?${qs}` : location.pathname);
}

export function filterJournals(journals, f) {
  const q = f.q.trim().toLowerCase();
  return journals.filter((j) =>
    (!q || [j.journal, j.publisher, j.notes, ...j.subjects].join(" ").toLowerCase().includes(q)) &&
    (!f.publisher || j.publisher === f.publisher) &&
    (!f.quartile || j.quartile === f.quartile) &&
    (!f.speed || j.speed === f.speed) &&
    (!f.verified || j.ifVerified) &&
    (f.subjects.size === 0 || j.subjects.some((s) => f.subjects.has(s))));
}

export function sortJournals(journals, by) {
  const out = [...journals];
  if (by === "name") out.sort((a, b) => a.journal.localeCompare(b.journal));
  else if (by === "speed") out.sort((a, b) => (SPEED_RANK[a.speed] ?? 9) - (SPEED_RANK[b.speed] ?? 9) || (b.impactFactor ?? 0) - (a.impactFactor ?? 0));
  else out.sort((a, b) => (b.impactFactor ?? -1) - (a.impactFactor ?? -1));
  return out;
}

function render() {
  const f = {
    q: els.q.value, publisher: els.publisher.value, quartile: els.quartile.value,
    speed: els.speed.value, verified: els.verified.checked, subjects: state.subjects,
  };
  const shown = sortJournals(filterJournals(state.journals, f), els.sort.value);

  for (const chip of els.subjects.children) {
    chip.setAttribute("aria-pressed", String(state.subjects.has(chip.textContent)));
  }
  els.count.textContent = `${shown.length} of ${state.journals.length} journals`;
  els.list.replaceChildren(...shown.map(card));
  if (!shown.length) {
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = "No journals match these filters.";
    els.list.append(p);
  }
  renderCompare();
  writeUrl();
}

function card(j) {
  const node = els.tpl.content.firstElementChild.cloneNode(true);
  const a = node.querySelector(".title a");
  a.href = j.url;
  a.textContent = j.journal;
  const q = node.querySelector(".quartile");
  q.textContent = j.quartile;
  q.classList.toggle("q1", j.quartile === "Q1");
  node.querySelector(".publisher").textContent = `${j.publisher} · ${j.accessModel}`;

  const ifEl = node.querySelector(".if");
  ifEl.textContent = j.impactFactor ?? "-";
  if (!j.ifVerified && j.impactFactor != null) {
    const b = document.createElement("span");
    b.className = "badge warn";
    b.textContent = "unverified";
    b.title = "Estimate; confirm on the journal's page";
    ifEl.append(" ", b);
  }
  node.querySelector(".speed").textContent = j.speed ?? "-";
  node.querySelector(".indexing").textContent = j.indexing || "-";
  node.querySelector(".oa").textContent = j.greenOA ? `Green OA: ${j.greenOA}` : "";
  node.querySelector(".notes").textContent = j.notes;

  const tags = node.querySelector(".tags");
  for (const s of j.subjects) {
    const t = document.createElement("span");
    t.className = "tag";
    t.textContent = s;
    tags.append(t);
  }

  const box = node.querySelector(".cmp input");
  box.checked = state.compare.has(j.id);
  box.disabled = !box.checked && state.compare.size >= MAX_COMPARE;
  box.addEventListener("change", () => {
    box.checked ? state.compare.add(j.id) : state.compare.delete(j.id);
    render();
  });
  return node;
}

function renderCompare() {
  const picked = state.journals.filter((j) => state.compare.has(j.id));
  els.compare.hidden = picked.length < 2;
  if (picked.length < 2) return;
  const rows = [
    ["Journal", (j) => j.journal],
    ["Publisher", (j) => j.publisher],
    ["Quartile", (j) => j.quartile],
    ["Impact factor", (j) => `${j.impactFactor ?? "-"}${j.ifVerified ? "" : " (unverified)"}`],
    ["Speed", (j) => j.speed ?? "-"],
    ["Green OA", (j) => j.greenOA || "-"],
    ["Subjects", (j) => j.subjects.join(", ")],
  ];
  const table = els.compareTable;
  table.replaceChildren();
  for (const [label, get] of rows) {
    const tr = table.insertRow();
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = label;
    tr.append(th);
    for (const j of picked) tr.insertCell().textContent = get(j);
  }
}

if (typeof document !== "undefined" && document.querySelector("#list")) init();
