/* PERSONAA hero: optional Three.js enhancement. CSS/video fallback remains usable. */
const canvas = document.querySelector("#personaa-hero-canvas");
const hero = document.querySelector(".persona-hero");

const defaults = {
  modelPath: canvas?.dataset.modelUrl || "",
  enabled: true,
  rotationSpeed: 0.0025,
  floatIntensity: 0.18,
  mouseInfluence: 0.18,
  quality: "auto",
};
window.PERSONAA_3D_CONFIG = { ...defaults, ...(window.PERSONAA_3D_CONFIG || {}) };

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const coarsePointer = window.matchMedia("(pointer: coarse)").matches;
const lowPower = navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4;

if (canvas && hero && window.PERSONAA_3D_CONFIG.enabled && !reducedMotion && !(coarsePointer && lowPower)) {
  startHero().catch(() => canvas.remove());
}

async function startHero() {
  if (!window.WebGLRenderingContext) throw new Error("WebGL unavailable");
  const THREE = await import("https://unpkg.com/three@0.161.0/build/three.module.js");
  const { RoundedBoxGeometry } = await import("https://unpkg.com/three@0.161.0/examples/jsm/geometries/RoundedBoxGeometry.js");
  const config = window.PERSONAA_3D_CONFIG;
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: !coarsePointer, powerPreference: "low-power" });
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
  camera.position.set(0, 0, 7);
  const group = new THREE.Group();
  scene.add(group);

  const sticker = new THREE.Mesh(
    new RoundedBoxGeometry(3.1, 3.1, 0.16, 5, 0.18),
    new THREE.MeshPhysicalMaterial({ color: 0xeeb1a9, roughness: 0.29, metalness: 0.04, clearcoat: 0.65, clearcoatRoughness: 0.2 })
  );
  const mark = new THREE.Mesh(new THREE.CircleGeometry(0.7, 48), new THREE.MeshStandardMaterial({ color: 0x3c2445, roughness: 0.5 }));
  mark.position.z = 0.1;
  sticker.add(mark); group.add(sticker);
  // The supplied GLB is optional. Until it exists (or if it fails to load),
  // this lightweight sticker remains as the visual fallback.
  if (config.modelPath) {
    try {
      const { GLTFLoader } = await import("https://unpkg.com/three@0.161.0/examples/jsm/loaders/GLTFLoader.js");
      new GLTFLoader().load(config.modelPath, (gltf) => {
        group.remove(sticker);
        gltf.scene.scale.setScalar(1.7);
        group.add(gltf.scene);
      }, undefined, () => {});
    } catch (_) { /* Keep the procedural sticker if the loader is unavailable. */ }
  }
  scene.add(new THREE.HemisphereLight(0xffe8df, 0x372240, 2.2));
  const key = new THREE.DirectionalLight(0xffffff, 2.4); key.position.set(3, 5, 5); scene.add(key);
  const rim = new THREE.PointLight(0xf07d8e, 18, 12); rim.position.set(-4, -1, 3); scene.add(rim);

  let pointerX = 0, pointerY = 0, visible = true, raf = 0;
  const setSize = () => { const box = hero.getBoundingClientRect(); const ratio = Math.min(window.devicePixelRatio || 1, coarsePointer ? 1.25 : 1.75); renderer.setPixelRatio(ratio); renderer.setSize(box.width, box.height, false); camera.aspect = box.width / box.height; camera.updateProjectionMatrix(); };
  const pointerMove = (event) => { const box = hero.getBoundingClientRect(); pointerX = ((event.clientX - box.left) / box.width - .5) * 2; pointerY = ((event.clientY - box.top) / box.height - .5) * 2; };
  const clock = new THREE.Clock();
  const render = () => { if (!visible) return; const elapsed = clock.getElapsedTime(); sticker.rotation.y += config.rotationSpeed; sticker.rotation.x += (pointerY * config.mouseInfluence - sticker.rotation.x) * .035; group.rotation.y += (pointerX * config.mouseInfluence - group.rotation.y) * .025; group.position.y = Math.sin(elapsed * .85) * config.floatIntensity; renderer.render(scene, camera); raf = requestAnimationFrame(render); };
  const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting && !document.hidden; if (visible && !raf) render(); if (!visible) { cancelAnimationFrame(raf); raf = 0; } }, { threshold: .05 });
  const visibility = () => { visible = !document.hidden; if (!visible) { cancelAnimationFrame(raf); raf = 0; } else if (!raf) render(); };
  window.addEventListener("resize", setSize, { passive: true }); window.addEventListener("pointermove", pointerMove, { passive: true }); document.addEventListener("visibilitychange", visibility); observer.observe(hero); setSize(); render();
  window.addEventListener("pagehide", () => { cancelAnimationFrame(raf); observer.disconnect(); renderer.dispose(); sticker.geometry.dispose(); sticker.material.dispose(); mark.geometry.dispose(); mark.material.dispose(); }, { once: true });
}
