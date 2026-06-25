#!/usr/bin/env python3
"""Build Vue 3 SPA study-notes site using Synthesis design tokens.

Run: python build.py
Output: _site/index.html
"""

import html as _html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml

ROOT     = Path(__file__).parent
BOOKS    = ROOT / "books"
STATE    = ROOT / "state"
SITE     = ROOT / "_site"

# ──────────────────────────────────────────────────────────────────────────────
# Full RAE chapter manifest (matches design prototype)
# ──────────────────────────────────────────────────────────────────────────────

PARTS = [
    {"label": "Licensing & Operating",            "color": "var(--c-accent-purple)", "blurb": "The hobby, the rules, and how to operate on the air."},
    {"label": "Electrical Theory",                "color": "var(--c-accent-cyan)",   "blurb": "From electrons to tuned circuits — the maths that underpins radio."},
    {"label": "Semiconductors & Circuits",        "color": "var(--c-accent-sky)",    "blurb": "Diodes, transistors, oscillators and the building blocks of equipment."},
    {"label": "Radio Systems",                    "color": "var(--c-accent-blue)",   "blurb": "Modulation, transmitters and receivers as complete systems."},
    {"label": "Antennas & Propagation",           "color": "var(--c-accent-pink)",   "blurb": "Getting the signal out — antennas, propagation and compatibility."},
    {"label": "Measurement, Digital & Practical", "color": "var(--c-accent-indigo)", "blurb": "Instruments, DSP, digital modes, safety and the exam itself."},
]

CHAPTERS = [
    {"n":"1",  "p":0, "t":"Overview of Amateur Radio",      "s":["1.1 Communicating with other amateurs","1.2 Collecting QSL cards","1.3 Building radio and electronics equipment","1.4 Building antennas","1.5 Public service and emergency communications","1.6 DXing","1.7 DXpeditions","1.8 Contests","1.9 Satellite communications","1.10 Maritime and off-road communications","1.11 RaDAR","1.12 The governance of amateur radio","1.13 Licence requirements in South Africa","1.14 The Code of Conduct","1.15 The Radio Amateur Examination","1.16 Restrictions on the use of an amateur radio station"]},
    {"n":"2",  "p":0, "t":"Operating Procedures",           "s":["2.1 International regulations","2.2 HF phone procedures","2.3 Telegraphy procedures","2.4 Repeater procedures","2.5 Emergency communications and social responsibility","2.6 General points","2.7 Keeping a log","2.8 Exchanging QSL cards","2.9 Electronic confirmations","Revision Questions"]},
    {"n":"3",  "p":1, "t":"Basic Electrical Concepts",      "s":["3.1 Atoms and electrons","3.2 Conductors and insulators","3.3 Electric current","3.4 Electric potential","3.5 Power","3.6 Where energy comes from","3.7 Units and abbreviations","3.8 Scientific notation","3.9 Number formats","Summary","Revision Questions"]},
    {"n":"4",  "p":1, "t":"Resistance and Ohm's Law",       "s":["4.1 Resistance","4.2 Symbols in mathematical equations","4.3 Rearranging Ohm's Law","Summary","Revision Questions"]},
    {"n":"5",  "p":1, "t":"The Resistor and Potentiometer", "s":["5.1 The resistor","5.2 Different types of resistor","5.3 The resistor colour code","5.4 Expressing resistor values","5.5 The potentiometer","Summary","Revision Questions"]},
    {"n":"6",  "p":1, "t":"Direct Current Circuits",        "s":["6.1 Direct current and voltage","6.2 Kirchoff's laws","6.3 Resistors in series","6.4 Resistors in parallel","6.5 The voltage divider","Summary","Revision Questions"]},
    {"n":"7",  "p":1, "t":"Power in DC Circuits",           "s":["7.1 Power dissipation in resistances","7.2 Using Ohm's Law with the formula for power","7.3 Electrical sources","7.4 Matching source and load","7.5 Efficiency","Summary","Revision Questions"]},
    {"n":"8",  "p":1, "t":"Alternating Current",            "s":["8.1 Introduction","8.2 The sine signal","8.3 Cycles and half-cycles","8.4 Period and frequency","8.5 Wavelength and the speed of light","8.6 Phase","8.7 RMS voltage and current","8.8 Frequency ranges","Summary","Revision Questions"]},
    {"n":"9",  "p":1, "t":"Capacitance and the Capacitor",  "s":["9.1 The capacitor","9.2 Capacitors in AC circuits","9.3 Capacitive reactance","9.4 Phase of current and voltage","9.5 Capacitors in parallel and series","9.6 Types of capacitor","Summary","Revision Questions"]},
    {"n":"10", "p":1, "t":"Inductance and the Inductor",    "s":["10.1 Inductors","10.2 Inductor values","10.3 Inductors in AC circuits","10.4 Inductive reactance","10.5 Ohm\u2019s Law and reactance","10.6 Phase relationship between voltage and current","10.7 Inductors in series and parallel","Summary","Revision Questions"]},
    {"n":"11", "p":1, "t":"Tuned Circuits",                 "s":["11.1 Reactances in series","11.2 Reactances in parallel","11.3 The series tuned circuit","11.4 Impedance","11.5 The parallel tuned circuit","11.6 Circulating current in a parallel tuned circuit","11.7 Calculating the resonant frequency","11.8 Circuit losses and the quality factor","Summary","Revision Questions"]},
    {"n":"12", "p":1, "t":"Decibel Notation",               "s":["12.1 The decibel","12.2 Adding decibels","12.3 Representing losses","12.4 Quick and easy decibel conversions","12.5 Expressing voltage ratios as decibels","12.6 Expressing power levels in dBW and dBm","Summary","Revision Questions"]},
    {"n":"13", "p":1, "t":"Filters",                        "s":["13.1 The lowpass filter","13.2 The highpass filter","13.3 The bandpass filter","13.4 Crystal filters","13.5 The bandstop filter","13.6 More sophisticated filters","13.7 Practical RF circuits","Summary","Revision Questions"]},
    {"n":"14", "p":1, "t":"The Transformer",                "s":["14.1 Theory of operation","14.2 Turns ratio","14.3 Voltage ratio","14.4 Current ratio","14.5 Impedance ratio","14.6 Applications","Summary","Revision Questions"]},
    {"n":"15", "p":2, "t":"Semiconductors and the Diode",   "s":["15.1 Semiconductors","15.2 The junction diode","15.3 The half-wave rectifier","15.4 The full-wave rectifier","15.5 Special diodes","Summary","Revision Questions"]},
    {"n":"16", "p":2, "t":"The Power Supply",               "s":["16.1 Simple power supply","16.2 A regulated power supply","16.3 Switching power supplies","16.4 Batteries","Summary","Revision Questions"]},
    {"n":"17", "p":2, "t":"The Bipolar Junction Transistor","s":["17.1 Types of transistors","17.2 Operation of the NPN transistor","17.3 Operation of the PNP transistor","17.4 The transistor switch","Summary","Revision Questions"]},
    {"n":"18", "p":2, "t":"The Transistor Amplifier",       "s":["18.1 Amplification","18.2 Class C amplifiers","18.3 The Class A common-emitter amplifier","18.4 The common-collector (emitter-follower) amplifier","18.5 The common-base amplifier","18.6 The Class AB amplifier","18.7 Field-effect transistors","18.8 Thermionic tubes","18.9 Integrated circuits","Summary","Revision Questions"]},
    {"n":"19", "p":2, "t":"The Oscillator",                 "s":["19.1 Oscillators","19.2 Principle of operation","19.3 The Barkhausen criteria for oscillation","19.4 The Colpitts oscillator","19.5 Buffering","19.6 The Hartley oscillator","19.7 The Voltage-Controlled Oscillator","19.8 The crystal oscillator","Summary","Revision Questions"]},
    {"n":"20", "p":2, "t":"Frequency Translation",          "s":["20.1 The frequency multiplier","20.2 The frequency divider","20.3 The Phase Locked Loop frequency synthesiser","20.4 The mixer","Summary","Revision Questions"]},
    {"n":"21", "p":3, "t":"Modulation Methods",             "s":["21.1 Modulation","21.2 Amplitude modulation (AM)","21.3 Double-sideband suppressed-carrier modulation","21.4 Single-sideband (SSB)","21.5 Continuous wave (CW)","21.6 Frequency modulation (FM)","21.7 Digital modulation techniques","Summary","Revision Questions"]},
    {"n":"22", "p":3, "t":"The Transmitter",                "s":["22.1 A single-band CW transmitter","22.2 An amplitude-modulated (AM) transmitter","22.3 A simple SSB transmitter","22.4 A frequency-synthesised VHF FM transmitter"]},
    {"n":"23", "p":3, "t":"Receiver Fundamentals",          "s":["23.1 Noise in receivers","23.2 Receiver characteristics","23.3 The tuned radio frequency (TRF) receiver","23.4 The direct-conversion receiver","Summary","Revision Questions"]},
    {"n":"24", "p":3, "t":"The Superheterodyne Receiver",   "s":["24.1 The single-conversion superhet","24.2 Multiple-conversion superhet receivers","24.3 Noise limiters and noise blankers","24.4 Frequency modulation (FM) reception","24.5 Reciprocal mixing","Summary","Revision Questions"]},
    {"n":"25", "p":3, "t":"Transceivers and Transverters",  "s":["25.1 The transceiver","25.2 The transverter","Summary","Revision Questions"]},
    {"n":"26", "p":4, "t":"Antennas",                       "s":["26.1 Antennas and electromagnetic fields","26.2 The electromagnetic spectrum","26.3 Polarisation","26.4 The half-wave dipole","26.5 The quarter-wave vertical","26.6 The groundplane antenna","26.7 Short and long vertical antennas","26.8 Loop antennas","26.9 Folded dipole","26.10 Multi-element arrays","26.11 The Yagi","26.12 Reflector antennas","26.13 Antenna gain","26.14 Effective Isotropic Radiated Power","26.15 Efficiency","26.16 Directivity as opposed to gain","26.17 Other performance measures","26.18 Stacking","26.19 Feedlines","26.20 Standing-wave ratio","26.21 Baluns","26.22 Multiband antennas","26.23 The log-periodic array","26.24 Making practical antennas","Summary","Revision Questions"]},
    {"n":"27", "p":4, "t":"Propagation",                    "s":["27.1 Frequency bands","27.2 Path loss","27.3 Direct wave (line of sight) propagation","27.4 Groundwave propagation","27.5 The atmosphere","27.6 Skywave (ionospheric) propagation","27.7 Exotic ionospheric propagation modes","27.8 Tropospheric bending, scatter and ducting","27.9 Earth-Moon-Earth (EME)","27.10 Amateur satellites","27.11 Propagation prediction","Summary","Revision Questions"]},
    {"n":"28", "p":4, "t":"Electromagnetic Compatibility",   "s":["28.1 Definition of electromagnetic compatibility","28.2 Intentional and unintentional radiators","28.3 Interference to non-receiving equipment","28.4 Intentional radiators interfering with receivers","28.5 Shared bands","28.6 Causes of interference","28.7 Transmitter defects","28.8 Receiver defects","28.9 Common-mode chokes","28.10 Direct radiation and shielding","28.11 Sensible measures against interference","Summary","Revision Questions"]},
    {"n":"29", "p":5, "t":"Measurements",                   "s":["29.1 The ammeter","29.2 The voltmeter","29.3 The multimeter","29.4 Frequency counter","29.5 Power and SWR meter","29.6 The oscilloscope","29.7 Marker generator","29.8 The dip meter","29.9 The dummy load","29.10 The field strength meter","29.11 The absorption wavemeter","29.12 The two-tone signal generator","Summary","Revision Questions"]},
    {"n":"30", "p":5, "t":"Digital Systems",                 "s":["30.1 Advantages of digital systems","30.2 Principles of Digital Signal Processing","30.3 Digital filters","30.4 Direct digital synthesis","30.5 The Fourier transform","30.6 Convolution","30.7 SDR platforms","Summary","Revision Questions"]},
    {"n":"31", "p":5, "t":"Digital Communication Modes",    "s":["31.1 Practical implementation of digital communications","31.2 Digital modulation","31.3 Text modes","31.4 Image modes","31.5 Digital voice\u2014the future?","Summary","Revision Questions"]},
    {"n":"32", "p":5, "t":"Safety Considerations",          "s":["32.1 The human body","32.2 Mains power supply","32.3 High voltages","32.4 Lightning","Revision Questions"]},
    {"n":"33", "p":5, "t":"Before You Go",                  "s":["33.1 Meeting the standard","33.2 Writing the RAE"]},
    {"n":"A",  "p":5, "t":"Glossary of Abbreviations",      "s":["A list of the abbreviations and acronyms used throughout amateur radio."]},
]

