const state = {
  teams: [],
  players: [],
  matches: [],
};

/* ===== Club badge images ===== */

const BADGE_MAP = {
  "arsenal": "Arsenal",
  "aston villa": "Aston Villa",
  "bournemouth": "Bournemouth",
  "afc bournemouth": "Bournemouth",
  "brentford": "Brentford",
  "brighton": "Brighton",
  "brighton & hove albion": "Brighton",
  "brighton and hove albion": "Brighton",
  "burnley": "Burnley",
  "chelsea": "Chelsea",
  "crystal palace": "Crystal Palace",
  "everton": "Everton",
  "fulham": "Fulham",
  "leeds": "Leeds United",
  "leeds united": "Leeds United",
  "liverpool": "Liverpool",
  "manchester city": "Man City",
  "man city": "Man City",
  "manchester united": "Man United",
  "man united": "Man United",
  "man utd": "Man United",
  "newcastle": "Newcastle",
  "newcastle united": "Newcastle",
  "nottingham forest": "Nottingham Forest",
  "nott'm forest": "Nottingham Forest",
  "sunderland": "Sunderland",
  "tottenham": "Tottenham",
  "tottenham hotspur": "Tottenham",
  "spurs": "Tottenham",
  "west ham": "West Ham",
  "west ham united": "West Ham",
  "wolverhampton wanderers": "Wolves",
  "wolverhampton": "Wolves",
  "wolves": "Wolves",
};

function badgeURL(name) {
  const key = name.toLowerCase().trim();
  const file = BADGE_MAP[key];
  if (file) return `/static/badges/${encodeURIComponent(file)}.png`;
  for (const [k, v] of Object.entries(BADGE_MAP)) {
    if (key.includes(k) || k.includes(key)) return `/static/badges/${encodeURIComponent(v)}.png`;
  }
  return null;
}

function badgeHTML(name, small) {
  const url = badgeURL(name);
  const cls = small ? "club-badge club-badge-sm" : "club-badge";
  if (url) {
    return `<img class="${cls}" src="${url}" alt="" loading="lazy">`;
  }
  const initials = name.split(/\s+/).slice(0, 3).map((w) => w[0]).join("").toUpperCase();
  const hash = [...name].reduce((h, c) => c.charCodeAt(0) + ((h << 5) - h), 0);
  const colors = ["#c0392b","#2980b9","#27ae60","#8e44ad","#d35400","#16a085","#2c3e50","#e74c3c"];
  return `<span class="${cls}" style="background:${colors[Math.abs(hash) % colors.length]}">${initials}</span>`;
}

/* ===== Rank helpers ===== */

function rankIcon(rank) {
  if (rank === 1) return '<span class="rank-medal">&#129351;</span>';
  if (rank === 2) return '<span class="rank-medal">&#129352;</span>';
  if (rank === 3) return '<span class="rank-medal">&#129353;</span>';
  return `<span class="rank-medal" style="color:var(--ink-muted)">${rank}</span>`;
}

function posBadge(pos) {
  const cls = pos <= 3 ? `pos-badge pos-${pos}` : "pos-badge pos-other";
  return `<span class="${cls}">${pos}</span>`;
}

function gdClass(gd) {
  if (gd > 0) return "gd-pos";
  if (gd < 0) return "gd-neg";
  return "gd-zero";
}

/* ===== Core helpers ===== */

function getSeason() {
  return document.querySelector("#season-input").value.trim() || "2025/26";
}

function getApiKey() {
  return document.querySelector("#api-key").value.trim();
}

function setStatus(message, isError = false) {
  const el = document.querySelector("#global-status");
  el.textContent = message;
  el.style.color = isError ? "var(--danger)" : "";
}

function loadSavedSettings() {
  const apiKey = window.localStorage.getItem("fmi-api-key");
  const season = window.localStorage.getItem("fmi-season");
  if (apiKey) document.querySelector("#api-key").value = apiKey;
  if (season) document.querySelector("#season-input").value = season;
}

async function apiFetch(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  const apiKey = getApiKey();
  if (apiKey && ["POST", "PUT", "DELETE"].includes((options.method || "GET").toUpperCase())) {
    headers["X-API-Key"] = apiKey;
  }
  const response = await fetch(path, { ...options, headers });
  if (response.status === 204) return null;
  const data = await response.json();
  if (!response.ok) {
    const message = data?.detail?.error?.message || data?.detail?.[0]?.msg || "Request failed";
    throw new Error(message);
  }
  return data;
}

