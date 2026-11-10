// Research Agent web UI: Three.js "agent core + tool constellation" and the chat client.
// All model/tool text is inserted with textContent (never innerHTML) so tool output cannot inject HTML.

const $ = (selector) => document.querySelector(selector);
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Cosmetic grouping only (matches the legend in index.html); unknown tools get the default colour.
const TOOL_COLORS = {
  timeline: "#4cc9f0", social_search: "#4cc9f0", lookup: "#4cc9f0", fetch: "#4cc9f0",
  papers: "#90be6d", paper_text: "#90be6d", policy: "#90be6d",
  format: "#b388ff", clarify: "#ffd166", send: "#ff6b6b",
};
const TEAM_COLOR = "#ff4fd8";
const DEFAULT_COLOR = "#dddddd";

const SUGGESTIONS = [
  "Tin tức AI hôm nay có gì nổi bật?",
  "Tweet mới nhất của Sam Altman là gì?",
  "Tìm bài báo mới về AI agent evaluation trên arXiv",
  "Cho mình citation APA của bài 'Attention Is All You Need' của Ashish Vaswani, Noam Shazeer, năm 2017",
  "Đăng bản tin này lên Telegram giúp mình",
];

function colorFor(tool) {
  if (tool.team_tool) return TEAM_COLOR;
  return TOOL_COLORS[tool.name] || DEFAULT_COLOR;
}

// ---------------------------------------------------------------- Three.js stage

function noopStage() {
  return { setTools() {}, pulse() {}, setThinking() {} };
}

