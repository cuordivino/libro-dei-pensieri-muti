# -*- coding: utf-8 -*-
import json
import os

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
with open(os.path.join(base_dir, "poems.json"), "r", encoding="utf-8") as f:
    db = json.load(f)

meta = db["meta"]
poems = db["poems"]

md_lines = []
md_lines.append(f"# {meta['title']}")
md_lines.append(f"### {meta['subtitle']}\n")
md_lines.append(f"**Autore:** [{meta['author']} ({meta['authorPseudonym']})]({meta['instagramUrl']})  ")
md_lines.append(f"**Opera d'origine:** *{meta['originalWork']}*  ")
md_lines.append(f"**Profilo Instagram Ufficiale:** [{meta['instagramHandle']}]({meta['instagramUrl']})\n")
md_lines.append("---\n")

md_lines.append("## NOTA BIOGRAFICA DELL'AUTORE\n")
md_lines.append(meta["authorNote"] + "\n\n---\n")

md_lines.append("## PREFAZIONE\n")
md_lines.append(f"### La Carne e il Calice: L'eresia purificatrice\n")
md_lines.append(meta["preface"] + "\n\n---\n")

md_lines.append("## INDICE DEGLI STATI D'ANIMO\n")
for mm in meta["macroMoods"]:
    if mm["key"] == "all": continue
    count = len([p for p in poems if p["macroMoodKey"] == mm["key"]])
    md_lines.append(f"- **{mm['icon']} {mm['name']}** ({count} poesie): {mm['desc']}")

md_lines.append("\n---\n")

current_sec = ""
for p in poems:
    sec = f"{p['section']} — {p['sectionTitle']}"
    if sec != current_sec:
        current_sec = sec
        md_lines.append(f"\n# {current_sec}\n")
        md_lines.append("---\n")

    num_str = f"{p['number']}. " if p['number'] != '—' else ""
    md_lines.append(f"### {num_str}{p['title']}\n")
    md_lines.append(f"> **Stato d'Animo:** *{p['moodPrimary']}*  ")
    md_lines.append(f"> **Il Senso del Pensiero Muto:** {p['moodSense']}\n")
    md_lines.append("```text")
    md_lines.append(p["text"])
    md_lines.append("```\n")

with open(os.path.join(base_dir, "LIBRO_DEI_PENSIERI_MUTI.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Created LIBRO_DEI_PENSIERI_MUTI.md")