function optionMarkup(items, labelFn) {
  return items.map((item) => `<option value="${item.id}">${labelFn(item)}</option>`).join("");
}

function getTeamName(teamId) {
  const team = state.teams.find((row) => row.id === teamId);
  return team ? team.name : `Team ${teamId}`;
}

async function fetchCollection(path) {
  const limit = 100;
  let skip = 0;
  let items = [];
  while (true) {
    const page = await apiFetch(`${path}?skip=${skip}&limit=${limit}`);
    items = items.concat(page.items);
    if (items.length >= page.total || page.items.length === 0) return items;
    skip += limit;
  }
}

/* ===== Loading skeletons ===== */

function showLoading(target, rows = 3) {
  const skeletons = Array.from({ length: rows }, () =>
    '<div class="loading-skeleton" style="height:40px;margin-bottom:6px;border-radius:8px"></div>'
  ).join("");
  document.querySelector(target).innerHTML = skeletons;
}

/* ===== Render helpers ===== */

function renderTeamOptions() {
  const markup = optionMarkup(state.teams, (team) => `${team.name} (#${team.id})`);
  ["#player-team-id", "#match-home-team-id", "#match-away-team-id"].forEach((sel) => {
    document.querySelector(sel).innerHTML = markup || '<option value="">No teams available</option>';
  });
}

function renderMatchOptions() { return; }

function renderEmpty(target, message) {
  document.querySelector(target).innerHTML = `<div class="empty-state">${message}</div>`;
}

function renderTeams() {
  if (!state.teams.length) { renderEmpty("#teams-list", "No teams found."); return; }
  document.querySelector("#teams-list").innerHTML = `
    <div class="resource-items">
      ${state.teams.map((team) => `
        <div class="resource-row">
          ${badgeHTML(team.name)}
          <div class="resource-info">
            <div class="resource-name">${team.name}</div>
            <div class="resource-meta">
              <span>ID ${team.id}</span>
              <span>${team.league}</span>
              <span>${team.country}</span>
            </div>
          </div>
          <div class="resource-actions">
            <button class="btn btn-ghost btn-sm" type="button" data-action="edit-team" data-id="${team.id}">Edit</button>
            <button class="btn btn-danger-subtle btn-sm" type="button" data-action="delete-team" data-id="${team.id}">Delete</button>
          </div>
        </div>`).join("")}
    </div>`;
}

function renderPlayers() {
  if (!state.players.length) { renderEmpty("#players-list", "No players found."); return; }
  document.querySelector("#players-list").innerHTML = `
    <div class="toggle-list">
      ${state.teams.map((team) => {
        const tp = state.players.filter((p) => p.team_id === team.id);
        return `
          <details class="toggle-row">
            <summary class="toggle-summary">
              <span class="toggle-team-header">${badgeHTML(team.name, true)} <strong>${team.name}</strong></span>
              <span class="toggle-count">${tp.length} player${tp.length !== 1 ? "s" : ""}</span>
            </summary>
            <div class="toggle-content">
              ${tp.length ? tp.map((p) => `
                <div class="resource-row">
                  <div class="resource-info">
                    <div class="resource-name">${p.name}</div>
                    <div class="resource-meta">
                      <span>ID ${p.id}</span>
                      <span class="stat-pill-neutral">${p.position}</span>
                    </div>
                  </div>
                  <div class="resource-actions">
                    <button class="btn btn-ghost btn-sm" type="button" data-action="edit-player" data-id="${p.id}">Edit</button>
                    <button class="btn btn-danger-subtle btn-sm" type="button" data-action="delete-player" data-id="${p.id}">Delete</button>
                  </div>
                </div>`).join("") : '<div class="empty-state">No players for this team.</div>'}
            </div>
          </details>`;
      }).join("")}
    </div>`;
}

function renderMatches() {
  if (!state.matches.length) { renderEmpty("#matches-list", "No matches found."); return; }
  document.querySelector("#matches-list").innerHTML = `
    <div class="resource-items">
      ${state.matches.map((m) => {
        const home = getTeamName(m.home_team_id);
        const away = getTeamName(m.away_team_id);
        return `
          <div class="resource-row">
            <div class="match-date-label" style="min-width:130px">${m.match_date} &middot; ${m.season}</div>
            <div class="match-fixture" style="flex:1">
              <span class="match-team-home"><span>${home}</span> ${badgeHTML(home, true)}</span>
              <span class="match-score">${m.home_score} - ${m.away_score}</span>
              <span class="match-team-away">${badgeHTML(away, true)} <span>${away}</span></span>
            </div>
            <div class="resource-actions">
              <button class="btn btn-ghost btn-sm" type="button" data-action="edit-match" data-id="${m.id}">Edit</button>
              <button class="btn btn-danger-subtle btn-sm" type="button" data-action="delete-match" data-id="${m.id}">Delete</button>
            </div>
          </div>`;
      }).join("")}
    </div>`;
}