# ──────────────────────────────────────────────────────────────────────────────
# Markdown helpers
# ──────────────────────────────────────────────────────────────────────────────

_MD_EXT = ["markdown.extensions.tables","markdown.extensions.fenced_code",
           "markdown.extensions.admonition","markdown.extensions.toc"]

def md_to_html(text: str) -> str:
    text = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
    md = markdown.Markdown(extensions=_MD_EXT)
    body = md.convert(text)
    # mermaid fenced blocks -> divs
    body = re.sub(
        r'<pre><code[^>]*class="[^"]*(?:language-)?mermaid[^"]*"[^>]*>(.*?)</code></pre>',
        lambda m: f'<div class="mermaid">{_html.unescape(m.group(1))}</div>',
        body, flags=re.DOTALL)
    return body

def load_chapter_html(book_docs: Path, ch_n: str) -> str | None:
    """Return rendered HTML for a chapter number, or None if not available."""
    pat = re.compile(rf"^ch{int(ch_n):02d}-.*\.md$") if ch_n.isdigit() else None
    if pat is None:
        return None
    for f in book_docs.glob("*.md"):
        if pat.match(f.name):
            return md_to_html(f.read_text(encoding="utf-8"))
    return None

def parse_progress() -> dict[str, list]:
    path = STATE / "progress.md"
    if not path.exists():
        return {}
    result: dict[str, list] = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            current = m.group(1).strip(); result[current] = []; continue
        if current and re.match(r"^\|\s*\d", line):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3:
                try:
                    result[current].append((int(parts[0]), parts[1], parts[2].lower()))
                except (ValueError, IndexError):
                    pass
    return result

def count_glossary() -> int:
    p = STATE / "glossary.md"
    return sum(1 for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("**")) if p.exists() else 0

# ──────────────────────────────────────────────────────────────────────────────
# Main build
# ──────────────────────────────────────────────────────────────────────────────

FAVICON_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="7" fill="#130F0D"/>
  <circle cx="16" cy="16" r="2.6" fill="#59FFF5"/>
  <path d="M10.2 10.2a8.2 8.2 0 0 0 0 11.6M21.8 10.2a8.2 8.2 0 0 1 0 11.6"
        fill="none" stroke="#59FFF5" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M5.8 5.8a14.4 14.4 0 0 0 0 20.4M26.2 5.8a14.4 14.4 0 0 1 0 20.4"
        fill="none" stroke="#59FFF5" stroke-width="1.6" stroke-linecap="round" opacity="0.45"/>
