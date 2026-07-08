# Schema di Template per Dashboard Neurale 3D (Altair-Brain)

Questo documento definisce il template riproducibile e lo schema dati per generare al volo una console geopolitica/strategica 3D interattiva, sprovvista di dipendenze WebGL esterne. Graphify e futuri agenti possono utilizzare questa struttura per istanziare visualizzazioni 3D per qualsiasi argomento strategico.

---

## 1. Schema Dati (JSON Payload)

Per instanziare il template, l'agente deve generare tre strutture dati JSON:

### A. Nodi del Grafo (`nodes`)
Definisce le coordinate 3D $(x,y,z)$ dei nodi principali all'interno della sfera cerebrale e le relative etichette HUD.
```json
[
  { "id": "nodo_1", "label": "Etichetta HUD", "color": "#codice_esadecimale", "pos": { "x": 0.0, "y": 0.0, "z": 0.0 } }
]
```

### B. Connessioni Tratteggiate (`nodeConnections`)
Definisce i collegamenti logico-sistemici tracciati tra i nodi accesi.
```json
[
  { "from": "nodo_1", "to": "nodo_2", "color": "rgba(r, g, b, alpha)" }
]
```

### C. Contenuto Informativo dei Nodi (`nodeIntelligence`)
Associa a ogni nodo l'analisi dettagliata e la chiave oracolare (I Ching o sintesi del Brain).
```json
{
  "nodo_1": {
    "name": "Titolo Vettore",
    "type": "Sottotitolo / Categoria",
    "color": "var(--colore-css)",
    "text": "Contenuto dettagliato in formato HTML (es. liste, statistiche)",
    "oracle": "Testo oracolare / Ammonimento strategico"
  }
}
```

---

## 2. Blueprint del File HTML (`template_showcase_3d.html`)

