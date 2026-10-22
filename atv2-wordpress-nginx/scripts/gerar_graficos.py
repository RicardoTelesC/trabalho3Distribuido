#!/usr/bin/env python3
"""
Gera gráficos a partir dos CSV exportados pelo Locust (modo headless).

Espera arquivos em resultados/<cenario>/inst_<N>/users_<U>_stats.csv
ou um manifest.json gerado por run_locust_headless.ps1.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("Instale matplotlib: pip install matplotlib") from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "resultados"
DEFAULT_GRAFICOS = ROOT / "graficos"


def read_stats_row(stats_path: Path) -> dict | None:
    with stats_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == "Aggregated":
                return row
    return None


def collect_from_manifest(manifest_path: Path) -> list[dict]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = []
    for entry in data:
        stats = read_stats_row(Path(entry["stats_csv"]))
        if not stats:
            continue
        rows.append(
            {
                "cenario": entry["cenario"],
                "instancias": int(entry["instancias"]),
                "usuarios": int(entry["usuarios"]),
                "rps": float(stats.get("Requests/s", 0) or 0),
                "avg_ms": float(stats.get("Average Response Time", 0) or 0),
                "p95_ms": float(stats.get("95%", 0) or 0),
            }
        )
    return rows


def collect_from_tree(results_dir: Path) -> list[dict]:
    rows = []
    for stats_path in results_dir.rglob("*_stats.csv"):
        parts = stats_path.parts
        cenario = stats_path.parent.parent.name if len(parts) >= 2 else "desconhecido"
        inst = 3
        users = 0
        for p in stats_path.parts:
            if p.startswith("inst_"):
                inst = int(p.replace("inst_", ""))
            if p.startswith("users_"):
                users = int(p.replace("users_", "").split("_")[0])
        stats = read_stats_row(stats_path)
        if not stats or users == 0:
            continue
        rows.append(
            {
                "cenario": cenario,
                "instancias": inst,
                "usuarios": users,
                "rps": float(stats.get("Requests/s", 0) or 0),
                "avg_ms": float(stats.get("Average Response Time", 0) or 0),
                "p95_ms": float(stats.get("95%", 0) or 0),
            }
        )
    return rows


def plot_metric(rows: list[dict], metric_key: str, ylabel: str, out_dir: Path) -> None:
    by_cenario = defaultdict(list)
    for r in rows:
        by_cenario[r["cenario"]].append(r)

    for cenario, items in by_cenario.items():
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f"{cenario} — {ylabel}")

        for ax, group_key, xlabel in [
            (axes[0], "usuarios", "Usuários simultâneos (Locust)"),
            (axes[1], "instancias", "Instâncias WordPress"),
        ]:
            series: dict[int, list[tuple[int, float]]] = defaultdict(list)
            for it in items:
                fixed = it["instancias"] if group_key == "usuarios" else it["usuarios"]
                varying = it[group_key]
                series[fixed].append((varying, it[metric_key]))
            for fixed, points in sorted(series.items()):
                points.sort(key=lambda x: x[0])
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                label = (
                    f"{fixed} instância(s)"
                    if group_key == "usuarios"
                    else f"{fixed} usuário(s)"
                )
                ax.plot(xs, ys, marker="o", label=label)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend()
            ax.grid(True, alpha=0.3)

        safe_name = cenario.replace(" ", "_")
        out_path = out_dir / f"{safe_name}_{metric_key}.png"
        fig.tight_layout()
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"Gráfico: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_GRAFICOS)
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    manifest = args.manifest or (args.results / "manifest.json")
    if manifest.is_file():
        rows = collect_from_manifest(manifest)
    else:
        rows = collect_from_tree(args.results)

    if not rows:
        raise SystemExit(
            "Nenhum resultado encontrado. Execute os testes headless ou crie resultados/manifest.json."
        )

    plot_metric(rows, "rps", "Requisições por segundo", args.out)
    plot_metric(rows, "avg_ms", "Tempo médio de resposta (ms)", args.out)
    plot_metric(rows, "p95_ms", "Percentil 95 (ms)", args.out)


if __name__ == "__main__":
    main()