</svg>
"""


def build():
    SITE.mkdir(exist_ok=True)

    progress   = parse_progress()
    gloss_count = count_glossary()

    # Build status map from progress.md: chapter number -> status
    status_map: dict[str, str] = {}
    for slug, entries in progress.items():
        for num, title, status in entries:
            status_map[str(num)] = status

    # Load real HTML for available chapters
    book_docs = BOOKS / "rae-intro" / "docs"
    done_count = sum(1 for v in status_map.values() if v == "done")
    in_prog    = sum(1 for v in status_map.values() if v == "in progress")
    queued     = sum(1 for v in status_map.values() if v == "queued")

    # Build chapter records for JSON
    chapters_json = []
    for ch in CHAPTERS:
        n = ch["n"]
        status = status_map.get(n, "queued") if n.isdigit() else "queued"
        html_content = None
        if status == "done":
            html_content = load_chapter_html(book_docs, n)
        chapters_json.append({
            "n": n,
            "p": ch["p"],
            "t": ch["t"],
            "s": ch["s"],
            "status": status,
            "html": html_content or "",
        })

    # Copy figures
    figures_src = book_docs / "figures"
    if figures_src.exists():
        shutil.copytree(figures_src, SITE / "figures", dirs_exist_ok=True)

    data = {
        "parts": PARTS,
        "chapters": chapters_json,
        "stats": {
            "done": done_count,
            "inProgress": in_prog,
            "queued": queued,
            "glossary": gloss_count,
            "total": len([c for c in CHAPTERS if c["n"].isdigit()]),
        },
    }

    (SITE / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")

    html = render_spa(data)
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"_site/index.html — {len(chapters_json)} chapters, {done_count} done")


# ──────────────────────────────────────────────────────────────────────────────
# SPA template
# ──────────────────────────────────────────────────────────────────────────────

def render_spa(data: dict) -> str:
    data_json = json.dumps(data, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Amateur Radio Study Notes</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Inter+Tight:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<style>
/* ── Synthesis design tokens ─────────────────────────────────────────── */
:root {{
  --c-ink:           #130F0D;
  --c-ink-90:        #1B1816;
  --c-ink-80:        #2A2522;
  --c-ink-60:        #4A4440;
  --c-paper-soft:    #F3F3F0;
  --c-paper-muted:   #E8E6E0;
  --c-mute:          #616167;
  --c-accent-purple: #B841FB;
  --c-accent-blue:   #7D93FC;
  --c-accent-indigo: #7E68FE;
  --c-accent-cyan:   #59FFF5;
  --c-accent-pink:   #F966B4;
  --c-accent-sky:    #5AC6FF;
  --c-link:          #57D2BE;
  --font-display: "Inter Tight", system-ui, -apple-system, sans-serif;
  --font-body:    "Inter", system-ui, -apple-system, sans-serif;
  --font-mono:    "JetBrains Mono", ui-monospace, Menlo, monospace;
  --glow-cyan:   0 0 24px rgba(89,255,245,.35), 0 0 64px rgba(89,255,245,.18);
  --glow-purple: 0 0 24px rgba(184,65,251,.35), 0 0 64px rgba(184,65,251,.18);
  --glow-pink:   0 0 24px rgba(249,102,180,.35), 0 0 64px rgba(249,102,180,.18);
  /* semantic */
  --bg:          var(--c-ink);
  --bg-elevated: var(--c-ink-90);
  --fg:          var(--c-paper-soft);
  --fg-muted:    #B6B4AF;
  --fg-dim:      #8C8985;
  --border:      rgba(243,243,240,.10);
  --border-strong: rgba(243,243,240,.18);
}}
/* light theme overrides */
.theme-light {{
  --bg:          #F3F3F0;
  --bg-elevated: #FFFFFF;
  --fg:          #130F0D;
  --fg-muted:    #4A4440;
  --fg-dim:      #6E6A64;
  --border:      rgba(19,15,13,.10);
  --border-strong: rgba(19,15,13,.16);
  --glow-cyan:   0 2px 18px rgba(19,15,13,.06);
  --glow-purple: 0 2px 18px rgba(184,65,251,.14);
  --c-ink-60:    #CFCCC4;
}}

*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ height:100%; }}
body {{
  background:var(--bg);
  color:var(--fg);
  font-family:var(--font-body);
  font-size:16px;
  line-height:1.45;
  -webkit-font-smoothing:antialiased;
  transition:background .25s,color .25s;
}}
::selection {{ background:rgba(89,255,245,.28); }}

/* scrollbar */
.ar-scroll::-webkit-scrollbar {{ width:8px; }}
.ar-scroll::-webkit-scrollbar-track {{ background:transparent; }}
.ar-scroll::-webkit-scrollbar-thumb {{ background:var(--c-ink-60); border-radius:8px; border:2px solid transparent; background-clip:padding-box; }}
.ar-scroll::-webkit-scrollbar-thumb:hover {{ background:var(--c-mute); background-clip:padding-box; }}

/* animations */
@keyframes ar-fade-up {{ from{{opacity:0;transform:translateY(14px)}} to{{opacity:1;transform:translateY(0)}} }}
@keyframes ar-ripple   {{ 0%{{transform:scale(.12);opacity:.9}} 100%{{transform:scale(2.8);opacity:0}} }}
@keyframes ar-dash     {{ from{{stroke-dashoffset:var(--dl)}} to{{stroke-dashoffset:0}} }}
@keyframes ar-float    {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-5px)}} }}
@keyframes ar-pulse    {{ 0%,100%{{opacity:.35}} 50%{{opacity:1}} }}
.ar-ripple {{ transform-box:fill-box; transform-origin:center; }}
.katex {{ font-size:1.08em; }}
.katex-display {{ margin:0; }}

/* ── layout ─────────────────────────────────────────────────────────── */
#app {{ display:flex; flex-direction:column; min-height:100vh; }}

/* mobile topbar */
.topbar {{
  display:none;
  position:sticky; top:0; z-index:50;
  align-items:center; gap:14px;
  padding:14px 18px;
  background:var(--bg-elevated);
  border-bottom:1px solid var(--border);
}}
.topbar-title {{
  font-family:var(--font-display);
  font-weight:700;
  font-size:18px;
  letter-spacing:-0.02em;
}}

/* backdrop */
.backdrop {{
  display:none;
  position:fixed; inset:0; z-index:55;
  background:rgba(8,7,5,.6);
  backdrop-filter:blur(2px);
}}

.shell {{ display:flex; flex:1; align-items:stretch; }}

/* sidebar */
.sidebar {{
  width:320px; flex:0 0 320px;
  height:100vh; position:sticky; top:0;
  overflow-y:auto;
  background:var(--bg-elevated);
  border-right:1px solid var(--border);
  padding:26px 18px 60px;
  z-index:60;
  transition:transform .32s cubic-bezier(.2,.8,.2,1);
}}
.sb-logo {{
  display:flex; align-items:flex-start; gap:13px;
  width:100%; text-align:left;
  background:transparent; border:0;
  padding:6px 8px 4px; cursor:pointer; color:var(--fg);
}}
.sb-logo-icon {{
  display:flex; align-items:center; justify-content:center;
  flex:0 0 auto; width:42px; height:42px;
  border-radius:13px;
  border:1.5px solid var(--c-accent-cyan);
  box-shadow:var(--glow-cyan);
}}
.sb-logo-name {{
  font-family:var(--font-display);
  font-weight:800; font-size:19px;
  letter-spacing:-0.02em; line-height:1.05;
}}
.sb-logo-sub {{
  font-size:11px; letter-spacing:.16em;
  text-transform:uppercase;
  color:var(--c-accent-cyan); font-weight:600;
}}
.theme-toggle {{
  display:flex; gap:8px;
  margin:22px 8px 10px;
  padding:5px;
  border:1px solid var(--border);
  border-radius:999px;
  background:var(--bg);
}}
.theme-btn {{
  display:flex; align-items:center; justify-content:center;
  gap:7px; flex:1; padding:9px 0;
  border-radius:999px; border:0; cursor:pointer;
  font-size:13px; font-weight:600;
  font-family:var(--font-body);
  transition:all .18s;
  background:transparent; color:var(--fg-dim);
}}
.theme-btn.active-dark  {{ background:var(--bg-elevated); color:var(--c-accent-cyan); box-shadow:var(--glow-cyan); }}
.theme-btn.active-light {{ background:var(--c-accent-cyan); color:#130F0D; }}

.nav-section-hdr {{
  display:flex; align-items:center; gap:8px;
  padding:4px 10px 8px;
}}
.nav-part-num {{
  font-family:var(--font-display); font-weight:800;
  font-size:12px; opacity:.9;
}}
.nav-part-label {{
  font-size:10.5px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--fg-dim); font-weight:600;
}}
.nav-ch-btn {{
  display:flex; align-items:center; gap:12px;
  width:100%; text-align:left; cursor:pointer;
  padding:9px 10px; border-radius:12px;
  border:0; background:transparent; color:var(--fg-muted);
  transition:background .16s,color .16s;
  font-family:var(--font-body); font-size:13.5px; line-height:1.3;
}}
.nav-ch-btn:hover {{ background:var(--bg); color:var(--fg); }}
.nav-ch-btn.active {{ background:var(--bg); color:var(--fg); }}
.nav-ch-badge {{
  display:flex; align-items:center; justify-content:center;
  flex:0 0 auto; min-width:26px; height:24px;
  padding:0 6px; border-radius:7px;
  font-family:var(--font-display); font-weight:800; font-size:12px;
  border:1px solid currentColor;
  transition:background .16s,color .16s;
}}
.nav-ch-btn.active .nav-ch-badge {{ border:0; color:#130F0D; }}

/* ── main content ────────────────────────────────────────────────────── */
.content-area {{
  flex:1; min-width:0;
  height:100vh; overflow-y:auto;
}}
.content-inner {{
  max-width:1080px;
  margin:0 auto;
  padding:clamp(28px,5vw,76px) clamp(20px,5vw,72px) 120px;
  animation:ar-fade-up .42s cubic-bezier(.2,.8,.2,1);
}}

/* ── home view ───────────────────────────────────────────────────────── */
.home-eyebrow {{
  font-size:12px; letter-spacing:.2em;
  text-transform:uppercase; color:var(--c-accent-cyan);
  font-weight:600; margin-bottom:18px;
}}
.home-title {{
  font-family:var(--font-display); font-weight:800;
  font-size:clamp(40px,6vw,76px);
  line-height:1.02; letter-spacing:-0.03em;
  margin:0 0 20px; max-width:16ch;
}}
.home-sub {{
  font-size:clamp(17px,2vw,21px); line-height:1.6;
  color:var(--fg-muted); max-width:62ch; margin:0 0 36px;
}}
.hero-diagram {{
  border-radius:22px; overflow:hidden;
  border:1px solid var(--border);
  background:var(--bg-elevated);
  box-shadow:var(--glow-cyan);
  margin-bottom:40px;
}}
.stats-row {{
  display:flex; flex-wrap:wrap; gap:14px; margin-bottom:48px;
}}
.stat-card {{
  flex:1; min-width:150px;
  padding:22px 24px; border-radius:18px;
  background:var(--bg-elevated); border:1px solid var(--border);
}}
.stat-num {{
  font-family:var(--font-display); font-weight:800;
  font-size:40px; line-height:1;
}}
.stat-label {{
  font-size:13px; color:var(--fg-muted); margin-top:6px;
}}
.jump-label {{
  font-size:11px; letter-spacing:.18em;
  text-transform:uppercase; color:var(--fg-dim);
  font-weight:600; margin-bottom:18px;
}}
.parts-grid {{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  gap:16px;
}}
.part-card {{
  text-align:left; cursor:pointer;
  padding:24px; border-radius:18px;
  background:var(--bg-elevated); border:1px solid var(--border);
  color:var(--fg); width:100%;
  transition:border-color .2s,transform .2s;
  font-family:var(--font-body);
}}
.part-card:hover {{ transform:translateY(-3px); }}
.part-card-hdr {{ display:flex; align-items:baseline; gap:10px; margin-bottom:12px; }}
.part-card-num  {{ font-family:var(--font-display); font-weight:800; font-size:26px; }}
.part-card-range {{ font-size:12px; color:var(--fg-dim); }}
.part-card-title {{
  font-family:var(--font-display); font-weight:700;
  font-size:18px; letter-spacing:-0.01em; line-height:1.2;
}}
.part-card-blurb {{ font-size:13px; color:var(--fg-muted); margin-top:8px; line-height:1.45; }}

/* ── chapter view ────────────────────────────────────────────────────── */
.ch-part-label {{
  font-size:11.5px; letter-spacing:.18em;
  text-transform:uppercase; font-weight:600; margin-bottom:14px;
}}
.ch-title-row {{
  display:flex; align-items:flex-start;
  gap:clamp(16px,3vw,28px); margin-bottom:28px;
}}
.ch-big-num {{
  font-family:var(--font-display); font-weight:800;
  font-size:clamp(48px,9vw,104px);
  line-height:.85; letter-spacing:-0.04em;
  flex:0 0 auto;
}}
.ch-title {{
  font-family:var(--font-display); font-weight:800;
  font-size:clamp(28px,4.4vw,52px);
  line-height:1.04; letter-spacing:-0.025em;
  margin:0; padding-top:clamp(2px,1vw,12px);
}}
.ch-diagram {{
  border-radius:22px; overflow:hidden;
  border:1px solid var(--border);
  background:var(--bg-elevated); margin-bottom:34px;
}}
.ch-intro {{
  font-size:17px; line-height:1.65;
  color:var(--fg-muted); max-width:64ch; margin:0 0 36px;
}}
/* formulas box */
.formulas-box {{
  border:1.5px solid var(--c-accent-purple);
  box-shadow:var(--glow-purple);
  border-radius:20px;
  padding:28px clamp(20px,3vw,34px);
  margin-bottom:42px;
  background:var(--bg-elevated);
}}
.formulas-eyebrow {{
  font-size:11px; letter-spacing:.2em;
  text-transform:uppercase; color:var(--c-accent-purple);
  font-weight:700; margin-bottom:22px;
}}
.formulas-grid {{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(230px,1fr));
  gap:22px 28px;
}}
.formula-label {{
  font-size:11px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--fg-dim);
  font-weight:600; margin-bottom:10px;
}}
.formula-tex {{ font-size:19px; color:var(--fg); overflow-x:auto; }}
/* prose content (from markdown) */
.ch-prose {{
  border:1px solid var(--border);
  border-radius:18px; background:var(--bg-elevated);
  overflow:hidden; padding:clamp(20px,3vw,32px);
  margin-bottom:18px;
}}
.ch-prose h1,.ch-prose h2,.ch-prose h3,.ch-prose h4 {{
  font-family:var(--font-display);
  color:var(--fg); letter-spacing:-.01em; margin:1.5em 0 .5em;
}}
.ch-prose h1 {{ font-size:clamp(26px,3.5vw,40px); font-weight:800; margin-top:.5em; }}
.ch-prose h2 {{ font-size:clamp(20px,2.5vw,28px); font-weight:700;
  padding-bottom:8px; border-bottom:1px solid var(--border); }}
.ch-prose h3 {{ font-size:clamp(17px,2vw,22px); font-weight:600; }}
.ch-prose h4 {{ font-size:16px; font-weight:600; }}
.ch-prose p  {{ margin-bottom:14px; line-height:1.65; color:var(--fg-muted); }}
.ch-prose a  {{ color:var(--c-link); text-decoration:none; }}
.ch-prose a:hover {{ text-decoration:underline; }}
.ch-prose strong {{ font-weight:700; color:var(--fg); }}
.ch-prose em     {{ font-style:italic; }}
.ch-prose hr {{ border:none; border-top:1px solid var(--border); margin:32px 0; }}
.ch-prose ul,.ch-prose ol {{ margin:0 0 14px 22px; color:var(--fg-muted); }}
.ch-prose li {{ margin-bottom:5px; line-height:1.6; }}
.ch-prose code {{
  font-family:var(--font-mono); font-size:.855em;
  background:rgba(89,255,245,.07); color:var(--c-accent-cyan);
  padding:.15em .45em; border-radius:4px;
  border:1px solid rgba(89,255,245,.15);
}}
.ch-prose pre {{
  background:#0B0907; border-radius:10px;
  padding:18px 22px; overflow-x:auto; margin-bottom:18px;
  border:1px solid var(--border);
}}
.ch-prose pre code {{ background:none; border:none; padding:0; color:#c9d1d9; font-size:.875rem; }}
.ch-prose table {{
  width:100%; border-collapse:collapse; margin-bottom:20px;
  font-size:.9rem; border:1px solid var(--border); border-radius:10px; overflow:hidden;
}}
.ch-prose th {{
  background:rgba(243,243,240,.04); font-weight:700;
  text-align:left; padding:9px 14px;
  border-bottom:1px solid var(--border); color:var(--fg);
  font-size:11px; letter-spacing:.06em; text-transform:uppercase;
}}
.ch-prose th+th,.ch-prose td+td {{ border-left:1px solid var(--border); }}
.ch-prose td {{
  padding:9px 14px; border-bottom:1px solid var(--border);
  vertical-align:top; color:var(--fg-muted);
}}
.ch-prose tr:last-child td {{ border-bottom:none; }}
.ch-prose tr:nth-child(even) td {{ background:rgba(243,243,240,.02); }}
/* admonitions */
.ch-prose .admonition {{ border-radius:10px; padding:14px 18px; margin:18px 0; border-left:3px solid; }}
.ch-prose .admonition.note    {{ background:rgba(89,255,245,.07); border-color:var(--c-accent-cyan); }}
.ch-prose .admonition.warning,.ch-prose .admonition.caution {{ background:rgba(249,102,180,.07); border-color:var(--c-accent-pink); }}
.ch-prose .admonition-title   {{ font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; margin-bottom:6px; }}
.ch-prose .admonition.note .admonition-title {{ color:var(--c-accent-cyan); }}
.ch-prose .admonition.warning .admonition-title {{ color:var(--c-accent-pink); }}
.ch-prose .admonition p:last-child {{ margin-bottom:0; }}
/* mermaid in prose */
.ch-prose .mermaid {{
  display:flex; justify-content:center; margin:24px 0;
  background:rgba(243,243,240,.03); border-radius:10px;
  padding:18px; border:1px solid var(--border); overflow-x:auto;
}}
/* section placeholder cards */
.sections-list {{ display:flex; flex-direction:column; gap:18px; }}
.section-card {{
  border:1px solid var(--border); border-radius:18px;
  background:var(--bg-elevated); overflow:hidden;
}}
.section-card-hdr {{
  display:flex; align-items:center; gap:14px;
  padding:20px clamp(18px,2.5vw,26px) 14px;
}}
.section-badge {{
  display:flex; align-items:center; justify-content:center;
  flex:0 0 auto; min-width:40px; height:28px;
  padding:0 9px; border-radius:8px;
  font-family:var(--font-display); font-weight:800; font-size:13px;
  background:transparent; border:1px solid currentColor;
}}
.section-title {{
  font-family:var(--font-display); font-weight:700;
  font-size:clamp(18px,2.2vw,23px); letter-spacing:-0.01em;
}}
.section-placeholder {{
  font-size:15px; line-height:1.6; color:var(--fg-muted);
  margin:0 0 16px; border-left:2px solid var(--border-strong);
  padding-left:16px;
  padding:0 clamp(18px,2.5vw,26px) clamp(18px,2.5vw,26px);
}}
/* prev/next nav */
.ch-nav {{ display:flex; gap:14px; margin-top:48px; flex-wrap:wrap; }}
.ch-nav-btn {{
  flex:1; min-width:200px; cursor:pointer;
  padding:18px 22px; border-radius:16px;
  background:var(--bg-elevated); border:1px solid var(--border);
  color:var(--fg); transition:border-color .2s;
  font-family:var(--font-body);
}}
.ch-nav-btn:hover {{ border-color:var(--c-accent-cyan); }}
.ch-nav-label {{
  font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--fg-dim); margin-bottom:6px;
}}
.ch-nav-title {{
  font-family:var(--font-display); font-weight:600; font-size:15px;
}}
.ch-nav-btn.next {{ text-align:right; }}

/* ── icon btn ────────────────────────────────────────────────────────── */
.icon-btn {{
  display:flex; align-items:center; justify-content:center;
  width:42px; height:42px; border-radius:12px;
  border:1px solid var(--border); background:transparent;
  color:var(--fg); cursor:pointer;
}}

/* ── responsive ──────────────────────────────────────────────────────── */
@media(max-width:920px) {{
  .topbar {{ display:flex; }}
  .sidebar {{
    position:fixed; top:0; left:0; bottom:0;
    height:100vh; box-shadow:0 0 60px rgba(0,0,0,.5);
  }}
  .sidebar.closed {{ transform:translateX(-110%); }}
  .backdrop.open  {{ display:block; }}
  .content-area   {{ height:calc(100vh - 57px); }}
}}
</style>
</head>
<body>
<div id="app" :class="['theme-'+theme]">

  <!-- mobile topbar -->
  <header class="topbar" :style="{{display: mobile ? 'flex' : 'none'}}">
    <button class="icon-btn" @click="navOpen=!navOpen" aria-label="Menu">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
      </svg>
    </button>
    <span class="topbar-title">RAE Study Notes</span>
  </header>

  <!-- backdrop -->
  <div class="backdrop" :class="{{open: mobile && navOpen}}" @click="navOpen=false"></div>

  <div class="shell">
    <!-- sidebar -->
    <aside class="sidebar ar-scroll" :class="{{closed: mobile && !navOpen}}">
      <button class="sb-logo" @click="goHome">
        <span class="sb-logo-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#59FFF5" stroke-width="1.8" stroke-linecap="round">
            <circle cx="12" cy="12" r="2.4"/>
            <path d="M6.3 6.3a8 8 0 0 0 0 11.4M17.7 6.3a8 8 0 0 1 0 11.4M3.5 3.5a12 12 0 0 0 0 17M20.5 3.5a12 12 0 0 1 0 17"/>
          </svg>
        </span>
        <span style="display:flex;flex-direction:column;gap:2px;padding-top:1px;">
          <span class="sb-logo-name">Amateur Radio</span>
          <span class="sb-logo-sub">RAE &middot; Study Notes</span>
        </span>
      </button>

      <div class="theme-toggle">
        <button class="theme-btn" :class="{{['active-dark']: theme==='dark'}}" @click="setTheme('dark')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/></svg>
          Dark
        </button>
        <button class="theme-btn" :class="{{['active-light']: theme==='light'}}" @click="setTheme('light')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
          Light
        </button>
      </div>

      <nav style="margin-top:14px;display:flex;flex-direction:column;gap:18px;">
        <div v-for="(part,pi) in navParts" :key="pi" style="display:flex;flex-direction:column;gap:3px;">
          <div class="nav-section-hdr">
            <span class="nav-part-num" :style="{{color: part.color}}">{{{{ part.roman }}}}</span>
            <span class="nav-part-label">{{{{ part.label }}}}</span>
          </div>
          <button v-for="ch in part.chapters" :key="ch.idx"
            class="nav-ch-btn"
            :class="{{active: view===ch.idx}}"
            :style="{{boxShadow: view===ch.idx ? 'inset 3px 0 0 '+part.color : 'none'}}"
            @click="select(ch.idx)">
            <span class="nav-ch-badge"
              :style="{{background: view===ch.idx ? part.color : 'transparent', color: view===ch.idx ? '#130F0D' : part.color}}">
              {{{{ch.n}}}}
            </span>
            <span>{{{{ch.t}}}}</span>
          </button>
        </div>
      </nav>
    </aside>

    <!-- main -->
    <main class="content-area ar-scroll" ref="contentEl">
      <div class="content-inner" :key="view">

        <!-- HOME -->
        <template v-if="view==='home'">
          <div class="home-eyebrow">South African Radio League &middot; RAE</div>
          <h1 class="home-title">Introduction to Amateur&nbsp;Radio</h1>
          <p class="home-sub">Your complete study companion for the Radio Amateur Examination — every chapter, the theory, the formulas, and your own notes, all in one place.</p>

          <div class="hero-diagram">
            <svg viewBox="0 0 900 170" width="100%" height="170" preserveAspectRatio="none" style="display:block;">
              <g v-html="gridSvg(900,170)"></g>
              <line x1="0" y1="85" x2="900" y2="85" stroke="var(--fg-dim)" stroke-width="1" opacity=".6"/>
              <path :d="sinePath(900,170,3,52)" fill="none" stroke="var(--c-accent-cyan)" stroke-width="3.5" :style="{{filter:'drop-shadow(0 0 7px var(--c-accent-cyan))'}}" />
            </svg>
          </div>

          <div class="stats-row">
            <div class="stat-card">
              <div class="stat-num" style="color:var(--c-accent-cyan)">{{{{ stats.total }}}}</div>
              <div class="stat-label">Chapters</div>
            </div>
            <div class="stat-card">
              <div class="stat-num" style="color:var(--c-accent-purple)">6</div>
              <div class="stat-label">Study parts</div>
            </div>
            <div class="stat-card">
              <div class="stat-num" style="color:var(--c-accent-pink)">{{{{stats.done}}}}</div>
              <div class="stat-label">Done</div>
            </div>
            <div class="stat-card">
              <div class="stat-num" style="color:var(--c-accent-sky)">&Sigma;</div>
              <div class="stat-label">{{{{stats.glossary}}}} glossary terms</div>
            </div>
          </div>

          <div class="jump-label">Jump in</div>
          <div class="parts-grid">
            <button v-for="(part,pi) in navParts" :key="pi" class="part-card"
              :style="{{borderColor: 'var(--border)'}}"
              @mouseenter="e=>e.currentTarget.style.borderColor=part.color"
              @mouseleave="e=>e.currentTarget.style.borderColor='var(--border)'"
              @click="select(part.firstIdx)">
              <div class="part-card-hdr">
                <span class="part-card-num" :style="{{color:part.color}}">{{{{part.roman}}}}</span>
                <span class="part-card-range">{{{{part.range}}}}</span>
              </div>
              <div class="part-card-title">{{{{part.label}}}}</div>
              <div class="part-card-blurb">{{{{part.blurb}}}}</div>
            </button>
          </div>
        </template>

        <!-- CHAPTER -->
        <article v-else-if="currentCh">
          <div class="ch-part-label" :style="{{color: currentPart.color}}">{{{{currentPart.label}}}}</div>
          <div class="ch-title-row">
            <span class="ch-big-num" :style="{{color: currentPart.color}}">{{{{currentCh.n}}}}</span>
            <h1 class="ch-title">{{{{currentCh.t}}}}</h1>
          </div>

          <!-- animated diagram -->
          <div class="ch-diagram" v-html="chDiagram"></div>

          <!-- intro blurb -->
          <p class="ch-intro" v-if="chIntro">{{{{chIntro}}}}</p>

          <!-- formulas -->
          <div class="formulas-box" v-if="chFormulas.length">
            <div class="formulas-eyebrow">Key Formulas</div>
            <div class="formulas-grid">
              <div v-for="f in chFormulas" :key="f.label">
                <div class="formula-label">{{{{f.label}}}}</div>
                <div class="formula-tex" :data-tex="f.tex"></div>
              </div>
            </div>
          </div>

          <!-- real markdown content -->
          <div v-if="currentCh.html" class="ch-prose" v-html="currentCh.html"></div>

          <!-- placeholder section cards when no real content yet -->
          <div v-else class="sections-list">
            <section v-for="(s,si) in currentCh.s" :key="si" class="section-card">
              <div class="section-card-hdr">
                <span class="section-badge" :style="{{color: currentPart.color}}">
                  {{{{sectionNum(s)}}}}
                </span>
                <h3 class="section-title">{{{{sectionTitle(s)}}}}</h3>
              </div>
              <p class="section-placeholder">
                Notes for <strong :style="{{color:'var(--fg)'}}">{{{{sectionTitle(s)}}}}</strong> will appear here once this chapter is summarised.
              </p>
            </section>
          </div>

          <!-- prev / next -->
          <div class="ch-nav">
            <button v-if="prevCh !== null" class="ch-nav-btn" @click="select(prevCh)">
              <div class="ch-nav-label">&larr; Previous</div>
              <div class="ch-nav-title">{{{{ chapters[prevCh].n }}}}. {{{{ chapters[prevCh].t }}}}</div>
            </button>
            <button v-if="nextCh !== null" class="ch-nav-btn next" @click="select(nextCh)">
              <div class="ch-nav-label">Next &rarr;</div>
              <div class="ch-nav-title">{{{{ chapters[nextCh].n }}}}. {{{{ chapters[nextCh].t }}}}</div>
            </button>
          </div>
        </article>

      </div>
    </main>
  </div>
</div>

<script>
window.__DATA__ = {data_json};

const ROMAN = ['I','II','III','IV','V','VI'];

const ACCENTS = [
  'var(--c-accent-purple)','var(--c-accent-cyan)','var(--c-accent-sky)',
  'var(--c-accent-blue)','var(--c-accent-pink)','var(--c-accent-indigo)'
];

const INTROS = {{
  '1':'Amateur radio is a licensed hobby with dozens of facets — from casual chats to emergency communications, satellite work and contesting. This chapter sets the scene and covers the South African licensing landscape.',
  '3':'Everything in radio rests on a handful of electrical ideas: charge, current, voltage and power. Get these foundations solid before moving on.',
  '4':"Ohm\u2019s Law is the single most important relationship in electronics. Three quantities \u2014 voltage, current and resistance \u2014 locked together in one tidy equation.",
  '6':'Real circuits combine resistors in series and parallel and split voltages between them. Kirchhoff\u2019s laws let you analyse any DC network.',
  '7':'Power is the rate at which energy is converted. Combine the power formula with Ohm\u2019s Law and you can find dissipation, source matching and efficiency.',
  '8':'Alternating current is the lifeblood of radio. The sine wave, its period, frequency, wavelength and RMS value are the vocabulary of every signal you will meet.',
  '9':'A capacitor stores energy in an electric field and opposes changes in voltage. In AC circuits it presents a frequency-dependent reactance.',
  '10':'An inductor stores energy in a magnetic field and opposes changes in current. Its reactance rises with frequency \u2014 the mirror image of the capacitor.',
  '11':'Combine inductance and capacitance and you get resonance \u2014 the basis of every tuned circuit, filter and oscillator in radio.',
  '12':'The decibel turns awkward ratios into addable numbers. Master it and gain, loss and signal levels become simple arithmetic.',
  '13':'Filters shape the frequency content of a signal \u2014 passing what you want and rejecting the rest. Lowpass, highpass, bandpass and bandstop all start from R, L and C.',
  '14':'The transformer couples energy between circuits by a shared magnetic field, transforming voltage, current and impedance by its turns ratio.',
  '26':'The antenna is where electrical signals become radio waves. This long chapter covers dipoles, verticals, Yagis, gain, SWR and feedlines.',
  '27':'A signal that leaves your antenna has to get somewhere. Propagation explains how radio waves travel \u2014 by ground, sky and everything in between.',
}};

const FORMULAS = {{
  '3':[{{label:'Charge',tex:'Q = I\\,t'}},{{label:'Power',tex:'P = V\\,I'}}],
  '4':[{{label:"Ohm's Law",tex:'V = I\\,R'}},{{label:'Current',tex:'I = \\\\dfrac{{V}}{{R}}'}},{{label:'Resistance',tex:'R = \\\\dfrac{{V}}{{I}}'}}],
  '6':[{{label:'Resistors in series',tex:'R_s = R_1 + R_2 + \\\\cdots'}},{{label:'Resistors in parallel',tex:'\\\\dfrac{{1}}{{R_p}} = \\\\dfrac{{1}}{{R_1}}+\\\\dfrac{{1}}{{R_2}}+\\\\cdots'}},{{label:'Voltage divider',tex:'V_{{out}} = V_{{in}}\\,\\\\dfrac{{R_2}}{{R_1+R_2}}'}}],
  '7':[{{label:'Power',tex:'P = VI = I^2 R = \\\\dfrac{{V^2}}{{R}}'}},{{label:'Efficiency',tex:'\\\\eta = \\\\dfrac{{P_{{out}}}}{{P_{{in}}}}\\\\times 100\\\\%'}}],
  '8':[{{label:'Sine signal',tex:'v(t) = V_p\\\\sin(2\\\\pi f t)'}},{{label:'Period',tex:'T = \\\\dfrac{{1}}{{f}}'}},{{label:'Wavelength',tex:'\\\\lambda = \\\\dfrac{{c}}{{f}}'}},{{label:'RMS voltage',tex:'V_{{rms}} = \\\\dfrac{{V_p}}{{\\\\sqrt{{2}}}}'}}],
  '9':[{{label:'Capacitive reactance',tex:'X_C = \\\\dfrac{{1}}{{2\\\\pi f C}}'}},{{label:'Capacitors in series',tex:'\\\\dfrac{{1}}{{C_s}}=\\\\dfrac{{1}}{{C_1}}+\\\\dfrac{{1}}{{C_2}}'}}],
  '10':[{{label:'Inductive reactance',tex:'X_L = 2\\\\pi f L'}},{{label:'Inductors in series',tex:'L_s=L_1+L_2+\\\\cdots'}}],
  '11':[{{label:'Resonant frequency',tex:'f_0 = \\\\dfrac{{1}}{{2\\\\pi\\\\sqrt{{LC}}}}'}},{{label:'Quality factor',tex:'Q = \\\\dfrac{{X_L}}{{R}}'}}],
  '12':[{{label:'Power ratio',tex:'\\\\text{{dB}} = 10\\\\log_{{10}}\\\\dfrac{{P_2}}{{P_1}}'}},{{label:'Voltage ratio',tex:'\\\\text{{dB}} = 20\\\\log_{{10}}\\\\dfrac{{V_2}}{{V_1}}'}}],
  '13':[{{label:'RC cutoff',tex:'f_c = \\\\dfrac{{1}}{{2\\\\pi RC}}'}}],
  '14':[{{label:'Voltage ratio',tex:'\\\\dfrac{{V_s}}{{V_p}} = \\\\dfrac{{N_s}}{{N_p}}'}},{{label:'Impedance ratio',tex:'\\\\dfrac{{Z_p}}{{Z_s}} = \\\\left(\\\\dfrac{{N_p}}{{N_s}}\\\\right)^2'}}],
  '26':[{{label:'Half-wave dipole',tex:'\\\\ell \\\\approx \\\\dfrac{{143}}{{f_{{\\\\text{{MHz}}}}}}\\,\\\\text{{m}}'}},{{label:'SWR',tex:'\\\\text{{SWR}} = \\\\dfrac{{1+|\\\\Gamma|}}{{1-|\\\\Gamma|}}'}}],
  '27':[{{label:'Free-space path loss',tex:'L_{{fs}}=20\\\\log_{{10}}\\!\\\\left(\\\\dfrac{{4\\\\pi d}}{{\\\\lambda}}\\\\right)'}}],
}};

const DIAGRAMS = {{
  '3':'electron','4':'ohm','6':'electron','8':'sine',
  '9':'cap','10':'cap','11':'resonance','12':'sine',
  '13':'filter','14':'transformer','26':'antenna','27':'antenna'
}};

const {{ createApp }} = Vue;

createApp({{
  data() {{
    const saved_view  = this.tryLS('ar-view')  || 'home';
    const saved_theme = this.tryLS('ar-theme') || 'dark';
    const d = window.__DATA__;
    return {{
      view: saved_view === 'home' ? 'home' : (parseInt(saved_view) || 'home'),
      theme: saved_theme,
      navOpen: false,
      mobile: window.innerWidth < 920,
      parts: d.parts,
      chapters: d.chapters,
      stats: d.stats,
    }};
  }},
  computed: {{
    navParts() {{
      return this.parts.map((p, pi) => {{
        const chs = this.chapters
          .map((c, ci) => ({{ ...c, idx: ci }}))
          .filter(c => c.p === pi);
        const nums = chs.map(c => c.n);
        return {{
          ...p,
          roman: ROMAN[pi],
          range: nums.length ? 'Ch ' + nums[0] + '\u2013' + nums[nums.length - 1] : '',
          blurb: p.blurb,
          chapters: chs,
          firstIdx: this.chapters.findIndex(c => c.p === pi),
        }};
      }});
    }},
    currentCh()   {{ return this.view === 'home' ? null : this.chapters[this.view]; }},
    currentPart() {{ return this.currentCh ? this.parts[this.currentCh.p] : null; }},
    chIntro()     {{ return this.currentCh ? (INTROS[this.currentCh.n] || null) : null; }},
    chFormulas()  {{ return this.currentCh ? (FORMULAS[this.currentCh.n] || []) : []; }},
    chDiagram()   {{
      if (!this.currentCh) return this.buildDiagram('sine', 'var(--c-accent-cyan)');
      const kind   = DIAGRAMS[this.currentCh.n] || 'sine';
      const accent = this.currentPart ? this.currentPart.color : 'var(--c-accent-cyan)';
      return this.buildDiagram(kind, accent);
    }},
    prevCh() {{
      if (this.view === 'home') return null;
      return this.view > 0 ? this.view - 1 : null;
    }},
    nextCh() {{
      if (this.view === 'home') return null;
      return this.view < this.chapters.length - 1 ? this.view + 1 : null;
    }},
  }},
  watch: {{
    view(v) {{
      try {{ localStorage.setItem('ar-view', String(v)); }} catch(e) {{}}
      this.$nextTick(() => {{
        const el = this.$refs.contentEl;
        if (el) el.scrollTop = 0;
        this.renderMath();
        this.renderMermaid();
      }});
    }},
    theme() {{
      this.$nextTick(() => this.renderMermaid());
    }},
  }},
  mounted() {{
    window.addEventListener('resize', this.onResize);
    this.$nextTick(() => {{ this.renderMath(); this.renderMermaid(); }});
    mermaid.initialize({{ startOnLoad: false, theme: this.theme === 'dark' ? 'dark' : 'default', fontFamily: 'Inter' }});
  }},
  beforeUnmount() {{
    window.removeEventListener('resize', this.onResize);
  }},
  methods: {{
    tryLS(k) {{ try {{ return localStorage.getItem(k); }} catch(e) {{ return null; }} }},
    onResize() {{ this.mobile = window.innerWidth < 920; }},
    goHome()   {{ this.view = 'home'; this.navOpen = false; }},
    select(i)  {{ this.view = i;      this.navOpen = false; }},
    setTheme(t) {{
      this.theme = t;
      mermaid.initialize({{ startOnLoad: false, theme: t === 'dark' ? 'dark' : 'default', fontFamily: 'Inter' }});
      try {{ localStorage.setItem('ar-theme', t); }} catch(e) {{}}
    }},
    sectionNum(s)   {{ const m = s.match(/^([0-9][0-9A-Za-z.]*)\\s/); return m ? m[1] : '\u00b7'; }},
    sectionTitle(s) {{ const m = s.match(/^([0-9][0-9A-Za-z.]*)\\s+(.*)/); return m ? m[2] : s; }},
    renderMath() {{
      if (!window.katex) {{
        this._ktTries = (this._ktTries || 0) + 1;
        if (this._ktTries < 30) {{ clearTimeout(this._kt); this._kt = setTimeout(() => this.renderMath(), 200); }}
        return;
      }}
      document.querySelectorAll('[data-tex]').forEach(el => {{
        const tex = el.getAttribute('data-tex');
        if (!tex || el.getAttribute('data-rendered') === tex) return;
        try {{ katex.render(tex, el, {{ displayMode: true, throwOnError: false }}); el.setAttribute('data-rendered', tex); }} catch(e) {{}}
      }});
    }},
    renderMermaid() {{
      this.$nextTick(async () => {{
        const els = document.querySelectorAll('.mermaid:not([data-rendered])');
        if (!els.length) return;
        try {{
          await mermaid.run({{ nodes: Array.from(els) }});
          els.forEach(el => el.setAttribute('data-rendered','1'));
        }} catch(e) {{}}
      }});
    }},
    sinePath(W, H, periods, amp) {{
      const mid = H / 2; let d = '';
      for (let x = 0; x <= W; x += 4) {{
        const y = mid - amp * Math.sin((x / W) * periods * 2 * Math.PI);
        d += (x === 0 ? 'M' : 'L') + x + ' ' + y.toFixed(1);
      }}
      return d;
    }},
    gridSvg(W, H) {{
      let s = '';
      for (let x = 0; x <= W; x += W/12)
        s += `<line x1="${{x}}" y1="0" x2="${{x}}" y2="${{H}}" stroke="var(--border)" stroke-width="1"/>`;
      for (let y = 0; y <= H; y += H/4)
        s += `<line x1="0" y1="${{y}}" x2="${{W}}" y2="${{y}}" stroke="var(--border)" stroke-width="1"/>`;
      return s;
    }},
    buildDiagram(kind, accent) {{
      const W = 900, H = 170;
      const grid = this.gridSvg(W, H);
      const wrap = inner => `<svg viewBox="0 0 ${{W}} ${{H}}" width="100%" height="${{H}}" preserveAspectRatio="none" style="display:block;">${{inner}}</svg>`;
      if (kind === 'sine') {{
        const d = this.sinePath(W, H, 3, 52);
        return wrap(`${{grid}}<line x1="0" y1="${{H/2}}" x2="${{W}}" y2="${{H/2}}" stroke="var(--fg-dim)" stroke-width="1" opacity=".6"/>
          <path d="${{d}}" fill="none" stroke="${{accent}}" stroke-width="3.5" style="filter:drop-shadow(0 0 7px ${{accent}})" />
          <circle r="7" fill="${{accent}}" style="filter:drop-shadow(0 0 6px ${{accent}})"><animateMotion dur="6s" repeatCount="indefinite" path="${{d}}" calcMode="linear"/></circle>`);
      }}
      if (kind === 'antenna') {{
        const cx = W/2, cy = H/2;
        const rings = [0,1,2,3].map(i =>
          `<circle cx="${{cx}}" cy="${{cy}}" r="30" fill="none" stroke="${{accent}}" stroke-width="2" class="ar-ripple" style="transform-origin:${{cx}}px ${{cy}}px;animation:ar-ripple 3.6s ease-out ${{i*0.9}}s infinite"/>`
        ).join('');
        return wrap(`${{rings}}<line x1="${{cx}}" y1="${{cy-46}}" x2="${{cx}}" y2="${{cy+46}}" stroke="var(--fg)" stroke-width="4" stroke-linecap="round"/>
          <circle cx="${{cx}}" cy="${{cy}}" r="5" fill="${{accent}}" style="filter:drop-shadow(0 0 6px ${{accent}})"/>`);
      }}
      if (kind === 'resonance') {{
        let d = ''; const x0=70,x1=W-50,yTop=36,yBot=H-34,f0=0.5;
        for(let i=0;i<=120;i++){{ const t=i/120,x=x0+(x1-x0)*t,g=1/(1+Math.pow((t-f0)*14,2)),y=yBot-(yBot-yTop)*g; d+=(i===0?'M':'L')+x.toFixed(1)+' '+y.toFixed(1); }}
        const cx=x0+(x1-x0)*f0;
        return wrap(`${{grid}}<line x1="${{x0}}" y1="${{yBot}}" x2="${{x1}}" y2="${{yBot}}" stroke="var(--fg-dim)" stroke-width="1.5" opacity=".6"/>
          <line x1="${{cx}}" y1="${{yTop-2}}" x2="${{cx}}" y2="${{yBot}}" stroke="var(--c-accent-pink)" stroke-width="1.5" stroke-dasharray="5 6" opacity=".8"/>
          <text x="${{cx+8}}" y="${{yTop+10}}" fill="var(--c-accent-pink)" font-size="15" font-family="var(--font-mono)">f\u2080</text>
          <path d="${{d}}" fill="none" stroke="${{accent}}" stroke-width="3.5" style="filter:drop-shadow(0 0 6px ${{accent}})"/>`);
      }}
      if (kind === 'electron') {{
        const y=H/2, x1=130, x2=W-130;
        const dots = [0,1,2,3,4,5,6].map(i =>
          `<circle r="6" fill="${{accent}}" style="filter:drop-shadow(0 0 5px ${{accent}})"><animateMotion dur="3.4s" begin="${{i*0.48}}s" repeatCount="indefinite" path="M${{x1}} ${{y}} L${{x2}} ${{y}}" calcMode="linear"/></circle>`
        ).join('');
        return wrap(`<line x1="${{x1}}" y1="${{y}}" x2="${{x2}}" y2="${{y}}" stroke="var(--fg-dim)" stroke-width="3" opacity=".5"/>
          <rect x="40" y="${{y-42}}" width="78" height="84" rx="12" fill="none" stroke="${{accent}}" stroke-width="2"/>
          <text x="79" y="${{y+7}}" text-anchor="middle" fill="${{accent}}" font-size="30" font-family="var(--font-display)" font-weight="800">\u2212</text>
          <rect x="${{W-118}}" y="${{y-42}}" width="78" height="84" rx="12" fill="none" stroke="var(--c-accent-pink)" stroke-width="2"/>
          <text x="${{W-79}}" y="${{y+9}}" text-anchor="middle" fill="var(--c-accent-pink)" font-size="28" font-family="var(--font-display)" font-weight="800">+</text>
          ${{dots}}`);
      }}
      if (kind === 'cap') {{
        let d=''; const x0=80,x1=W-60,y0=H-34,y1=34;
        for(let i=0;i<=80;i++){{ const t=i/80,x=x0+(x1-x0)*t,y=y0-(y0-y1)*(1-Math.exp(-3.2*t)); d+=(i===0?'M':'L')+x.toFixed(1)+' '+y.toFixed(1); }}
        const dl=1400;
        return wrap(`${{grid}}<line x1="${{x0}}" y1="${{y0}}" x2="${{x1}}" y2="${{y0}}" stroke="var(--fg-dim)" stroke-width="1.5" opacity=".6"/>
          <line x1="${{x0}}" y1="${{y0}}" x2="${{x0}}" y2="${{y1-6}}" stroke="var(--fg-dim)" stroke-width="1.5" opacity=".6"/>
          <line x1="${{x0}}" y1="${{y1}}" x2="${{x1}}" y2="${{y1}}" stroke="${{accent}}" stroke-width="1" stroke-dasharray="5 6" opacity=".5"/>
          <path d="${{d}}" fill="none" stroke="${{accent}}" stroke-width="3.5" stroke-dasharray="${{dl}}" style="--dl:${{dl}}px;animation:ar-dash 4s cubic-bezier(.2,.8,.2,1) infinite;filter:drop-shadow(0 0 6px ${{accent}})"/>`);
      }}
      if (kind === 'filter') {{
        let d=''; const x0=70,x1=W-50,yTop=40,yBot=H-36,fc=0.46;
        for(let i=0;i<=100;i++){{ const t=i/100,x=x0+(x1-x0)*t,g=t<fc?1:1/Math.sqrt(1+Math.pow((t-fc)/(1-fc)*5,2)),y=yBot-(yBot-yTop)*g; d+=(i===0?'M':'L')+x.toFixed(1)+' '+y.toFixed(1); }}
        const cx=x0+(x1-x0)*fc;
        return wrap(`${{grid}}<line x1="${{x0}}" y1="${{yBot}}" x2="${{x1}}" y2="${{yBot}}" stroke="var(--fg-dim)" stroke-width="1.5" opacity=".6"/>
          <line x1="${{cx}}" y1="${{yTop-4}}" x2="${{cx}}" y2="${{yBot}}" stroke="var(--c-accent-pink)" stroke-width="1.5" stroke-dasharray="5 6" opacity=".8"/>
          <text x="${{cx+8}}" y="${{yTop+8}}" fill="var(--c-accent-pink)" font-size="15" font-family="var(--font-mono)">fc</text>
          <path d="${{d}}" fill="none" stroke="${{accent}}" stroke-width="3.5" style="filter:drop-shadow(0 0 6px ${{accent}})"/>
          <circle r="6" fill="${{accent}}" style="filter:drop-shadow(0 0 6px ${{accent}})"><animateMotion dur="5s" repeatCount="indefinite" path="${{d}}" calcMode="linear"/></circle>`);
      }}
      if (kind === 'ohm') {{
        const cx=W/2,cy=H/2;
        const loop=`M200 ${{cy-46}} L${{W-200}} ${{cy-46}} L${{W-200}} ${{cy+46}} L200 ${{cy+46}} Z`;
        const dots=[0,1,2,3,4].map(i=>`<circle r="5.5" fill="${{accent}}" style="filter:drop-shadow(0 0 5px ${{accent}})"><animateMotion dur="4s" begin="${{i*0.8}}s" repeatCount="indefinite" path="${{loop}}" calcMode="linear"/></circle>`).join('');
        return wrap(`<rect x="200" y="${{cy-46}}" width="${{W-400}}" height="92" rx="8" fill="none" stroke="var(--fg-dim)" stroke-width="2.5" opacity=".5"/>
          <rect x="184" y="${{cy-26}}" width="32" height="52" rx="6" fill="var(--bg-elevated)" stroke="var(--c-accent-pink)" stroke-width="2.5"/>
          <text x="200" y="${{cy+6}}" text-anchor="middle" fill="var(--c-accent-pink)" font-size="20" font-family="var(--font-display)" font-weight="800">V</text>
          <rect x="${{cx-46}}" y="${{cy-58}}" width="92" height="24" rx="5" fill="var(--bg-elevated)" stroke="${{accent}}" stroke-width="2.5"/>
          <text x="${{cx}}" y="${{cy-40}}" text-anchor="middle" fill="${{accent}}" font-size="16" font-family="var(--font-display)" font-weight="800">R</text>
          ${{dots}}`);
      }}
      if (kind === 'transformer') {{
        const cy=H/2;
        const coil=(x,col)=>[0,1,2,3].map(i=>`<path d="M${{x}} ${{cy-44+i*22}} a 11 11 0 1 1 0 22" fill="none" stroke="${{col}}" stroke-width="3"/>`).join('');
        return wrap(`${{coil(330,accent)}}${{coil(W-330,'var(--c-accent-pink)')}}
          <line x1="${{W/2-12}}" y1="${{cy-58}}" x2="${{W/2-12}}" y2="${{cy+58}}" stroke="var(--fg-dim)" stroke-width="3" opacity=".6"/>
          <line x1="${{W/2+12}}" y1="${{cy-58}}" x2="${{W/2+12}}" y2="${{cy+58}}" stroke="var(--fg-dim)" stroke-width="3" opacity=".6"/>
          <text x="330" y="${{cy+86}}" text-anchor="middle" fill="${{accent}}" font-size="16" font-family="var(--font-mono)">Np</text>
          <text x="${{W-330}}" y="${{cy+86}}" text-anchor="middle" fill="var(--c-accent-pink)" font-size="16" font-family="var(--font-mono)">Ns</text>
          <circle r="5" fill="${{accent}}" opacity=".9"><animateMotion dur="2.4s" repeatCount="indefinite" path="M${{W/2-12}} ${{cy-58}} L${{W/2-12}} ${{cy+58}}" calcMode="linear"/></circle>`);
      }}
      // fallback — sine
      const d = this.sinePath(W, H, 3, 52);
      return wrap(`${{grid}}<path d="${{d}}" fill="none" stroke="${{accent}}" stroke-width="3.5" style="filter:drop-shadow(0 0 7px ${{accent}})"/>`);
    }},
  }},
}}).mount('#app');
</script>
</body>
</html>"""


if __name__ == "__main__":
    build()
