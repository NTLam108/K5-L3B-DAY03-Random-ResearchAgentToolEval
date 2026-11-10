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

// Each tool is shown as a real object (CC0 models from Poly Haven, see assets/CREDITS.md).
// The metaphor is ours: it is only a visual hint, not a statement about what the tool does internally.
const TOOL_MODELS = {
  lookup: "magnifying_glass_01",        // searching the web
  fetch: "vintage_microscope",          // reading one page closely
  timeline: "mantel_clock_01",          // posts over time
  social_search: "vintage_radio_transceiver", // listening to what people say
  papers: "book_encyclopedia_set_01",   // finding papers
  paper_text: "binder_notebook",        // full text of a paper
  policy: "drawer_cabinet",             // internal documents
  format: "office_notepads",            // laying out a digest
  clarify: "Megaphone_01",              // asking the user
  send: "postcard_set_01",              // sending out
  cite: "stationery_supplies",          // writing a citation
};
// Objects modelled lying flat are tilted toward the camera, otherwise they look like a thin line.
const MODEL_TILT = {
  binder_notebook: -0.5, office_notepads: -0.7, stationery_supplies: -0.5, book_encyclopedia_set_01: -0.3,
};
// Small or flat sets look tiny next to the others; scale them up a little (relative to MODEL_SIZE).
const MODEL_SCALE = {
  binder_notebook: 1.3, stationery_supplies: 1.45, book_encyclopedia_set_01: 1.25, vintage_radio_transceiver: 1.15,
};
const MODEL_SIZE = 1.25;               // longest side of every object, in scene units
const MODEL_URL = (id) => `/static/assets/models/${id}/${id}_1k.gltf`;
const ENV_URL = "/static/assets/env/studio.hdr";

function noopStage() {
  return { setTools() {}, pulse() {}, setThinking() {}, whenLoaded: Promise.resolve() };
}