function renderMetricList(target, rows, formatter) {
  if (!rows.length) { renderEmpty(target, "No records returned for that season."); return; }
  document.querySelector(target).innerHTML = `<div class="metric-list">${rows.map(formatter).join("")}</div>`;
}

/* ===== Analytics ===== */

async function loadAnalytics() {
  showLoading("#league-table", 5);
  showLoading("#top-scorers");
  showLoading("#most-assists");
  showLoading("#player-impact");
  showLoading("#clutch-impact");

  const season = encodeURIComponent(getSeason());
  const [league, scorers, assists, impact, clutch] = await Promise.all([
    apiFetch(`/analytics/league-table?season=${season}`),
    apiFetch(`/analytics/top-scorers?season=${season}&limit=8`),
    apiFetch(`/analytics/most-assists?season=${season}&limit=8`),
    apiFetch(`/analytics/player-impact?season=${season}&limit=8`),
    apiFetch(`/analytics/clutch-impact?season=${season}&limit=8`),
  ]);

  /* League Table */
  if (!league.table.length) {
    renderEmpty("#league-table", "No league table rows for that season.");
  } else {
    document.querySelector("#league-table").innerHTML = `
      <table>
        <thead>
          <tr>
            <th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th>
          </tr>
        </thead>
        <tbody>
          ${league.table.map((r) => `
            <tr>
              <td>${posBadge(r.position)}</td>
              <td><span class="team-cell">${badgeHTML(r.team_name, true)} ${r.team_name}</span></td>
              <td>${r.played}</td>
              <td>${r.wins}</td>
              <td>${r.draws}</td>
              <td>${r.losses}</td>
              <td><span class="${gdClass(r.goal_difference)}">${r.goal_difference > 0 ? "+" : ""}${r.goal_difference}</span></td>
              <td><span class="pts-cell">${r.points}</span></td>
            </tr>`).join("")}
        </tbody>
      </table>`;
  }

  /* Top Scorers */
  renderMetricList("#top-scorers", scorers.top_scorers, (r) => `
    <div class="metric-row">
      ${rankIcon(r.rank)}
      ${badgeHTML(r.team_name, true)}
      <div class="metric-info">
        <div class="metric-name">${r.player_name}</div>
        <div class="metric-detail">${r.team_name}</div>
      </div>
      <span class="metric-value">${r.goals}</span>
    </div>`);

  /* Most Assists */
  renderMetricList("#most-assists", assists.most_assists, (r) => `
    <div class="metric-row">
      ${rankIcon(r.rank)}
      ${badgeHTML(r.team_name, true)}
      <div class="metric-info">
        <div class="metric-name">${r.player_name}</div>
        <div class="metric-detail">${r.team_name}</div>
      </div>
      <span class="metric-value">${r.assists}</span>
    </div>`);

  /* Player Impact */
  renderMetricList("#player-impact", impact.players, (r) => `
    <div class="metric-row">
      ${rankIcon(r.rank)}
      ${badgeHTML(r.team_name, true)}
      <div class="metric-info">
        <div class="metric-name">${r.player_name}</div>
        <div class="metric-detail">
          <span>${r.team_name}</span>
          <span class="stat-pill-secondary">G${r.goals} A${r.assists} S${r.saves}</span>
        </div>
      </div>
      <span class="metric-value">${r.impact_score}</span>
    </div>`);

  /* Clutch Impact */
  renderMetricList("#clutch-impact", clutch.players, (r) => `
    <div class="metric-row">
      ${rankIcon(r.rank)}
      ${badgeHTML(r.team_name, true)}
      <div class="metric-info">
        <div class="metric-name">${r.player_name}</div>
        <div class="metric-detail">
          <span>${r.team_name}</span>
          <span>${r.events_count} events</span>
        </div>
      </div>
      <span class="metric-value">${r.clutch_impact_score}</span>
    </div>`);
}

/* ===== Resources ===== */