async function createStage() {
  let THREE;
  try {
    THREE = await import("three");
  } catch (error) {
    console.warn("Three.js could not be loaded (offline?). The chat still works.", error);
    return noopStage();
  }

  const canvas = $("#stage");
  const labelLayer = $("#labels");
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch (error) {
    console.warn("WebGL is not available. The chat still works.", error);
    return noopStage();
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x060914, 0.018);
  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 120);
  camera.position.set(0, 0, 12.5);

  scene.add(new THREE.AmbientLight(0x6070a0, 0.8));
  const coreLight = new THREE.PointLight(0x66ccff, 90, 40, 2);
  scene.add(coreLight);
  const rim = new THREE.DirectionalLight(0xff4fd8, 0.6);
  rim.position.set(-6, 4, 5);
  scene.add(rim);

  // Radial glow texture (drawn on a canvas, no external asset).
  const glowCanvas = document.createElement("canvas");
  glowCanvas.width = glowCanvas.height = 128;
  const g = glowCanvas.getContext("2d");
  const grad = g.createRadialGradient(64, 64, 4, 64, 64, 64);
  grad.addColorStop(0, "rgba(120,200,255,0.9)");
  grad.addColorStop(0.35, "rgba(70,120,255,0.35)");
  grad.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
  const glowTexture = new THREE.CanvasTexture(glowCanvas);

  // Agent core.
  const core = new THREE.Group();
  const coreMesh = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.95, 2),
    new THREE.MeshStandardMaterial({
      color: 0x4cc9f0, emissive: 0x1b6fff, emissiveIntensity: 0.9,
      roughness: 0.35, metalness: 0.25, flatShading: true,
    }),
  );
  const cage = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.45, 1),
    new THREE.MeshBasicMaterial({ color: 0x7aa2ff, wireframe: true, transparent: true, opacity: 0.35 }),
  );
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture, blending: THREE.AdditiveBlending, transparent: true, depthWrite: false,
  }));
  glow.scale.set(7, 7, 1);
  core.add(coreMesh, cage, glow);
  scene.add(core);

  // Background particles.
  const starCount = 900;
  const starPositions = new Float32Array(starCount * 3);
  for (let i = 0; i < starCount; i += 1) {
    const radius = 14 + Math.random() * 30;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    starPositions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    starPositions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    starPositions[i * 3 + 2] = radius * Math.cos(phi);
  }
  const starGeometry = new THREE.BufferGeometry();
  starGeometry.setAttribute("position", new THREE.BufferAttribute(starPositions, 3));
  const stars = new THREE.Points(starGeometry, new THREE.PointsMaterial({
    color: 0x9fb6ff, size: 0.06, transparent: true, opacity: 0.8, depthWrite: false,
  }));
  scene.add(stars);

  // Tool constellation.
  const constellation = new THREE.Group();
  scene.add(constellation);
  /** @type {Map<string, any>} */
  const nodes = new Map();
  const pulses = [];
  const tmp = new THREE.Vector3();

  function clearNodes() {
    for (const node of nodes.values()) {
      constellation.remove(node.group);
      node.group.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
      node.label.remove();
    }
    nodes.clear();
  }

  function setTools(tools) {
    clearNodes();
    const count = tools.length;
    const radius = 4.8;
    tools.forEach((tool, i) => {
      const y = count > 1 ? 1 - (i / (count - 1)) * 2 : 0;
      const ring = Math.sqrt(Math.max(0, 1 - y * y));
      const theta = i * Math.PI * (3 - Math.sqrt(5));
      const position = new THREE.Vector3(Math.cos(theta) * ring * radius, y * radius * 0.72, Math.sin(theta) * ring * radius);
      const color = new THREE.Color(colorFor(tool));

      const group = new THREE.Group();
      group.position.copy(position);
      const mesh = new THREE.Mesh(
        tool.team_tool ? new THREE.IcosahedronGeometry(0.38, 0) : new THREE.OctahedronGeometry(0.3, 0),
        new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.55, roughness: 0.4, metalness: 0.2, flatShading: true }),
      );
      group.add(mesh);
      if (tool.team_tool) {
        const halo = new THREE.Mesh(
          new THREE.RingGeometry(0.6, 0.66, 48),
          new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.7, side: THREE.DoubleSide }),
        );
        group.add(halo);
        group.userData.halo = halo;
      }
      constellation.add(group);

      const lineGeometry = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), position.clone()]);
      const line = new THREE.Line(lineGeometry, new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.16 }));
      constellation.add(line);
      group.userData.line = line;

      const label = document.createElement("div");
      label.className = "label" + (tool.team_tool ? " team" : "");
      label.style.setProperty("--c", colorFor(tool));
      label.textContent = tool.name;
      label.title = tool.description || tool.name;
      labelLayer.appendChild(label);

      nodes.set(tool.name, { group, mesh, line, label, color, flash: 0, seed: Math.random() * 6.28 });
    });
  }

  function pulse(toolName) {
    const node = nodes.get(toolName);
    if (!node) return;
    const ball = new THREE.Mesh(
      new THREE.SphereGeometry(0.14, 16, 16),
      new THREE.MeshBasicMaterial({ color: node.color, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }),
    );
    scene.add(ball);
    pulses.push({ ball, node, t: 0 });
  }

  let thinking = false;
  function setThinking(value) { thinking = Boolean(value); }

  // Layout: keep the scene centred in the free area next to the chat panel.
  function resize() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    const narrow = width <= 820;
    const panel = narrow ? 0 : Math.min(440, width);
    const offsetX = narrow ? 0 : panel / 2;
    const offsetY = narrow ? height * 0.29 : 0;
    camera.setViewOffset(width, height, offsetX, offsetY, width, height);
    camera.updateProjectionMatrix();
  }
  window.addEventListener("resize", resize);
  resize();

  const pointer = { x: 0, y: 0 };
  window.addEventListener("pointermove", (event) => {
    if (reduceMotion) return;
    pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (event.clientY / window.innerHeight) * 2 - 1;
  });

  const clock = new THREE.Clock();
  let elapsed = 0;
  const speed = reduceMotion ? 0.25 : 1;

  function frame() {
    requestAnimationFrame(frame);
    const dt = Math.min(clock.getDelta(), 0.05);
    elapsed += dt;

    const spin = (thinking ? 1.8 : 0.35) * speed;
    core.rotation.y += dt * spin;
    core.rotation.x += dt * spin * 0.4;
    cage.rotation.y -= dt * spin * 1.4;
    const beat = 1 + Math.sin(elapsed * (thinking ? 7 : 1.6)) * (thinking ? 0.08 : 0.03) * speed;
    core.scale.setScalar(beat);
    coreMesh.material.emissiveIntensity = (thinking ? 1.6 : 0.9) + Math.sin(elapsed * 3) * 0.2 * speed;
    glow.material.opacity = thinking ? 1 : 0.75;

    constellation.rotation.y += dt * 0.1 * speed;
    stars.rotation.y += dt * 0.012 * speed;

    for (let i = pulses.length - 1; i >= 0; i -= 1) {
      const p = pulses[i];
      p.t += dt / 0.9;
      if (p.t >= 1) {
        scene.remove(p.ball);
        p.ball.geometry.dispose();
        p.ball.material.dispose();
        p.node.flash = 1;
        p.node.label.classList.add("hot");
        const label = p.node.label;
        setTimeout(() => label.classList.remove("hot"), 2600);
        pulses.splice(i, 1);
        continue;
      }
      p.node.group.getWorldPosition(tmp);
      const ease = p.t * p.t * (3 - 2 * p.t);
      p.ball.position.set(0, 0, 0).lerp(tmp, ease);
      p.ball.scale.setScalar(1 + Math.sin(p.t * Math.PI) * 1.4);
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    for (const node of nodes.values()) {
      node.flash = Math.max(0, node.flash - dt * 0.55);
      node.mesh.rotation.y += dt * 0.8 * speed;
      node.mesh.rotation.x += dt * 0.5 * speed;
      const bob = 1 + Math.sin(elapsed * 1.4 + node.seed) * 0.06 * speed;
      node.group.scale.setScalar(bob * (1 + node.flash * 0.9));
      node.mesh.material.emissiveIntensity = 0.55 + node.flash * 2.4;
      node.line.material.opacity = 0.16 + node.flash * 0.7;
      if (node.group.userData.halo) node.group.userData.halo.lookAt(camera.position);

      node.group.getWorldPosition(tmp);
      node.worldZ = tmp.z;
      tmp.project(camera);
      const visible = tmp.z < 1;
      // Dim labels of tools that are behind the core so they do not float over it.
      const behind = node.worldZ < -0.5;
      node.label.style.opacity = visible ? (behind ? "0.3" : "1") : "0";
      if (visible) {
        const x = (tmp.x * 0.5 + 0.5) * width;
        const y = (-tmp.y * 0.5 + 0.5) * height;
        node.label.style.transform = `translate(${x.toFixed(1)}px, ${(y + 22).toFixed(1)}px) translateX(-50%)`;
      }
    }

    if (!reduceMotion) {
      camera.position.x += (pointer.x * 0.9 - camera.position.x) * 0.04;
      camera.position.y += (-pointer.y * 0.6 - camera.position.y) * 0.04;
    }
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
  }
  frame();

  return { setTools, pulse, setThinking };
}