async function createStage() {
  let THREE;
  try {
    THREE = await import("three");
  } catch (error) {
    console.warn("Three.js could not be loaded (offline?). The chat still works.", error);
    return noopStage();
  }
  let GLTFLoader = null;
  let RGBELoader = null;
  try {
    ({ GLTFLoader } = await import("three/addons/loaders/GLTFLoader.js"));
    ({ RGBELoader } = await import("three/addons/loaders/RGBELoader.js"));
  } catch (error) {
    console.warn("Three.js loaders could not be loaded; using plain shapes.", error);
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
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(46, 1, 0.1, 120);
  camera.position.set(0, 0.4, 15.5);

  // Studio HDRI = the light source AND what polished metal reflects. Without it, fall back to plain lights.
  let hasEnvironment = false;
  const environmentReady = (async () => {
    if (!RGBELoader) return;
    try {
      const hdr = await new RGBELoader().loadAsync(ENV_URL);
      hdr.mapping = THREE.EquirectangularReflectionMapping;
      const pmrem = new THREE.PMREMGenerator(renderer);
      const envMap = pmrem.fromEquirectangular(hdr).texture;
      scene.environment = envMap;
      scene.background = hdr;
      scene.backgroundBlurriness = 0.75;
      scene.backgroundIntensity = 0.05;
      pmrem.dispose();
      hasEnvironment = true;
    } catch (error) {
      console.warn("HDRI could not be loaded; using plain lights.", error);
    }
    if (!hasEnvironment) {
      scene.add(new THREE.HemisphereLight(0xffffff, 0x302820, 1.4));
    }
  })();

  const key = new THREE.DirectionalLight(0xfff1dc, 1.6);
  key.position.set(5, 7, 8);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0x9fb4ff, 0.35);
  fill.position.set(-7, 2, -4);
  scene.add(fill);

  // Agent core: glowing blue sphere inside a wire cage.
  const glowCanvas = document.createElement("canvas");
  glowCanvas.width = glowCanvas.height = 128;
  const g = glowCanvas.getContext("2d");
  const grad = g.createRadialGradient(64, 64, 4, 64, 64, 64);
  grad.addColorStop(0, "rgba(120,200,255,0.9)");
  grad.addColorStop(0.35, "rgba(70,120,255,0.35)");
  grad.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
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
    map: new THREE.CanvasTexture(glowCanvas), blending: THREE.AdditiveBlending, transparent: true, depthWrite: false,
  }));
  glow.scale.set(7, 7, 1);
  core.add(coreMesh, cage, glow);
  scene.add(core);

  // Background: slow-drifting stars (the blurred studio light is set once the HDRI has loaded).
  const starCount = 1100;
  const starPositions = new Float32Array(starCount * 3);
  for (let i = 0; i < starCount; i += 1) {
    const radius = 16 + Math.random() * 34;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    starPositions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    starPositions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    starPositions[i * 3 + 2] = radius * Math.cos(phi);
  }
  const starGeometry = new THREE.BufferGeometry();
  starGeometry.setAttribute("position", new THREE.BufferAttribute(starPositions, 3));
  const stars = new THREE.Points(starGeometry, new THREE.PointsMaterial({
    color: 0xaec0ff, size: 0.07, transparent: true, opacity: 0.85, depthWrite: false,
  }));
  scene.add(stars);
  const thinkingLight = new THREE.PointLight(0x66aaff, 0, 14, 2);
  scene.add(thinkingLight);

  const constellation = new THREE.Group();
  scene.add(constellation);
  // Two concentric orbits in one tilted plane. Tools on the same orbit keep their spacing while it spins,
  // and the two orbits are far enough apart that objects never overlap.
  const ORBIT_TILT = -1.05;
  const INNER_RADIUS = 2.9;
  const OUTER_RADIUS = 5.0;
  const orbit = new THREE.Group();
  orbit.rotation.x = ORBIT_TILT;
  const innerRing = new THREE.Group();
  const outerRing = new THREE.Group();
  orbit.add(innerRing, outerRing);
  constellation.add(orbit);
  /** @type {Map<string, any>} */
  const nodes = new Map();
  const pulses = [];
  const tmp = new THREE.Vector3();
  const gltfLoader = GLTFLoader ? new GLTFLoader() : null;
  const modelCache = new Map();
  let loadToken = 0;

  function loadModel(id) {
    if (!modelCache.has(id)) {
      modelCache.set(id, gltfLoader.loadAsync(MODEL_URL(id)).then((gltf) => gltf.scene));
    }
    return modelCache.get(id);
  }

  function fitModel(source, modelId) {
    const object = source.clone(true);
    object.traverse((child) => {
      if (child.isMesh) {
        child.material = child.material.clone();
        if (child.material.emissive) child.material.emissive.set(0x000000);
      }
    });
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const scale = (MODEL_SIZE * (MODEL_SCALE[modelId] || 1)) / Math.max(size.x, size.y, size.z, 1e-6);
    const holder = new THREE.Group();
    // Move the model's centre to the origin, then scale it so its longest side is MODEL_SIZE.
    object.position.copy(center).multiplyScalar(-scale);
    object.scale.setScalar(scale);
    holder.add(object);
    holder.rotation.x = MODEL_TILT[modelId] || 0;
    return holder;
  }

  function placeholderShape(color) {
    return new THREE.Mesh(
      new THREE.SphereGeometry(0.28, 24, 24),
      new THREE.MeshStandardMaterial({ color, metalness: 0.8, roughness: 0.35 }),
    );
  }

  function clearNodes() {
    for (const node of nodes.values()) {
      node.group.parent?.remove(node.group);
      node.line.parent?.remove(node.line);
      node.line.geometry.dispose();
      node.line.material.dispose();
      node.group.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material && !obj.userData.sharedMaterial) obj.material.dispose();
      });
      node.label.remove();
    }
    nodes.clear();
  }

  function setTools(tools) {
    clearNodes();
    const token = ++loadToken;
    const count = tools.length;
    const innerCount = count >= 6 ? Math.min(4, Math.floor(count / 3)) : 0;
    const outerCount = count - innerCount;
    const jobs = [];
    tools.forEach((tool, i) => {
      // The first tools fill the inner orbit, the rest the outer one.
      const inner = i < innerCount;
      const slot = inner ? i : i - innerCount;
      const slots = inner ? innerCount : outerCount;
      const angle = (slot / slots) * Math.PI * 2 + (inner ? Math.PI / slots : 0) - Math.PI / 2;
      const orbitRadius = inner ? INNER_RADIUS : OUTER_RADIUS;
      const position = new THREE.Vector3(Math.cos(angle) * orbitRadius, Math.sin(angle) * orbitRadius, 0);
      const parentRing = inner ? innerRing : outerRing;
      const color = new THREE.Color(colorFor(tool));

      const group = new THREE.Group();
      group.position.copy(position);
      const spinner = new THREE.Group();
      group.add(spinner);
      const placeholder = placeholderShape(color);
      spinner.add(placeholder);

      // Colour-coding ring (the objects keep their real colours). Always faces the camera.
      const band = new THREE.Mesh(
        new THREE.RingGeometry(tool.team_tool ? 0.72 : 0.7, tool.team_tool ? 0.78 : 0.735, 64),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: tool.team_tool ? 0.95 : 0.5, side: THREE.DoubleSide }),
      );
      group.add(band);
      parentRing.add(group);

      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), position.clone()]),
        new THREE.LineBasicMaterial({ color: 0xcdb98f, transparent: true, opacity: 0.14 }),
      );
      parentRing.add(line);

      const label = document.createElement("div");
      label.className = "label" + (tool.team_tool ? " team" : "");
      label.style.setProperty("--c", colorFor(tool));
      label.textContent = tool.name;
      label.title = tool.description || tool.name;
      labelLayer.appendChild(label);

      const node = { group, spinner, band, bandBase: band.material.opacity, line, label, color, flash: 0, seed: Math.random() * 6.28, materials: [], worldZ: 0 };
      nodes.set(tool.name, node);

      const modelId = TOOL_MODELS[tool.name];
      if (gltfLoader && modelId) {
        jobs.push(loadModel(modelId).then((source) => {
          if (token !== loadToken) return;
          const model = fitModel(source, modelId);
          spinner.remove(placeholder);
          placeholder.geometry.dispose();
          placeholder.material.dispose();
          spinner.add(model);
          model.traverse((child) => { if (child.isMesh) node.materials.push(child.material); });
        }).catch((error) => console.warn(`Model for ${tool.name} failed; keeping the plain shape.`, error)));
      }
    });
    stage.whenLoaded = Promise.all([environmentReady, ...jobs]).then(() => undefined);
    return stage.whenLoaded;
  }

  function pulse(toolName) {
    const node = nodes.get(toolName);
    if (!node) return;
    const ball = new THREE.Mesh(
      new THREE.SphereGeometry(0.1, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0xffd9a0, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }),
    );
    ball.userData.sharedMaterial = false;
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
    camera.setViewOffset(width, height, narrow ? 0 : panel / 2, narrow ? height * 0.29 : 0, width, height);
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
  const flashColor = new THREE.Color();
  const worldPosition = new THREE.Vector3();

  function frame() {
    requestAnimationFrame(frame);
    const dt = Math.min(clock.getDelta(), 0.05);
    elapsed += dt;

    const spin = (thinking ? 1.6 : 0.3) * speed;
    core.rotation.y += dt * spin;
    core.rotation.x += dt * spin * 0.4;
    cage.rotation.y -= dt * spin * 1.4;
    core.scale.setScalar(1 + Math.sin(elapsed * (thinking ? 7 : 1.6)) * (thinking ? 0.08 : 0.03) * speed);
    coreMesh.material.emissiveIntensity = (thinking ? 1.6 : 0.9) + Math.sin(elapsed * 3) * 0.2 * speed;
    glow.material.opacity = thinking ? 1 : 0.75;
    thinkingLight.intensity += ((thinking ? 14 + Math.sin(elapsed * 6) * 5 : 0) - thinkingLight.intensity) * Math.min(1, dt * 5);
    stars.rotation.y += dt * 0.012 * speed;

    innerRing.rotation.z += dt * 0.11 * speed;
    outerRing.rotation.z -= dt * 0.065 * speed;

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
      p.ball.scale.setScalar(1 + Math.sin(p.t * Math.PI) * 1.6);
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    // Where the core appears on screen: labels of tools hidden behind it get dimmed.
    tmp.set(0, 0, 0).project(camera);
    const coreX = (tmp.x * 0.5 + 0.5) * width;
    const coreY = (-tmp.y * 0.5 + 0.5) * height;
    for (const node of nodes.values()) {
      node.flash = Math.max(0, node.flash - dt * 0.55);
      node.spinner.rotation.y += dt * 0.55 * speed;
      node.spinner.rotation.x = Math.sin(elapsed * 0.5 + node.seed) * 0.12 * speed;
      node.spinner.position.y = Math.sin(elapsed * 1.2 + node.seed) * 0.05 * speed;
      node.group.scale.setScalar(1 + node.flash * 0.35);
      flashColor.copy(node.color);
      for (const material of node.materials) {
        if (material.emissive) {
          material.emissive.copy(flashColor);
          material.emissiveIntensity = node.flash * 0.55;
        }
      }
      node.band.material.opacity = Math.min(1, node.bandBase + node.flash * 0.5);
      node.band.lookAt(camera.position);
      node.line.material.opacity = 0.14 + node.flash * 0.6;

      node.group.getWorldPosition(worldPosition);
      node.worldZ = worldPosition.z;
      tmp.copy(worldPosition).project(camera);
      const visible = tmp.z < 1;
      const x = (tmp.x * 0.5 + 0.5) * width;
      const y = (-tmp.y * 0.5 + 0.5) * height;
      const behind = node.worldZ < 0 && Math.hypot(x - coreX, y - coreY) < 140;
      node.label.style.opacity = visible ? (behind ? "0.3" : "1") : "0";
      if (visible) {
        const distance = camera.position.distanceTo(tmp.set(0, 0, 0).add(worldPosition));
        const pxPerUnit = height / (2 * Math.tan((camera.fov * Math.PI) / 360) * distance);
        const offset = pxPerUnit * 0.82 + 6;
        node.label.style.transform = `translate(${x.toFixed(1)}px, ${(y + offset).toFixed(1)}px) translateX(-50%)`;
      }
    }

    if (!reduceMotion) {
      camera.position.x += (pointer.x * 0.9 - camera.position.x) * 0.04;
      camera.position.y += (0.4 - pointer.y * 0.6 - camera.position.y) * 0.04;
    }
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
  }
  frame();

  const stage = { setTools, pulse, setThinking, whenLoaded: environmentReady };
  return stage;
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
  state.stage.setThinking(state.busy);
  const loading = $("#loading");
  try {
    await state.stage.setTools(state.tools);
  } finally {
    if (loading) loading.remove();
  }
}

init();
