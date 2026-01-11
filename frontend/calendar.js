const DAY = 24 * 60 * 60 * 1000;

let calendarByYear = {};
let currentYear = null;

function formatISO(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function buildDateRange(year) {
  const start = new Date(year, 0, 1);
  const end = new Date(year, 11, 31);

  // Align start to Monday
  while (start.getDay() !== 1) {
    start.setDate(start.getDate() - 1);
  }

  const dates = [];
  for (let d = new Date(start); d <= end; d = new Date(d.getTime() + DAY)) {
    dates.push(new Date(d));
  }
  return dates;
}

function groupByYear(days) {
  const byYear = {};

  for (const [dateStr, entry] of Object.entries(days)) {
    const year = new Date(dateStr).getFullYear();
    if (!byYear[year]) byYear[year] = {};
    byYear[year][dateStr] = entry;
  }

  return byYear;
}

async function renderCalendar() {
  let data;
  try {
    const res = await fetch("./calendar.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
  } catch (err) {
    console.error("Failed to load calendar.json", err);
    return;
  }

  const days = data.days;
  if (!days || Object.keys(days).length === 0) {
    console.error("calendar.json has no days");
    return;
  }

  // ✅ Group ALL days by year (no data loss)
  calendarByYear = groupByYear(days);

  // ✅ Populate selector
  const years = Object.keys(calendarByYear)
    .map(y => Number(y))
    .sort((a, b) => b - a);

  populateYearSelector(years);

  // Default to most recent year
  currentYear = years[0];
  renderYear(currentYear);
}

function populateYearSelector(years) {
  const select = document.getElementById("year-select");
  select.innerHTML = "";

  years.forEach(year => {
    const opt = document.createElement("option");
    opt.value = year;
    opt.textContent = year;
    select.appendChild(opt);
  });

  select.value = years[0];

  select.onchange = () => {
    currentYear = Number(select.value);
    renderYear(currentYear);
  };
}

function renderYear(year) {
  const days = calendarByYear[year];
  const calendar = document.getElementById("calendar");
  const panel = document.getElementById("day-panel");

  calendar.innerHTML = "";
  panel.classList.add("hidden");

  const dates = buildDateRange(year);

  dates.forEach(date => {
    const iso = formatISO(date);
    const entry = days[iso];

    const cell = document.createElement("div");
    cell.className =
      "w-3 h-3 rounded cursor-pointer transition " +
      (entry
        ? entry.status_color === "green"
          ? "bg-green-500 hover:bg-green-400"
          : "bg-red-500 hover:bg-red-400"
        : "bg-neutral-800");

    if (entry) {
      cell.onclick = () => showDay(entry, panel);
    }

    calendar.appendChild(cell);
  });

  renderMonthLabels(dates);
}


function renderMonthLabels(dates) {
  const labels = document.getElementById("month-labels");
  labels.innerHTML = "";

  let lastMonth = -1;

  dates.forEach(date => {
    const month = date.getMonth();
    const label = document.createElement("div");

    if (month !== lastMonth && date.getDate() <= 7) {
      label.textContent = date.toLocaleString("default", { month: "short" });
      lastMonth = month;
    }

    labels.appendChild(label);
  });
}

function showDay(entry, panel) {
  panel.innerHTML = `
    <h2 class="font-semibold mb-2">${entry.date}</h2>
    <div class="text-sm mb-2">
      Net:
      <span class="${entry.net_daily_avg >= 0 ? "text-green-400" : "text-red-400"}">
        ${entry.net_daily_avg.toFixed(2)}
      </span>
    </div>

    <ul class="space-y-1 text-sm">
      ${entry.statements.map(s => `
        <li class="flex justify-between gap-2">
          <span class="truncate">${s.desc}</span>
          <span class="${s.amount >= 0 ? "text-green-400" : "text-red-400"}">
            ${s.amount.toFixed(2)}
          </span>
        </li>
      `).join("")}
    </ul>
  `;

  panel.classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", renderCalendar);
