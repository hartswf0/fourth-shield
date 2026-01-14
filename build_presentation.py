#!/usr/bin/env python3
"""
Generate OPTIMIZED presentation.html:
- Single Active WebGL Context (Prevents crushing browser memory)
- Click-to-Load Studio for each scene
- Auto-copies MPD on load
- FIXED: Iframe height issue to use VH (Fill Window)
- NEW: State-Persistent CSS Grid Layout (Seamless Hot-Swap)
- FIXED: Hardened JS (Debounce, GC, Clipboard Safety)

Run: python3 build_presentation.py
"""

import os
import json
from pathlib import Path

LEGOS_DIR = Path("dist/legos")
OUTPUT = Path("dist/presentation.html")

scenes = [
    {"id": "01", "title": "Production Pipeline & Triage Strategy", "desc": "Master overview: Brainstorming (Chaos) → Execution (Order)", "file": "scene_01_pipeline.legos"},
    {"id": "02", "title": "Humanist Ontology Template", "desc": "Code-compliant schema for Iliad 18 zones", "file": "scene_02_ontology.legos"},
    {"id": "03", "title": "Techs Asset Loop", "desc": "Scrape → Train → Test cycle for Bronze LoRA", "file": "scene_03_techs_loop.legos"},
    {"id": "04", "title": "Designers Stagecraft Volume", "desc": "Unreal Engine block-out: Rings, Dome, Forge, Camera", "file": "scene_04_designers.legos"},
    {"id": "05", "title": "The Auden Button", "desc": "P3 toggle: Homeric Simulation ↔ Modernist Critique", "file": "scene_05_auden_button.legos"},
    {"id": "06", "title": "Humanists: Essays to Data", "desc": "Transform prose → structured JSON schema", "file": "scene_06_humanists.legos"},
    {"id": "07", "title": "Techs Material Pipeline", "desc": "PBR focus: Roughness & Metallic maps", "file": "scene_07_techs_pipeline.legos"},
    {"id": "08", "title": "Stagecraft Mandate", "desc": "Build volume only, lock camera, get sign-off", "file": "scene_08_mandate.legos"},
    {"id": "09", "title": "Monday Morning Plan", "desc": "Triage execution: Classicist, Dev, Director actions", "file": "scene_09_monday.legos"},
]

