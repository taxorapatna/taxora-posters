#!/usr/bin/env python3
"""Render posters/*.json -> out/<slug>.jpg (1080x1350) with headless Chrome. Skips slugs already rendered."""
import json, pathlib, subprocess, html, sys
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parent
CSS = (ROOT / "template" / "style.css").read_text(encoding="utf-8")
FRAME = (ROOT / "template" / "frame.html").read_text(encoding="utf-8")
FONTS = ROOT / "fonts"
out = ROOT / "out"; out.mkdir(exist_ok=True)
tmp = ROOT / ".tmp"; tmp.mkdir(exist_ok=True)
face = "".join(f"@font-face{{font-family:P;src:url('file://{FONTS}/Poppins-{n}.ttf');font-weight:{w}}}" for n, w in (("Regular",400),("Medium",500),("Bold",700)))
done = 0
for f in sorted((ROOT / "posters").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    slug = d["slug"]
    jpg = out / f"{slug}.jpg"
    if jpg.exists() and not d.get("force"):
        continue
    page = ("<!doctype html><html><head><meta charset='utf-8'><style>" + face +
            "*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1350px;overflow:hidden}body{font-family:P,'Noto Sans Devanagari',sans-serif;color:#13233a}" + CSS +
            "</style></head><body>" + FRAME.replace("{{TAG}}", html.escape(d.get("tag", "GST · ITR · TDS"))).replace("{{BODY}}", d["body"]) + "</body></html>")
    h = tmp / f"{slug}.html"; h.write_text(page, encoding="utf-8")
    png = tmp / f"{slug}.png"
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--allow-file-access-from-files", "--virtual-time-budget=4000", "--force-device-scale-factor=1",
                    f"--screenshot={png}", "--window-size=1080,1350", h.as_uri()], check=True)
    Image.open(png).convert("RGB").resize((1080, 1350)).save(jpg, "JPEG", quality=88, optimize=True)
    print("rendered", slug); done += 1
print("total rendered:", done)
