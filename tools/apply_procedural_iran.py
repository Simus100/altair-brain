import json
import re

html_path = 'reports/altair-brain-ai-tools-2026-prototype.html'
aion_path = 'engine/aion.model.json'

with open(aion_path, 'r', encoding='utf-8') as f:
    aion = json.load(f)

aion_nodes = []
aion_edges = []

for cat in ['livelli', 'modalita', 'agenti', 'componenti', 'insegnamenti']:
    for item in aion.get(cat, []):
        if 'id' in item:
            aion_nodes.append({'id': item['id'], 'label': item.get('label', item.get('titolo', item['id'])), 'cat': cat})

node_ids = {n['id']: i for i, n in enumerate(aion_nodes)}

for cat in ['agenti', 'componenti', 'livelli', 'modalita', 'insegnamenti']:
    for item in aion.get(cat, []):
        if 'id' not in item: continue
        u = item['id']
        for rel in ['usa', 'consulta', 'collabora', 'orchestra', 'dominanti']:
            for tgt in item.get(rel, []):
                if tgt in node_ids:
                    aion_edges.append({'source': u, 'target': tgt})

js_code = f"""
    const aionLogicNodes = {json.dumps(aion_nodes)};
    const aionLogicEdges = {json.dumps(aion_edges)};
    
    const topicToAion = {{
        "nodo_market": "aion-analyst",
        "nodo_dev": "aion-adaptive",
        "nodo_design": "aion-visual",
        "nodo_dir": "aion-oracle",
        "nodo_roi": "aion-strategic-engine"
    }};

    function generateBrainGeometry() {{
      brainPoints = [];
      brainLines = [];
      
      const hemisphereOffset = 1.6;
      
      let pIndex = 0;
      aionLogicNodes.forEach(logicNode => {{
          const isRight = Math.random() > 0.5;
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.acos(Math.random() * 2 - 1);
          const r = (0.6 + 0.4 * Math.random()) * 2.5;

          const dx = Math.sin(phi * 4) * 0.2;
          const dy = Math.cos(theta * 3.5) * 0.15;
          
          const bx = r * Math.sin(phi) * Math.cos(theta) + (isRight ? hemisphereOffset : -hemisphereOffset) + dx;
          const by = r * Math.sin(phi) * Math.sin(theta) * 0.72 + dy;
          const bz = r * Math.cos(phi) * 0.8;
          
          const mainPtIndex = pIndex++;
          brainPoints.push({{ 
              x: bx, y: by, z: bz, 
              id: logicNode.id, 
              isAion: true,
              label: logicNode.label,
              cat: logicNode.cat
          }});
          
          for(let k = 0; k < 3; k++) {{
              const sx = bx + (Math.random() - 0.5) * 0.6;
              const sy = by + (Math.random() - 0.5) * 0.6;
              const sz = bz + (Math.random() - 0.5) * 0.6;
              brainPoints.push({{ 
                  x: sx, y: sy, z: sz, 
                  isAion: false,
                  parentId: logicNode.id
              }});
              brainLines.push({{ p1: mainPtIndex, p2: pIndex++ }});
          }}
      }});
      
      aionLogicEdges.forEach(edge => {{
          const p1 = brainPoints.findIndex(p => p.id === edge.source);
          const p2 = brainPoints.findIndex(p => p.id === edge.target);
          if (p1 !== -1 && p2 !== -1) {{
              brainLines.push({{ p1, p2, type: 'aion_logic' }});
          }}
      }});
      
      nodes.forEach(topic => {{
          const targetAionId = topicToAion[topic.id];
          const targetPt = brainPoints.find(p => p.id === targetAionId);
          if (targetPt) {{
              topic.connectedToId = targetAionId;
          }}
      }});
    }}
"""

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'function generateBrainGeometry\(\)\s*\{[\s\S]*?\}\s*function render3DFrame\(\)', lambda m: js_code + "\n    function render3DFrame()", html)

bridge_logic = """
      nodes.forEach(node => {
          if (node.connectedToId) {
              const targetPt = brainPoints.find(p => p.id === node.connectedToId);
              if (targetPt && targetPt.screenX && node.screenX) {
                  ctx.beginPath();
                  ctx.moveTo(node.screenX, node.screenY);
                  ctx.lineTo(targetPt.screenX, targetPt.screenY);
                  ctx.setLineDash([3, 3]);
                  
                  // Convert hex to rgba for the line
                  var result = /^#?([a-f\\d]{2})([a-f\\d]{2})([a-f\\d]{2})$/i.exec(node.color);
                  if(result) {
                      var r = parseInt(result[1], 16);
                      var g = parseInt(result[2], 16);
                      var b = parseInt(result[3], 16);
                      ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.5)`;
                  } else {
                      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                  }
                  
                  ctx.lineWidth = 1;
                  ctx.stroke();
                  ctx.setLineDash([]);
              }
          }
      });
"""

html = html.replace('renderQueue.forEach(item => {', bridge_logic + '\n      renderQueue.forEach(item => {')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