def load_scene(filename):
    path = LEGOS_DIR / filename
    if not path.exists():
        return "", ""
    content = path.read_text()
    parts = content.split("\n---\n", 1)
    yaml = parts[0] if len(parts) > 0 else ""
    mpd = parts[1] if len(parts) > 1 else ""
    return yaml, mpd

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main():
    scene_data = []
    for s in scenes:
        yaml, mpd = load_scene(s["file"])
        scene_data.append({
            "id": s["id"],
            "title": s["title"],
            "desc": s["desc"],
            "yaml": yaml,
            "mpd": mpd,
            "image": f"pages/{s['id'].zfill(4)}.png"
        })
    
    html_header = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Shield of Achilles — Studio</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600&family=Cinzel:wght@600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050505;
            --panel: #0a0a0a;
            --border: #333;
            --gold: #c9a227;
            --text: #e0e0e0;
            --text-dim: #666;
            --active-bg: #1a1a1a;
            --code-bg: #000;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); line-height: 1.4; font-size: 13px; }

        /* HEADER */
        .header {
            background: var(--bg); border-bottom: 1px solid var(--border); height: 48px;
            display: flex; align-items: center; justify-content: space-between; padding: 0 1rem;
            position: sticky; top: 0; z-index: 500;
        }
        .logo { font-family: 'Cinzel', serif; color: var(--gold); font-size: 0.9rem; letter-spacing: 0.05em; }
        .mode-toggle { display: flex; background: var(--panel); border: 1px solid var(--border); border-radius: 4px; padding: 2px; }
        .mode-btn {
            padding: 4px 10px; background: transparent; border: none; color: var(--text-dim);
            font-size: 10px; font-weight: 600; font-family: 'JetBrains Mono', monospace; cursor: pointer; text-transform: uppercase;
        }
        .mode-btn.active { background: var(--gold); color: #000; border-radius: 2px; }

        /* NAV */
        .nav-scroller {
            background: var(--bg); border-bottom: 1px solid var(--border); padding: 8px 1rem;
            display: flex; gap: 6px; overflow-x: auto; position: sticky; top: 48px; z-index: 400; scrollbar-width: none;
        }
        .nav-scroller::-webkit-scrollbar { display: none; }
        .nav-pill {
            flex: 0 0 auto; padding: 4px 8px; background: var(--panel); border: 1px solid var(--border);
            color: var(--text-dim); border-radius: 3px; font-size: 10px; font-family: 'JetBrains Mono', monospace; cursor: pointer;
        }
        .nav-pill.active { border-color: var(--gold); color: var(--gold); }

        /* SCENES */
        .container { max-width: 1600px; margin: 0 auto; padding: 1rem; }
        .scene-card { border: 1px solid var(--border); background: var(--panel); margin-bottom: 2rem; display: flex; flex-direction: column; }
        .scene-header {
            padding: 8px 12px; border-bottom: 1px solid var(--border); display: flex; align-items: baseline; gap: 8px; background: #080808;
        }
        .scene-id { color: var(--gold); font-family: 'JetBrains Mono'; font-weight: 700; font-size: 11px; }
        .scene-title { font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }

        /* VIEWPORT GRID */
        .viewport { 
            display: grid; 
            min-height: 500px; 
            background: #000;
            overflow: hidden;
            
            /* Default: Single column mobile stack */
            grid-template-columns: 1fr;
            grid-template-rows: 1fr 1fr;
            grid-template-areas: 
                "top"
                "bottom";
        }
        @media (min-width: 768px) {
            .viewport { 
                /* Calc height to fill screen minus header/nav/margins */
                height: calc(100vh - 140px); 
                max-height: 1200px; 
                min-height: 600px;
                
                grid-template-columns: 1fr 1fr;
                grid-template-rows: 1fr;
                grid-template-areas: "left right";
            }
        }

        /* GRID ITEMS (Persistent) */
        .slot { display: none; flex-direction: column; height: 100%; border: 1px solid var(--border); overflow: hidden; }
        
        .slot-pres { border-right: none; }
        .slot-studio { background: #000; }
        .slot-yaml { background: var(--code-bg); border-left: 1px solid var(--border); }
        .slot-mpd { background: var(--code-bg); border-left: 1px solid var(--border); }

        /* MODE LAYOUT LOGIC */
        /* 2D */
        body.mode-2d .scene-card .slot-pres { display: flex; grid-area: top; }
        body.mode-2d .scene-card .slot-yaml { display: flex; grid-area: bottom; }
        @media (min-width: 768px) {
            body.mode-2d .scene-card .slot-pres { grid-area: left; border-right: 1px solid var(--border); }
            body.mode-2d .scene-card .slot-yaml { grid-area: right; }
        }

        /* 3D */
        body.mode-3d .scene-card .slot-studio { display: flex; grid-area: top; }
        body.mode-3d .scene-card .slot-mpd { display: flex; grid-area: bottom; }
        @media (min-width: 768px) {
            body.mode-3d .scene-card .slot-studio { grid-area: left; border-right: 1px solid var(--border); }
            body.mode-3d .scene-card .slot-mpd { grid-area: right; }
        }

        /* COMPARE */
        body.mode-compare .scene-card .slot-pres { display: flex; grid-area: top; }
        body.mode-compare .scene-card .slot-studio { display: flex; grid-area: bottom; }
        @media (min-width: 768px) {
            body.mode-compare .scene-card .slot-pres { grid-area: left; border-right: 1px solid var(--border); }
            body.mode-compare .scene-card .slot-studio { grid-area: right; }
        }

        /* COMPONENT STYLES */
        .pane-header {
            padding: 6px 10px; border-bottom: 1px solid var(--border); background: #111;
            display: flex; justify-content: space-between; align-items: center; height: 32px; flex-shrink: 0;
        }
        .pane-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-dim); }
        .pane-btn {
            background: transparent; border: 1px solid var(--border); color: var(--text-dim);
            padding: 2px 6px; font-size: 9px; text-transform: uppercase; cursor: pointer; border-radius: 2px;
        }
        .pane-btn:hover { border-color: var(--gold); color: var(--gold); }

        .hero-img { width: 100%; height: 100%; object-fit: contain; background: #000; cursor: zoom-in; }
        .code-area { flex: 1; overflow: auto; padding: 10px; }
        pre { font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.5; color: #ccc; }

        .studio-wrapper {
            flex: 1; display: flex; flex-direction: column; background: #000; min-height: 0; height: 100%; position: relative;
        }
        .studio-placeholder {
            flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
            background: #000; color: var(--text-dim); gap: 1rem; height: 100%;
        }
        .studio-btn {
            background: var(--panel); border: 1px solid var(--border); color: var(--gold);
            padding: 8px 16px; font-family: 'JetBrains Mono'; font-size: 11px; cursor: pointer; text-transform: uppercase;
        }
        .studio-btn:hover { border-color: var(--gold); background: #111; }
        iframe { width: 100%; height: 100%; border: none; background: #000; display: block; position: absolute; top: 0; left: 0; right: 0; bottom: 0; }

        #toast {
            position: fixed; top: 56px; right: 1rem; background: var(--gold); color: #000;
            padding: 6px 12px; border-radius: 2px; font-size: 11px; font-weight: 700;
            transform: translateY(-200%); transition: transform 0.2s; z-index: 1000;
        }
        #toast.active { transform: translateY(0); }
        .fullscreen { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.95); z-index: 2000; padding: 1rem; justify-content: center; align-items: center; }
        .fullscreen.active { display: flex; }
        .fullscreen img { max-width: 100%; max-height: 100%; object-fit: contain; }

        .yaml .key { color: #89e051; } .yaml .str { color: #a5d6ff; }
        .mpd .step { color: #89e051; font-weight: bold; } .mpd .part { color: #a5d6ff; } .mpd .cmt { color: #666; font-style: italic; }
    </style>
</head>
<body class="mode-2d">

    <div id="toast">COPIED MPD</div>
    <div class="fullscreen" id="fs" onclick="this.classList.remove('active')"><img id="fs-img" src=""></div>

    <header class="header">
        <div class="logo">SHIELD OF ACHILLES</div>
        <div class="mode-toggle">
            <button class="mode-btn active" onclick="setMode('2d')">2D VIEW</button>
            <button class="mode-btn" onclick="setMode('3d')">3D VIEW</button>
            <button class="mode-btn" onclick="setMode('compare')">COMPARE</button>
        </div>
    </header>

    <div class="nav-scroller" id="nav"></div>
    <main class="container" id="main"></main>

    <script>
        const scenes = SCENE_DATA_PLACEHOLDER;
        let activeStudioId = null; 
        let isTransitioning = false; 

        function init() {
            // NAV
            document.getElementById('nav').innerHTML = scenes.map(s => 
                `<button class="nav-pill" onclick="scrollToId('scene-${s.id}')">${s.id}</button>`
            ).join('');

            // SCENES
            document.getElementById('main').innerHTML = scenes.map(s => `
                <article class="scene-card" id="scene-${s.id}">
                    <header class="scene-header">
                        <span class="scene-id">${s.id}</span>
                        <span class="scene-title">${s.title}</span>
                    </header>
                    <div class="viewport">
                        <div class="slot slot-pres">
                            <div class="pane-header"><span class="pane-label">PRES</span><button class="pane-btn" onclick="openFs('${s.image}')">EXPAND</button></div>
                            <img class="hero-img" src="${s.image}" onclick="openFs('${s.image}')" onerror="this.src='';this.style.background='#111'">
                        </div>
                        <div class="slot slot-yaml">
                            <div class="pane-header"><span class="pane-label">YAML</span><button class="pane-btn" onclick="copyText('yaml-${s.id}')">COPY</button></div>
                            <div class="code-area"><pre class="yaml" id="yaml-${s.id}">${highlightYaml(s.yaml.trim())}</pre></div>
                        </div>
                        <div class="slot slot-studio" id="studio-slot-${s.id}">
                            <div class="pane-header"><span class="pane-label">STUDIO</span></div>
                            <div class="studio-wrapper">
                                <div class="studio-placeholder">
                                    <div>Ready to Load</div>
                                    <button class="studio-btn" onclick="loadStudio('${s.id}')">LAUNCH TERMINAL</button>
                                </div>
                            </div>
                        </div>
                        <div class="slot slot-mpd">
                            <div class="pane-header"><span class="pane-label">MPD</span><button class="pane-btn" onclick="copyText('mpd-${s.id}')">COPY</button></div>
                            <div class="code-area"><pre class="mpd" id="mpd-${s.id}">${highlightMpd(s.mpd.trim())}</pre></div>
                        </div>
                    </div>
                </article>
            `).join('');
        }

        window.setMode = (mode) => {
            document.body.className = `mode-${mode}`;
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            document.querySelector(`.mode-btn[onclick="setMode('${mode}')"]`).classList.add('active');
            
            if (activeStudioId && (mode === '3d' || mode === 'compare')) {
                 copyText(`mpd-${activeStudioId}`);
            }
        }

        window.loadStudio = (id) => {
            if (isTransitioning) return; // Debounce
            isTransitioning = true;
            setTimeout(() => isTransitioning = false, 1000);

            // Unload previous safety
            if (activeStudioId && activeStudioId !== id) {
                 const prevWrapper = document.querySelector(`#studio-slot-${activeStudioId} .studio-wrapper`);
                 if (prevWrapper) {
                    // Force GC help
                    const oldIframe = prevWrapper.querySelector('iframe');
                    if (oldIframe) { oldIframe.src = 'about:blank'; }
                    
                    prevWrapper.innerHTML = `
                        <div class="studio-placeholder">
                            <div>Terminated</div>
                            <button class="studio-btn" onclick="loadStudio('${activeStudioId}')">RELAUNCH</button>
                        </div>`;
                 }
            }

            activeStudioId = id;
            const container = document.querySelector(`#studio-slot-${id} .studio-wrapper`);
            container.innerHTML = `<iframe src="https://hartswf0.github.io/tractor-dce-gyo/grecian-urn.html"></iframe>`;
            
            copyText(`mpd-${id}`);
        }

        function copyText(id) {
            const el = document.getElementById(id);
            if(el) {
                const text = el.innerText;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text)
                        .then(() => showToast(id.startsWith('mpd') ? "COPIED MPD - PASTE IN STUDIO" : "COPIED YAML"))
                        .catch(err => {
                            console.error('Clipboard failed', err);
                            showToast("COPY FAILED - SELECT MANUALLY");
                        });
                } else {
                    // Fallback
                    showToast("USE CTRL+C TO COPY");
                }
            }
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.classList.add('active');
            setTimeout(() => t.classList.remove('active'), 2500);
        }

        function scrollToId(id) { document.getElementById(id).scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        function openFs(src) { document.getElementById('fs-img').src = src; document.getElementById('fs').classList.add('active'); }
        function escapeHtml(t) { return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
        function highlightYaml(t) { return escapeHtml(t).replace(/^(\\s*-\\s)/gm, '<span class="bullet">$1</span>').replace(/^(\\s*)([a-z_]+)(:)/gmi, '$1<span class="key">$2</span>$3').replace(/"([^"]*)"/g, '<span class="str">"$1"</span>'); }
        function highlightMpd(t) { return escapeHtml(t).replace(/^(0\\s+\\/\\/.*)$/gm, '<span class="cmt">$1</span>').replace(/^(0\\s+STEP.*)$/gm, '<span class="step">$1</span>').replace(/(parts\\/[^\\s]+\\.dat)/g, '<span class="part">$1</span>'); }

        init();
    </script>
</body>
</html>'''

    scene_json = json.dumps(scene_data, ensure_ascii=False)
    html = html_header.replace("SCENE_DATA_PLACEHOLDER", scene_json)
    
    OUTPUT.write_text(html)
    print(f"✓ Generated {OUTPUT}")

if __name__ == "__main__":
    main()