// ---------------------------------------------------------------- chat client

const state = { sessionId: null, tools: [], busy: false, stage: noopStage() };

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function scrollLog() {
  const log = $("#log");
  log.scrollTop = log.scrollHeight;
}

function addMessage(kind, text) {
  const node = el("div", `msg ${kind}`, text);
  $("#log").appendChild(node);
  scrollLog();
  return node;
}

function briefArgs(args) {
  const text = Object.entries(args || {})
    .map(([key, value]) => `${key}=${typeof value === "string" ? value : JSON.stringify(value)}`)
    .join(", ");
  return text.length > 90 ? `${text.slice(0, 89)}…` : text;
}

function pretty(value) {
  const text = JSON.stringify(value, null, 2);
  return text.length > 4000 ? `${text.slice(0, 4000)}\n…(đã cắt bớt)` : text;
}

function toolCard(event) {
  const meta = state.tools.find((tool) => tool.name === event.tool);
  const result = event.result;
  const failed = Boolean(result && typeof result === "object" && "error" in result);
  const details = el("details", `tool${failed ? " failed" : ""}`);
  if (meta) details.style.setProperty("--c", colorFor(meta));
  const summary = el("summary");
  summary.append(el("span", "name", `🔧 ${event.tool}`), el("span", "brief", briefArgs(event.args)));
  details.appendChild(summary);
  details.appendChild(el("pre", "", `args:\n${pretty(event.args)}\n\nresult:\n${pretty(result)}`));
  return details;
}

