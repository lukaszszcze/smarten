import { useEffect, useRef, useState } from "react";

const CHARTJS_SRC = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js";
const ROLL_N = 5;

// Color groups keyed by the short prefix returned by typeOf(exerciseId).
// Must mirror tadzio_progress.html TYPE_META.
const TYPE_COLOR = {
  knowledge: "#5b9cf6",
  mc: "#5b9cf6",
  matching: "#5b9cf6",
  gapfill: "#5b9cf6",
  dialogue: "#4caf7d",
  tfni: "#4caf7d",
  spelling: "#f5c842",
  formation: "#f5c842",
  transform: "#f87171",
  grammar: "#f87171",
  cloze: "#f87171",
  writing: "#f87171",
};

const GROUP_LABELS = [
  { color: "#5b9cf6", label: "Wiedza / MC / Matching / Gap-fill" },
  { color: "#4caf7d", label: "Dialogi / TF/NI" },
  { color: "#f5c842", label: "Pisownia / Tworzenie słów" },
  { color: "#f87171", label: "Transformacje / Gramatyka / Cloze / Writing" },
];

let chartJsPromise = null;
function loadChartJs() {
  if (window.Chart) return Promise.resolve(window.Chart);
  if (chartJsPromise) return chartJsPromise;
  chartJsPromise = new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = CHARTJS_SRC;
    s.onload = () => resolve(window.Chart);
    s.onerror = () => reject(new Error("Chart.js failed to load"));
    document.head.appendChild(s);
  });
  return chartJsPromise;
}

function typeOf(exerciseId) {
  // Strip trailing _<num>; preserve everything before
  return (exerciseId || "").replace(/_\d+$/, "");
}

function buildDatasets(practice) {
  const dateToX = (d) => {
    const [y, m, day] = d.split("-").map(Number);
    return new Date(y, m - 1, day).getTime();
  };

  const colorAttempts = {};
  for (const a of practice) {
    const t = typeOf(a.exerciseId);
    const col = TYPE_COLOR[t] || "#aaa";
    const d = (a.date || "").slice(0, 10);
    if (!d) continue;
    const pct = Math.max(0, Math.min(100, a.percentage || 0));
    (colorAttempts[col] = colorAttempts[col] || []).push({ t: dateToX(d), pct });
  }

  const pointAt = (attempts, endExclusive) => {
    const start = Math.max(0, endExclusive - ROLL_N);
    const pcts = [];
    let sum = 0;
    for (let k = start; k < endExclusive; k++) {
      sum += attempts[k].pct;
      pcts.push(attempts[k].pct);
    }
    return { y: Math.round(sum / (endExclusive - start)), pcts };
  };

  return Object.entries(colorAttempts).map(([color, attempts]) => {
    attempts.sort((a, b) => a.t - b.t);
    const data = [];
    let lastT = null;
    for (let i = 0; i < attempts.length; i++) {
      const { t } = attempts[i];
      if (lastT !== null && t !== lastT) {
        const { y, pcts } = pointAt(attempts, i);
        data.push({ x: lastT, y, pcts });
      }
      lastT = t;
    }
    if (lastT !== null) {
      const { y, pcts } = pointAt(attempts, attempts.length);
      data.push({ x: lastT, y, pcts });
    }
    return {
      data,
      borderColor: color,
      backgroundColor: color + "cc",
      pointRadius: 3,
      pointHoverRadius: 5,
      borderWidth: 2,
      tension: 0.25,
    };
  });
}

const MIESIACE = ["sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"];

export default function ProgressTrendChart({ attempts }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const [ready, setReady] = useState(false);

  const practiceCount = (attempts || []).filter((a) => a.kind === "practice" && a.exerciseId && a.date).length;

  useEffect(() => {
    let cancelled = false;
    loadChartJs().then(() => { if (!cancelled) setReady(true); }).catch(() => {});
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (!ready || !canvasRef.current) return;
    const practice = (attempts || []).filter((a) => a.kind === "practice" && a.exerciseId && a.date);
    if (practice.length === 0) return;

    const Chart = window.Chart;
    const datasets = buildDatasets(practice);

    const allTimes = datasets.flatMap((d) => d.data.map((p) => p.x));
    const tMin = Math.min(...allTimes) - 2 * 86400000;
    const tMax = Math.max(...allTimes) + 2 * 86400000;

    const hLine80 = {
      id: "hLine80",
      afterDatasetsDraw(chart) {
        const { ctx, chartArea: { left, right }, scales: { y } } = chart;
        const yPos = y.getPixelForValue(80);
        ctx.save();
        ctx.strokeStyle = "#e8e8f0aa";
        ctx.lineWidth = 1;
        ctx.setLineDash([6, 4]);
        ctx.beginPath();
        ctx.moveTo(left, yPos);
        ctx.lineTo(right, yPos);
        ctx.stroke();
        ctx.fillStyle = "#e8e8f0aa";
        ctx.font = "11px system-ui";
        ctx.textAlign = "right";
        ctx.textBaseline = "bottom";
        ctx.fillText("80%", right - 4, yPos - 2);
        ctx.restore();
      },
    };

    if (chartRef.current) chartRef.current.destroy();
    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: { datasets },
      plugins: [hLine80],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items) => {
                const d = new Date(items[0].parsed.x);
                return `${d.getDate()} ${MIESIACE[d.getMonth()]} ${d.getFullYear()}`;
              },
              label: (ctx) => {
                const pcts = ctx.raw?.pcts || [];
                const lines = [`Średnia: ${ctx.parsed.y.toFixed(0)}%`];
                if (pcts.length) lines.push(`Próby: ${pcts.map((p) => p + "%").join(", ")}`);
                return lines;
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear", min: tMin, max: tMax,
            grid: { color: "#1a1a28" },
            ticks: {
              color: "#7a7a9a",
              callback: (v) => {
                const d = new Date(v);
                return `${d.getDate()} ${MIESIACE[d.getMonth()]}`;
              },
              maxTicksLimit: 8,
            },
          },
          y: {
            min: -5, max: 105,
            grid: { color: "#1a1a28" },
            ticks: {
              color: "#7a7a9a",
              callback: (v) => (v < 0 || v > 100 ? "" : v + "%"),
              stepSize: 25,
            },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [ready, attempts, practiceCount]);

  if (practiceCount === 0) return null;

  return (
    <div style={{
      background: "#13131a", border: "1px solid #1e1e2e", borderRadius: 12,
      padding: "16px 20px", marginBottom: 24,
    }}>
      <div style={{ color: "#c8c8d8", fontWeight: 700, fontSize: 14, marginBottom: 12 }}>
        Średni wynik (ostatnie 5 prób) wg grupy ćwiczeń
      </div>
      <div style={{ position: "relative", height: 260 }}>
        <canvas ref={canvasRef} />
      </div>
      <div style={{
        display: "flex", flexWrap: "wrap", gap: 12,
        marginTop: 10, fontSize: 11, color: "#7a7a9a",
      }}>
        {GROUP_LABELS.map((g) => (
          <div key={g.color} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 10, height: 10, borderRadius: "50%", background: g.color, display: "inline-block" }} />
            {g.label}
          </div>
        ))}
      </div>
    </div>
  );
}