Sotto è riportato lo scheletro HTML pronto per l'interpolazione delle stringhe tramite template engine o sostituzione di variabili `{{TOKEN}}`.

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{SHOWCASE_TITLE}}</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

  <style>
    :root {
      --bg-dark: #06080d;
      --bg-card: #0e1322;
      --border-color: rgba(99, 102, 241, 0.25);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      
      --color-primary: #6366f1;
      --color-secondary: #06b6d4;
      --color-emerald: #10b981;
      --color-amber: #f59e0b;
      --color-rose: #f43f5e;
      --color-gold: #fbbf24;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      color: var(--text-main);
      background-color: var(--bg-dark);
      padding: 20px 10px;
      overflow-x: hidden;
    }
    @media (min-width: 768px) { body { padding: 40px 20px; } }
    .wrapper { max-width: 1200px; margin: 0 auto; }
    
    header {
      background: var(--bg-card);
      border: 2px solid var(--border-color);
      border-radius: 8px;
      padding: 25px;
      margin-bottom: 25px;
      box-shadow: 0 1px 0 rgba(255, 255, 255, 0.1) inset, 0 6px 0 #151a2b, 0 15px 25px rgba(0, 0, 0, 0.6);
    }
    .badge-brand {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(99, 102, 241, 0.12);
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #a5b4fc;
      font-size: 0.7rem;
      font-weight: 800;
      padding: 5px 12px;
      border-radius: 3px;
      text-transform: uppercase;
      margin-bottom: 12px;
    }
    h1 {
      font-size: 1.85rem; font-weight: 900; text-transform: uppercase;
      background: linear-gradient(to right, #ffffff, #c7d2fe, #38bdf8);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      display: flex; align-items: center; gap: 12px;
    }
    @media (min-width: 768px) { h1 { font-size: 2.35rem; } }
    
    .command-grid {
      display: grid; grid-template-columns: 1fr; gap: 30px;
    }
    @media (min-width: 950px) { .command-grid { grid-template-columns: 1fr 420px; } }
    
    .panel-3d {
      background: var(--bg-card);
      border: 2px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 1px 0 rgba(255, 255, 255, 0.1) inset, 0 5px 0 #151a2b, 0 15px 25px rgba(0, 0, 0, 0.5);
    }
    h2 {
      font-size: 1.15rem; font-weight: 800; margin-bottom: 20px;
      border-left: 4px solid var(--color-primary); padding-left: 12px;
      text-transform: uppercase; color: #ffffff;
    }
    
    .brain-canvas-container {
      width: 100%; height: 380px; background: #030509;
      border: 2px solid var(--border-color); border-radius: 6px;
      position: relative; overflow: hidden;
    }
    @media (min-width: 768px) { .brain-canvas-container { height: 480px; } }
    canvas { width: 100%; height: 100%; display: block; cursor: grab; touch-action: none; }
    
    .canvas-overlay-tip {
      position: absolute; bottom: 12px; left: 12px; right: 12px;
      background: rgba(4, 6, 11, 0.9); border: 1px solid var(--border-color);
      padding: 6px 10px; border-radius: 4px; font-size: 0.7rem;
      color: var(--text-muted); text-transform: uppercase; text-align: center;
    }
    
    .details-panel { display: flex; flex-direction: column; gap: 25px; }
    .node-details-card {
      background: rgba(14, 19, 34, 0.85); border: 2px solid var(--border-color);
      border-radius: 8px; padding: 20px;
      box-shadow: 0 1px 0 rgba(255, 255, 255, 0.1) inset, 0 5px 0 #151a2b, 0 15px 20px rgba(0, 0, 0, 0.5);
      min-height: 280px; display: flex; flex-direction: column;
    }
    .node-header {
      display: flex; align-items: center; gap: 12px;
      border-bottom: 2px solid var(--border-color); padding-bottom: 12px; margin-bottom: 15px;
    }
    .node-icon-dot { width: 14px; height: 14px; border-radius: 50%; }
    .node-title-text h3 { font-size: 1.15rem; font-weight: 800; text-transform: uppercase; color: #fff; }
    .node-title-text span { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; }
    .node-body-content { font-size: 0.875rem; color: var(--text-muted); line-height: 1.6; flex-grow: 1; }
    
    .oracle-box {
      border: 2px solid var(--color-gold); background: rgba(251, 191, 36, 0.03);
      border-radius: 6px; padding: 15px; margin-top: 15px;
    }
    .oracle-title { font-size: 0.8rem; font-weight: 800; color: var(--color-gold); text-transform: uppercase; }
    .oracle-content { font-style: italic; font-size: 0.85rem; color: #fef08a; }
    
    .tech-specs-sidebar { list-style: none; font-size: 0.825rem; }
    .tech-specs-sidebar li {
      display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-color);
    }
    .tech-specs-sidebar li span.label { color: var(--text-muted); }
    .tech-specs-sidebar li span.value { font-weight: 700; color: #fff; }
    
    .conclusions-box {
      background: linear-gradient(135deg, #101524 0%, #0c0f18 100%);
      border: 2px solid var(--border-color); border-top: 4px solid var(--color-gold);
      border-radius: 8px; padding: 25px;
      box-shadow: 0 1px 0 rgba(255,255,255,0.05) inset, 0 5px 0 #080a13, 0 15px 25px rgba(0,0,0,0.5);
    }
    .conclusions-box h3 { font-size: 1.15rem; font-weight: 800; text-transform: uppercase; color: var(--color-gold); }
    .conclusions-text { font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; }
    
    footer {
      margin-top: 40px; border-top: 2px solid var(--border-color);
      padding-top: 20px; display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted);
    }
  </style>
</head>
<body>

  <div class="wrapper">
    <header>
      <div class="badge-brand">
        <!-- Piccola Stella di Altair nel Badge -->
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 12px; height: 12px; filter: drop-shadow(0 0 2px var(--color-gold)); margin-right: 4px; display: inline-block; vertical-align: middle;">
          <path d="M12 2L14.8 9.2L22 12L14.8 14.8L12 22L9.2 14.8L2 12L9.2 9.2L12 2Z" fill="var(--color-gold)"/>
        </svg>
        <span>Multi-Agent Simulation // Altair-Brain</span>
      </div>
      
      <h1>
        <!-- Grande Stella di Altair nel Titolo principale -->
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 32px; height: 32px; filter: drop-shadow(0 0 8px var(--color-gold)); flex-shrink: 0;">
          <path d="M12 2L14.8 9.2L22 12L14.8 14.8L12 22L9.2 14.8L2 12L9.2 9.2L12 2Z" fill="url(#star-grad)"/>
          <defs>
            <linearGradient id="star-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="var(--color-gold)" />
              <stop offset="100%" stop-color="var(--color-amber)" />
            </linearGradient>
          </defs>
        </svg>
        <span>{{SHOWCASE_TITLE}}</span>
      </h1>
      <p class="tagline">{{SHOWCASE_TAGLINE}}</p>
    </header>

    <div class="command-grid">
      <main>
        <div class="panel-3d">
          <h2>🧠 Struttura Neurale 3D Altair-Brain</h2>
          <div class="brain-canvas-container">
            <canvas id="webgl-canvas"></canvas>
            <div class="canvas-overlay-tip">Trascina per ruotare · Clicca sui nodi per analizzare</div>
          </div>
        </div>
      </main>

      <aside class="details-panel">
        <div class="node-details-card" id="details-card">
          <div class="node-header">
            <div class="node-icon-dot" id="node-color-dot"></div>
            <div class="node-title-text">
              <h3 id="node-name-label">Console</h3>
              <span id="node-type-label">Seleziona un nodo</span>
            </div>
          </div>
          <div class="node-body-content" id="node-body-text">
            Clicca su una delle sfere all'interno del cervello 3D a sinistra.
          </div>
          
          <div class="oracle-box" id="oracle-box" style="display: none;">
            <div class="oracle-title">Oracolo AION</div>
            <div class="oracle-content" id="oracle-text-content"></div>
          </div>
        </div>

        <div class="panel-3d" style="padding: 20px;">
          <h2 style="font-size: 1rem; border-left-color: var(--color-emerald);">⚡ Altair-Brain Specs</h2>
          <ul class="tech-specs-sidebar">
            {{TECH_SPECS_HTML}}
          </ul>
        </div>
      </aside>
    </div>

    <div class="conclusions-box">
      <h3>🔮 Conclusioni Strategiche</h3>
      <div class="conclusions-text">
        {{STRATEGIC_CONCLUSIONS_HTML}}
      </div>
    </div>

    <footer>
      <span>Showcase sviluppata con tecnologia Altair-Brain</span>
      <span>© 2026 Altair Solutions // Riservato</span>
    </footer>
  </div>

  <script>
    const nodeIntelligence = {{NODE_INTELLIGENCE_JSON}};
    const nodes = {{NODES_LIST_JSON}};
    const nodeConnections = {{NODE_CONNECTIONS_JSON}};

    const canvas = document.getElementById('webgl-canvas');
    const ctx = canvas.getContext('2d');

    let width, height;
    let brainPoints = [];
    let brainLines = [];

    let angleX = -0.3;
    let angleY = 0.5;

    const cameraDist = 8;
    let perspectiveScale = 140;

    function resizeCanvas() {
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = width;
      canvas.height = height;
      perspectiveScale = Math.min(width, height) * 0.45;
    }

    function generateBrainGeometry() {
      brainPoints = [];
      const particleCount = 240;
      const hemisphereOffset = 1.6;

      for (let i = 0; i < particleCount; i++) {
        const isRight = Math.random() > 0.5;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(Math.random() * 2 - 1);
        const r = (0.6 + 0.4 * Math.random()) * 2.5;

        const dx = Math.sin(phi * 4) * 0.2;
        const dy = Math.cos(theta * 3.5) * 0.15;
        
        const x = r * Math.sin(phi) * Math.cos(theta) + (isRight ? hemisphereOffset : -hemisphereOffset) + dx;
        const y = r * Math.sin(phi) * Math.sin(theta) * 0.72 + dy;
        const z = r * Math.cos(phi) * 0.8;

        brainPoints.push({ x, y, z });
      }

      brainLines = [];
      for (let i = 0; i < brainPoints.length; i++) {
        let connections = 0;
        for (let j = i + 1; j < brainPoints.length; j++) {
          const dx = brainPoints[i].x - brainPoints[j].x;
          const dy = brainPoints[i].y - brainPoints[j].y;
          const dz = brainPoints[i].z - brainPoints[j].z;
          const dist = Math.hypot(dx, dy, dz);
          
          if (dist < 1.6 && connections < 2) {
            brainLines.push({ p1: i, p2: j });
            connections++;
          }
        }
      }
    }

    function render3DFrame() {
      ctx.clearRect(0, 0, width, height);

      const cosX = Math.cos(angleX);
      const sinX = Math.sin(angleX);
      const cosY = Math.cos(angleY);
      const sinY = Math.sin(angleY);

      const renderQueue = [];

      // Punti
      brainPoints.forEach((p) => {
        let x1 = p.x * cosY - p.z * sinY;
        let z1 = p.z * cosY + p.x * sinY;
        let y2 = p.y * cosX - z1 * sinX;
        let z2 = z1 * cosX + p.y * sinX;

        const depthFactor = cameraDist / (z2 + cameraDist);
        const sx = width / 2 + x1 * perspectiveScale * depthFactor * 0.8;
        const sy = height / 2 + y2 * perspectiveScale * depthFactor * 0.8;

        renderQueue.push({
          type: 'point', x: sx, y: sy, z: z2,
          color: 'rgba(99, 102, 241, ' + Math.max(0.12, 0.55 * depthFactor) + ')',
          size: Math.max(1, 2.2 * depthFactor)
        });
      });

      // Linee
      brainLines.forEach(line => {
        const pt1 = brainPoints[line.p1];
        const pt2 = brainPoints[line.p2];

        let x1_1 = pt1.x * cosY - pt1.z * sinY;
        let z1_1 = pt1.z * cosY + pt1.x * sinY;
        let y2_1 = pt1.y * cosX - z1_1 * sinX;
        let z2_1 = z1_1 * cosX + pt1.y * sinX;

        let x1_2 = pt2.x * cosY - pt2.z * sinY;
        let z1_2 = pt2.z * cosY + pt2.x * sinY;
        let y2_2 = pt2.y * cosX - z1_2 * sinX;
        let z2_2 = z1_2 * cosX + pt2.y * sinX;

        const depthFactor1 = cameraDist / (z2_1 + cameraDist);
        const depthFactor2 = cameraDist / (z2_2 + cameraDist);

        const sx1 = width / 2 + x1_1 * perspectiveScale * depthFactor1 * 0.8;
        const sy1 = height / 2 + y2_1 * perspectiveScale * depthFactor1 * 0.8;
        const sx2 = width / 2 + x1_2 * perspectiveScale * depthFactor2 * 0.8;
        const sy2 = height / 2 + y2_2 * perspectiveScale * depthFactor2 * 0.8;

        renderQueue.push({
          type: 'line', x1: sx1, y1: sy1, x2: sx2, y2: sy2, z: (z2_1 + z2_2) / 2,
          color: 'rgba(79, 70, 229, ' + Math.max(0.04, 0.15 * ((depthFactor1 + depthFactor2)/2)) + ')'
        });
      });

      // Nodi
      const pulseTime = Date.now() * 0.003;
      nodes.forEach(node => {
        const p = node.pos;

        let x1 = p.x * cosY - p.z * sinY;
        let z1 = p.z * cosY + p.x * sinY;
        let y2 = p.y * cosX - z1 * sinX;
        let z2 = z1 * cosX + p.y * sinX;

        const depthFactor = cameraDist / (z2 + cameraDist);
        const sx = width / 2 + x1 * perspectiveScale * depthFactor * 0.8;
        const sy = height / 2 + y2 * perspectiveScale * depthFactor * 0.8;

        node.screenX = sx;
        node.screenY = sy;

        const size = Math.max(6, 12 * depthFactor * (1.0 + Math.sin(pulseTime * 1.5) * 0.1));

        renderQueue.push({
          type: 'node', id: node.id, label: node.label, x: sx, y: sy, z: z2,
          size: size, color: node.color, depthFactor: depthFactor
        });
      });

      renderQueue.sort((a, b) => b.z - a.z);

      renderQueue.forEach(item => {
        if (item.type === 'point') {
          ctx.beginPath();
          ctx.arc(item.x, item.y, item.size, 0, Math.PI * 2);
          ctx.fillStyle = item.color;
          ctx.fill();
        } 
        else if (item.type === 'line') {
          ctx.beginPath();
          ctx.moveTo(item.x1, item.y1);
          ctx.lineTo(item.x2, item.y2);
          ctx.strokeStyle = item.color;
          ctx.lineWidth = 1;
          ctx.stroke();
        } 
        else if (item.type === 'node') {
          ctx.beginPath();
          ctx.arc(item.x, item.y, item.size * 1.8, 0, Math.PI * 2);
          const glowGrad = ctx.createRadialGradient(item.x, item.y, 1, item.x, item.y, item.size * 1.8);
          glowGrad.addColorStop(0, item.color);
          glowGrad.addColorStop(0.3, item.color + '33');
          glowGrad.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.fillStyle = glowGrad;
          ctx.fill();

          ctx.beginPath();
          ctx.arc(item.x, item.y, item.size, 0, Math.PI * 2);
          const sphereGrad = ctx.createRadialGradient(item.x - item.size*0.3, item.y - item.size*0.3, 1, item.x, item.y, item.size);
          sphereGrad.addColorStop(0, '#ffffff');
          sphereGrad.addColorStop(0.2, item.color);
          sphereGrad.addColorStop(1, '#000000');
          ctx.fillStyle = sphereGrad;
          ctx.fill();

          ctx.strokeStyle = 'rgba(255,255,255,0.4)';
          ctx.lineWidth = 1.5;
          ctx.stroke();

          if (item.z < 2) {
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 9.5px "Inter", sans-serif';
            ctx.textAlign = 'center';
            ctx.shadowColor = '#000000';
            ctx.shadowBlur = 4;
            ctx.fillText(item.label, item.x, item.y - item.size - 6);
            ctx.shadowBlur = 0;
          }
        }
      });

      // Linee di collegamento
      nodeConnections.forEach(conn => {
        const fromNode = nodes.find(n => n.id === conn.from);
        const toNode = nodes.find(n => n.id === conn.to);
        
        if (fromNode && toNode && fromNode.screenX !== undefined && toNode.screenX !== undefined) {
          ctx.beginPath();
          ctx.moveTo(fromNode.screenX, fromNode.screenY);
          ctx.lineTo(toNode.screenX, toNode.screenY);
          ctx.strokeStyle = conn.color;
          ctx.lineWidth = 1.5;
          ctx.setLineDash([4, 4]);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      });
    }

    let isDragging = false;
    let dragStart = { x: 0, y: 0 };
    let previousMousePosition = { x: 0, y: 0 };

    function setupInteraction() {
      canvas.addEventListener('mousedown', e => {
        isDragging = true;
        dragStart = { x: e.clientX, y: e.clientY };
        previousMousePosition = { x: e.clientX, y: e.clientY };
      });

      window.addEventListener('mousemove', e => {
        if (!isDragging) return;
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;
        angleY += deltaX * 0.005;
        angleX += deltaY * 0.005;
        previousMousePosition = { x: e.clientX, y: e.clientY };
      });

      window.addEventListener('mouseup', e => {
        if (!isDragging) return;
        isDragging = false;
        const dist = Math.hypot(e.clientX - dragStart.x, e.clientY - dragStart.y);
        if (dist < 5) {
          handleCanvasClick(e.clientX, e.clientY);
        }
      });

      canvas.addEventListener('touchstart', e => {
        if (e.touches.length === 1) {
          isDragging = true;
          const touch = e.touches[0];
          dragStart = { x: touch.clientX, y: touch.clientY };
          previousMousePosition = { x: touch.clientX, y: touch.clientY };
        }
      });

      canvas.addEventListener('touchmove', e => {
        if (!isDragging || e.touches.length !== 1) return;
        const touch = e.touches[0];
        const deltaX = touch.clientX - previousMousePosition.x;
        const deltaY = touch.clientY - previousMousePosition.y;
        angleY += deltaX * 0.005;
        angleX += deltaY * 0.005;
        previousMousePosition = { x: touch.clientX, y: touch.clientY };
      });

      canvas.addEventListener('touchend', e => {
        if (!isDragging) return;
        isDragging = false;
        if (e.changedTouches.length === 1) {
          const touch = e.changedTouches[0];
          const dist = Math.hypot(touch.clientX - dragStart.x, touch.clientY - dragStart.y);
          if (dist < 6) {
            handleCanvasClick(touch.clientX, touch.clientY);
          }
        }
      });
    }

    function handleCanvasClick(clientX, clientY) {
      const rect = canvas.getBoundingClientRect();
      const clickX = clientX - rect.left;
      const clickY = clientY - rect.top;

      let closestNode = null;
      let minDist = 30;

      nodes.forEach(node => {
        if (node.screenX !== undefined && node.screenY !== undefined) {
          const dist = Math.hypot(clickX - node.screenX, clickY - node.screenY);
          if (dist < minDist) {
            minDist = dist;
            closestNode = node;
          }
        }
      });

      if (closestNode) {
        selectNode(closestNode.id);
        const targetAngleY = -Math.atan2(closestNode.pos.x, closestNode.pos.z);
        const targetAngleX = Math.atan2(closestNode.pos.y, Math.hypot(closestNode.pos.x, closestNode.pos.z));
        
        let step = 0;
        function transition() {
          if (step < 12) {
            angleY += (targetAngleY - angleY) * 0.2;
            angleX += (targetAngleX - angleX) * 0.2;
            step++;
            requestAnimationFrame(transition);
          }
        }
        transition();
      }
    }

    function runRenderLoop() {
      function loop() {
        if (!isDragging) {
          angleY += 0.0015;
        }
        render3DFrame();
        requestAnimationFrame(loop);
      }
      requestAnimationFrame(loop);
    }

    function selectNode(id) {
      const data = nodeIntelligence[id];
      if (!data) return;

      document.getElementById('node-color-dot').style.backgroundColor = data.color;
      document.getElementById('node-color-dot').style.boxShadow = `0 0 10px ${data.color}`;
      document.getElementById('node-name-label').innerText = data.name;
      document.getElementById('node-type-label').innerText = data.type;
      document.getElementById('node-body-text').innerHTML = data.text;
      
      document.getElementById('oracle-box').style.display = 'block';
      document.getElementById('oracle-text-content').innerText = data.oracle;

      const card = document.getElementById('details-card');
      card.style.borderColor = data.color;
      setTimeout(() => { card.style.borderColor = 'var(--border-color)'; }, 300);

      if (window.innerWidth < 950) {
        card.scrollIntoView({ behavior: 'smooth' });
      }
    }

    document.addEventListener("DOMContentLoaded", function() {
      resizeCanvas();
      generateBrainGeometry();
      setupInteraction();
      runRenderLoop();
      window.addEventListener('resize', resizeCanvas);
    });
  </script>
</body>
</html>
```
