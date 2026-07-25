import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function HeroScene() {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    // Disable WebGL scene on mobile screens (<768px)
    if (window.innerWidth < 768) return;

    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const width = container.clientWidth || 380;
    const height = container.clientHeight || 380;

    // Scene, Camera, Renderer setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.z = 6;

    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);

    // Optimized Ambient & Directional Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x2e5c8a, 1.2);
    dirLight.position.set(5, 5, 5);
    scene.add(dirLight);

    // 1. Floating Icosahedron Wireframe
    const geometry = new THREE.IcosahedronGeometry(1.6, 1);
    const material = new THREE.MeshPhongMaterial({
      color: 0x1a3c5e,
      wireframe: true,
      shininess: 80,
    });
    const icosahedron = new THREE.Mesh(geometry, material);
    scene.add(icosahedron);

    // 2. Inner Core
    const innerGeo = new THREE.IcosahedronGeometry(1.3, 0);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x2e5c8a,
      transparent: true,
      opacity: 0.15,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerMesh);

    // 3. 800 Orbiting Particles
    const particleCount = 800;
    const particlePositions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const radius = 2.2 + Math.random() * 2.4;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      particlePositions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      particlePositions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      particlePositions[i * 3 + 2] = radius * Math.cos(phi);
    }

    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(particlePositions, 3)
    );

    // Soft Radial Texture
    const createParticleTexture = () => {
      const pCanvas = document.createElement("canvas");
      pCanvas.width = 32;
      pCanvas.height = 32;
      const ctx = pCanvas.getContext("2d");
      const grad = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
      grad.addColorStop(0, "rgba(46, 92, 138, 0.9)");
      grad.addColorStop(0.5, "rgba(235, 240, 245, 0.4)");
      grad.addColorStop(1, "rgba(255, 255, 255, 0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 32, 32);
      return new THREE.CanvasTexture(pCanvas);
    };

    const particleMaterial = new THREE.PointsMaterial({
      size: 0.12,
      map: createParticleTexture(),
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const particleSystem = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particleSystem);

    // Parallax Mouse Tilt
    let targetRotationX = 0;
    let targetRotationY = 0;

    const onMouseMove = (e) => {
      const mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      const mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
      targetRotationY = mouseX * 0.26;
      targetRotationX = mouseY * 0.26;
    };

    window.addEventListener("mousemove", onMouseMove, { passive: true });

    // Smooth Independent WebGL Loop (Zero Scroll Overhead)
    let animId;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      icosahedron.rotation.y += 0.003;
      innerMesh.rotation.y += 0.003;
      particleSystem.rotation.y += 0.001;

      icosahedron.rotation.x += (targetRotationX - icosahedron.rotation.x) * 0.05;
      icosahedron.rotation.z += (targetRotationY - icosahedron.rotation.z) * 0.05;
      innerMesh.rotation.x += (targetRotationX - innerMesh.rotation.x) * 0.05;

      const floatY = Math.sin(elapsedTime * 1.5) * 0.15;
      icosahedron.position.y = floatY;
      innerMesh.position.y = floatY;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize, { passive: true });

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animId);
      geometry.dispose();
      material.dispose();
      innerGeo.dispose();
      innerMat.dispose();
      particleGeometry.dispose();
      particleMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div ref={containerRef} className="relative w-full h-[400px] flex items-center justify-center">
      <canvas
        ref={canvasRef}
        className="w-full h-full block hidden md:block transition-opacity duration-300 gpu-layer"
      />
    </div>
  );
}