async function loadResources() {
  const [teams, players, matches] = await Promise.all([
    fetchCollection("/teams"),
    fetchCollection("/players"),
    fetchCollection("/matches"),
  ]);
  state.teams = teams;
  state.players = players;
  state.matches = matches;
  renderTeamOptions();
  renderMatchOptions();
  renderTeams();
  renderPlayers();
  renderMatches();
}

async function refreshAll() {
  try {
    setStatus("Refreshing data...");
    await loadResources();
    await loadAnalytics();
    setStatus("Synced with API");
  } catch (error) {
    setStatus(error.message, true);
  }
}

/* ===== CRUD handlers ===== */

function formDataToObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function submitJson(path, method, payload) {
  return apiFetch(path, { method, body: JSON.stringify(payload) });
}

async function handleCreate(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = formDataToObject(form);
  const numFields = ["team_id","home_team_id","away_team_id","match_id","player_id","minute","home_score","away_score"];
  numFields.forEach((k) => { if (payload[k] !== undefined) payload[k] = Number(payload[k]); });
  const pathByFormId = { "team-form": "/teams", "player-form": "/players", "match-form": "/matches" };
  try {
    await submitJson(pathByFormId[form.id], "POST", payload);
    form.reset();
    if (form.id === "match-form") form.querySelector('[name="season"]').value = getSeason();
    setStatus("Created successfully.");
    await refreshAll();
  } catch (error) { setStatus(error.message, true); }
}

async function handleDelete(resource, id) {
  try {
    await apiFetch(`/${resource}/${id}`, { method: "DELETE" });
    setStatus(`${resource.slice(0, -1)} ${id} deleted.`);
    await refreshAll();
  } catch (error) { setStatus(error.message, true); }
}

async function handleEdit(resource, id) {
  const resourceMap = { teams: state.teams, players: state.players, matches: state.matches };
  const row = resourceMap[resource].find((item) => item.id === id);
  if (!row) return;
  try {
    let payload = {};
    if (resource === "teams") {
      payload = {
        name: window.prompt("Team name", row.name) || row.name,
        league: window.prompt("League", row.league) || row.league,
        country: window.prompt("Country", row.country) || row.country,
      };
    } else if (resource === "players") {
      payload = {
        name: window.prompt("Player name", row.name) || row.name,
        team_id: Number(window.prompt("Team ID", row.team_id) || row.team_id),
        position: window.prompt("Position", row.position) || row.position,
      };
    } else if (resource === "matches") {
      payload = {
        home_team_id: Number(window.prompt("Home team ID", row.home_team_id) || row.home_team_id),
        away_team_id: Number(window.prompt("Away team ID", row.away_team_id) || row.away_team_id),
        home_score: Number(window.prompt("Home score", row.home_score) || row.home_score),
        away_score: Number(window.prompt("Away score", row.away_score) || row.away_score),
        match_date: window.prompt("Match date", row.match_date) || row.match_date,
        season: window.prompt("Season", row.season) || row.season,
      };
    }
    await submitJson(`/${resource}/${id}`, "PUT", payload);
    setStatus(`${resource.slice(0, -1)} ${id} updated.`);
    await refreshAll();
  } catch (error) { setStatus(error.message, true); }
}

/* ===== Event binding ===== */

function bindEvents() {
  document.querySelector("#save-settings").addEventListener("click", () => {
    window.localStorage.setItem("fmi-api-key", getApiKey());
    window.localStorage.setItem("fmi-season", getSeason());
    setStatus("Settings saved locally.");
  });
  document.querySelector("#refresh-all").addEventListener("click", refreshAll);
  document.querySelectorAll("[data-analytics]").forEach((btn) => btn.addEventListener("click", loadAnalytics));
  ["#team-form", "#player-form", "#match-form"].forEach((s) => document.querySelector(s).addEventListener("submit", handleCreate));
  ["#reload-teams", "#reload-players", "#reload-matches"].forEach((s) => document.querySelector(s).addEventListener("click", loadResources));

  document.body.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const id = Number(button.dataset.id);
    const action = button.dataset.action;
    if (action === "delete-team") handleDelete("teams", id);
    else if (action === "delete-player") handleDelete("players", id);
    else if (action === "delete-match") handleDelete("matches", id);
    else if (action === "edit-team") handleEdit("teams", id);
    else if (action === "edit-player") handleEdit("players", id);
    else if (action === "edit-match") handleEdit("matches", id);
  });
}

/* ===== Init ===== */

async function init() {
  loadSavedSettings();
  bindEvents();
  document.querySelector('#match-form [name="season"]').value = getSeason();
  await refreshAll();
}

window.addEventListener("DOMContentLoaded", init);
