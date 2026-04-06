const COLUMN_LABELS = {
    start_date: "Start<br>Date",
    end_date: "End<br>Date",
    start_rating: "Start<br>Rating",
    end_rating: "End<br>Rating",
    total: "+/-"
};

async function load() {
    const res = await fetch("/api/years");
    const rows = await res.json();
    console.log(rows[0]);
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
            let bolding = null;
            if (['superb', 'memorable', 'legendary'].includes(h) && value) {
                if (h === 'superb') cls = value.includes("Superb") ? 'good' : 'bad';
                else if (h === 'memorable') cls = value.includes("Memorable") ? 'good' : 'bad';
                else if (h === 'legendary') cls = value.includes("Legendary") ? 'good' : 'bad';

                if (h === 'memorable') bolding = 'memorable';
                else if (h === 'legendary') bolding = 'legendary';
            }
            else if (typeof value === 'number' || !isNaN(parseFloat(value))) {
                const num = parseFloat(value);
                if (h === 'diff') {
                    if (num >= 5) cls = 'really-good';
                    else if (num >= 1) cls = 'good';
                    else if (num === 0) cls = 'tie';
                    else if (num >= -4) cls = 'bad';
                    else cls = 'really-bad';

                    if (Math.abs(num) >= 20) bolding = 'legendary';
                    else if (Math.abs(num) >= 10) bolding = 'memorable';

                } else if (h === 'diff_7') {
                    if (num >= 35) cls = 'really-good';
                    else if (num >= 1) cls = 'good';
                    else if (num === 0) cls = 'tie';
                    else if (num >= -34) cls = 'bad';
                    else cls = 'really-bad';

                    if (Math.abs(num) >= 140) bolding = 'legendary';
                    else if (Math.abs(num) >= 70) bolding = 'memorable';

                } else if (h === 'diff_30') {
                    if (num >= 150) cls = 'really-good';
                    else if (num >= 1) cls = 'good';
                    else if (num === 0) cls = 'tie';
                    else if (num >= -149) cls = 'bad';
                    else cls = 'really-bad';

                    if (Math.abs(num) >= 600) bolding = 'legendary';
                    else if (Math.abs(num) >= 300) bolding = 'memorable';

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
            if (bolding) td.classList.add(bolding);

            // if (h === "diff") {
            //     td.classList.add("editable");
            //     td.contentEditable = true;

            //     td.onblur = async () => {
            //         await fetch("/edit", {
            //             method: "POST",
            //             headers: { "Content-Type": "application/json" },
            //             body: JSON.stringify({ row: i, diff: parseFloat(td.textContent) })
            //         });
            //         load();
            //     };
            // }

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
