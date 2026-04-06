const COLUMN_LABELS = {
    month: "Month",
    starting_rating: "Start<br>Rating",
    ending_rating: "End<br>Rating",
    average_rating: "Avg.<br>Rating",
    average_entropy: "Avg.<br>Entropy",
    streak_flips: "FLP",

    days: "Days",
    wins: "W",
    losses: "L",
    ties: "T",
    winning_percentage: "PCT",

    points_won: "PW",
    points_lost: "PL",
    total_points_awarded: "PT",
    points_per_day: "PPD",
    point_winning_percentage: "PPCT",

    value_per_win: "VPW",
    value_per_loss: "VPL",
    value_diff: "VD",
    notional_diff: "ND",
    x_factor: "XF",
    total_diff: "+/-"
};

async function load() {
    const res = await fetch("/api/months");
    const rows = await res.json();
    console.log(rows[0]);
    const table = document.getElementById("table");
    table.innerHTML = "";

    const headers = Object.keys(COLUMN_LABELS);
    table.insertAdjacentHTML("beforeend",
        "<tr>" + headers.map(h => `<th>${COLUMN_LABELS[h]}</th>`).join("") + "</tr>");

    rows.forEach((row, i) => {
        const tr = document.createElement("tr");

        headers.forEach((h, index) => {
            const td = index === 0 ? document.createElement("th") : document.createElement("td");
            const value = row[h];
            td.textContent = value;

            // Add coloring class based on column and value
            let cls = null;
            let bolding = null;

            if (h === "month" && value === 1) td.textContent += "/" + row["year"];
            if (["average_rating", "notional_diff", "points_per_day"].includes(h)) td.textContent = value.toFixed(2);
            if (["average_entropy", "winning_percentage", "point_winning_percentage",
                "value_per_win", "value_per_loss", "value_diff"].includes(h)) td.textContent = value.toFixed(3);
            if (h === "x_factor") td.textContent = value.toFixed(1);
            
            if (["wins", "losses", "total_diff"].includes(h)) bolding = "memorable";

            if (["value_diff", "notional_diff", "x_factor", "total_diff"].includes(h)) {
                if (value > 0) {
                    td.textContent = "+" + td.textContent;
                    cls = "good";
                }
                else if (value < 0) cls = "bad";
                else cls = "tie";
            }

            if (["winning_percentage", "point_winning_percentage"].includes(h)) {
                if (value > 0.5) cls = "winning_pct";
                else if (value < 0.5) cls = "bad";
                else cls = "tied_pct";
            }

            if (cls) td.classList.add(cls);
            if (bolding) td.classList.add(bolding);

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
