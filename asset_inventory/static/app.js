"use strict";

// Severity band of a CVSS v3 score
function severity(cvss) {
  if (cvss === 0) return "none";
  if (cvss < 4) return "low";
  if (cvss < 7) return "medium";
  if (cvss < 9) return "high";
  return "critical";
}

// Add one table row. textContent shows the data as plain text, never as HTML (prevents XSS).
function addRow(tbody, values) {
  const row = tbody.insertRow();
  for (const value of values) {
    row.insertCell().textContent = value;
  }
  return row;
}

// Row shown when a table has no data
function addEmptyRow(tbody, columns, text) {
  const cell = tbody.insertRow().insertCell();
  cell.colSpan = columns;
  cell.className = "empty";
  cell.textContent = text;
}

// Show or hide a message paragraph
function showMessage(id, text) {
  const element = document.getElementById(id);
  element.textContent = text;
  element.hidden = !text;
}

// GET a path of the API and return the JSON. Errors use the Problem Details "detail" field.
async function getJson(path) {
  let response;
  try {
    response = await fetch(path, { headers: { Accept: "application/json" } });
  } catch (error) {
    throw new Error("The API did not answer. Check that the api container is running.");
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(body && body.detail ? body.detail : "The API answered " + response.status + ".");
  }
  return body;
}

async function loadEquipments() {
  const equipments = await getJson("/v1/equipments");
  const tbody = document.getElementById("equipments");
  tbody.replaceChildren();
  for (const e of equipments) {
    addRow(tbody, [e.id, e.name, e.type, e.location, e.vulnerability_ids.join(", ")]);
  }
  if (equipments.length === 0) addEmptyRow(tbody, 5, "No equipments registered.");
  document.getElementById("stat-equipments").textContent = equipments.length;
}

async function loadVulnerabilities() {
  const vulnerabilities = await getJson("/v1/vulnerabilities");
  const tbody = document.getElementById("vulnerabilities");
  tbody.replaceChildren();
  for (const v of vulnerabilities) {
    const row = addRow(tbody, [v.id, v.description, v.category, v.cvss.toFixed(1), v.status]);
    row.cells[3].className = "num sev sev-" + severity(v.cvss);
    row.cells[3].title = severity(v.cvss);
  }
  if (vulnerabilities.length === 0) addEmptyRow(tbody, 5, "No vulnerabilities registered.");
  const active = vulnerabilities.filter(v => v.status === "OPEN" || v.status === "IN_PROGRESS");
  document.getElementById("stat-active").textContent = active.length;
}

async function loadRisk() {
  const tbody = document.getElementById("risk");
  tbody.replaceChildren();
  let rows;
  try {
    rows = await getJson("/v1/risk");
  } catch (error) {
    // 422 (no equipments, ill-conditioned system) is shown in this card only
    showMessage("risk-message", error.message);
    document.getElementById("stat-risk").textContent = "–";
    return;
  }
  showMessage("risk-message", "");
  const highest = rows.length ? rows[0].effective_risk : 0;
  for (const r of rows) {
    const row = addRow(tbody, [r.id, r.name, r.own_risk.toFixed(2), r.effective_risk.toFixed(2), ""]);
    row.cells[2].className = "num";
    row.cells[3].className = "num";
    const bar = document.createElement("div");
    bar.className = "bar";
    bar.style.width = (highest > 0 ? (r.effective_risk / highest) * 100 : 0) + "%";
    row.cells[4].append(bar);
  }
  document.getElementById("stat-risk").textContent = highest.toFixed(2);
}

async function loadAll() {
  showMessage("api-error", "");
  const results = await Promise.allSettled([loadEquipments(), loadVulnerabilities(), loadRisk()]);
  const failed = results.find(result => result.status === "rejected");
  if (failed) showMessage("api-error", failed.reason.message);
  document.getElementById("updated").textContent = "Updated at " + new Date().toLocaleTimeString();
}

document.getElementById("refresh").addEventListener("click", loadAll);
loadAll();