function renderAgentReply(payload) {
  const bubble = el("div", "msg agent");
  if (payload.status === "waiting_for_user") bubble.appendChild(el("div", "badge", "Agent đang hỏi lại bạn"));
  if (payload.status === "max_tool_rounds") bubble.appendChild(el("div", "badge", "Đã dừng vì đạt giới hạn số vòng gọi tool"));
  bubble.appendChild(document.createTextNode(payload.assistant_text || "(không có nội dung trả lời)"));
  if (payload.tool_events && payload.tool_events.length) {
    const wrap = el("div", "tools");
    payload.tool_events.forEach((event) => wrap.appendChild(toolCard(event)));
    bubble.appendChild(wrap);
  }
  $("#log").appendChild(bubble);
  scrollLog();
}

function setBusy(busy) {
  state.busy = busy;
  $("#send").disabled = busy;
  $("#send").textContent = busy ? "Đang xử lý…" : "Gửi";
  state.stage.setThinking(busy);
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  let payload = null;
  try { payload = await response.json(); } catch { /* non-JSON error body */ }
  return { ok: response.ok, status: response.status, payload };
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message || state.busy) return;
  addMessage("user", message);
  $("#input").value = "";
  const typing = el("div", "msg agent");
  const dots = el("span", "typing");
  dots.append(el("span"), el("span"), el("span"));
  dots.setAttribute("aria-label", "Agent đang xử lý");
  typing.appendChild(dots);
  $("#log").appendChild(typing);
  scrollLog();
  setBusy(true);

  try {
    const { ok, status, payload } = await postJson("/api/chat", { session_id: state.sessionId, message });
    typing.remove();
    if (payload && payload.session_id) state.sessionId = payload.session_id;
    if (!ok) {
      const reason = (payload && payload.error) || `HTTP ${status}`;
      addMessage("error", `Lỗi: ${reason}`);
      return;
    }
    (payload.tool_events || []).forEach((event, index) => {
      setTimeout(() => state.stage.pulse(event.tool), index * 380);
    });
    renderAgentReply(payload);
  } catch (error) {
    typing.remove();
    addMessage("error", `Không kết nối được server: ${error.message}`);
  } finally {
    setBusy(false);
    $("#input").focus();
  }
}

async function resetConversation() {
  if (state.sessionId) {
    try { await postJson("/api/reset", { session_id: state.sessionId }); } catch { /* ignore */ }
  }
  state.sessionId = null;
  $("#log").replaceChildren();
  addMessage("system", "Đã bắt đầu cuộc trò chuyện mới.");
}

async function init() {
  const suggestions = $("#suggestions");
  SUGGESTIONS.forEach((text) => {
    const button = el("button", "", text);
    button.type = "button";
    button.addEventListener("click", () => sendMessage(text));
    suggestions.appendChild(button);
  });

  $("#form").addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage($("#input").value);
  });
  $("#input").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      sendMessage($("#input").value);
    }
  });
  $("#reset").addEventListener("click", resetConversation);

  // Fetch server info first so the chat is usable even if Three.js is slow or blocked.
  try {
    const response = await fetch("/api/info");
    const info = await response.json();
    state.tools = info.tools || [];
    const keyNote = info.key_configured === false ? " · ⚠ chưa cấu hình API key" : "";
    $("#meta").textContent = `${info.provider} / ${info.model} · ${info.version} · ${state.tools.length} tool${keyNote}`;
    $("#meta").title = info.artifact_version;
  } catch (error) {
    $("#meta").textContent = "Không lấy được thông tin server";
  }
  addMessage("system", "Hỏi agent bất cứ điều gì về tin tức, bài đăng, paper hoặc citation. Mỗi lần gọi tool sẽ hiện ra bên dưới câu trả lời.");
  $("#input").focus();

  // The 3D scene loads last; the chat above already works without it.
  state.stage = await createStage();
  state.stage.setTools(state.tools);
  state.stage.setThinking(state.busy);
}

init();
