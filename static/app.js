const COLUMN_LABELS = {
    date: "Date",
    rating: "Rating",
    diff: "+/-",
    diff_7: "WD",
    diff_30: "MD",
    diff_365: "YD",
    entropy: "ENT",
    avg_entropy: "ENT90",
    last_30_wins: "L30W",
    wins: "YTD<br>W",
    losses: "YTD<br>L",
    ties: "YTD<br>T",
    points_won: "YTD<br>PW",
    points_lost: "YTD<br>PL",
    total_points: "YTD<br>TOT",
    streak: "STRK",
    record: "REC?"
};

async function load() {
    const res = await fetch("/data");
    const rows = await res.json();
    const table = document.getElementById("table");
    table.innerHTML = "";

    const headers = Object.keys(rows[0]);
    table.insertAdjacentHTML("beforeend",
        "<tr>" + headers.map(h => `<th>${COLUMN_LABELS[h]}</th>`).join("") + "</tr>");

    rows.forEach((row, i) => {
        const tr = document.createElement("tr");

        headers.forEach(h => {
            const td = document.createElement("td");
            td.textContent = row[h];

            // Add coloring class based on column and value
            const value = row[h];
            let cls = null;
            if (typeof value === 'number' || !isNaN(parseFloat(value))) {
                const num = parseFloat(value);
                if (h === 'diff') {
                    if (num >= 5) cls = 'really-good';
                    else if (num >= 1) cls = 'good';
                    else if (num === 0) cls = 'tie';
                    else if (num >= -4) cls = 'bad';
                    else cls = 'really-bad';
                } else if (h === 'diff_7') {
                    if (num >= 35) cls = 'really-good';
                    else if (num >= 1) cls = 'good';
                    else if (num === 0) cls = 'tie';
                    else if (num >= -34) cls = 'bad';
                    else cls = 'really-bad';
                } else if (h === 'diff_30') {
                    if (num >= 150) cls = 'really-good';
                    else if (num >= 1) cls = 'good';
                    else if (num === 0) cls = 'tie';
                    else if (num >= -149) cls = 'bad';
                    else cls = 'really-bad';
                } else if (h === 'diff_365') {
                    if (num > 0) cls = 'good';
                    else if (num < 0) cls = 'bad';
                    else cls = 'tie';
                } else if (h === 'entropy' || h === 'avg_entropy') {
                    cls = num < 0.5 ? 'good' : 'bad';
                } else if (h === 'last_30_wins') {
                    if (num >= 20) cls = 'really-good';
                    else if (num <= 10) cls = 'really-bad';
                    else if (num > 15) cls = 'good';
                    else if (num === 15) cls = 'tie';
                    else cls = 'bad';
                } else if (h === "streak" && num >= 10) {
                    cls = 'tie';
                }
            } else if (h === 'record' && value === "✓") {
                cls = 'really-good';
            }
            if (cls) td.classList.add(cls);

            if (h === "diff") {
                td.classList.add("editable");
                td.contentEditable = true;

                td.onblur = async () => {
                    await fetch("/edit", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ row: i, diff: parseFloat(td.textContent) })
                    });
                    load();
                };
            }

            tr.appendChild(td);
        });

        table.appendChild(tr);
    });
}

async function undo() {
    await fetch("/undo", { method: "POST" });
    load();
}

load();
