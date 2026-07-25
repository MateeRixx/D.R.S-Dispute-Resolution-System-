import { useRef, useEffect } from "react";

export default function CardTilt({ children, className = "", ...props }) {
  const cardRef = useRef(null);

  useEffect(() => {
    if (window.innerWidth < 768) return;

    const card = cardRef.current;
    if (!card) return;

    let animId;
    let isHovering = false;
    let targetRX = 0, targetRY = 0, curRX = 0, curRY = 0, curS = 1, targetS = 1;
    let bounds = null;

    const lerp = (s, e, a) => s + (e - s) * a;

    const tick = () => {
      if (!isHovering && Math.abs(curRX) < 0.01 && Math.abs(curRY) < 0.01 && Math.abs(curS - 1) < 0.001) {
        animId = 0;
        return;
      }
      curRX = lerp(curRX, targetRX, 0.15);
      curRY = lerp(curRY, targetRY, 0.15);
      curS = lerp(curS, targetS, 0.15);
      card.style.transform = `perspective(1000px) rotateX(${curRX.toFixed(2)}deg) rotateY(${curRY.toFixed(2)}deg) scale3d(${curS.toFixed(3)},${curS.toFixed(3)},1)`;
      animId = requestAnimationFrame(tick);
    };

    const startLoop = () => {
      if (!animId) animId = requestAnimationFrame(tick);
    };

    const onEnter = () => {
      isHovering = true;
      bounds = card.getBoundingClientRect();
      targetS = 1.02;
      startLoop();
    };

    const onMove = (e) => {
      if (!isHovering) return;
      if (!bounds) bounds = card.getBoundingClientRect();
      const x = e.clientX - bounds.left;
      const y = e.clientY - bounds.top;
      targetRX = ((y - bounds.height / 2) / (bounds.height / 2)) * -7;
      targetRY = ((x - bounds.width / 2) / (bounds.width / 2)) * 7;
      card.style.setProperty("--tilt-x", `${x}px`);
      card.style.setProperty("--tilt-y", `${y}px`);
    };

    const onLeave = () => {
      isHovering = false;
      bounds = null;
      targetRX = 0; targetRY = 0; targetS = 1;
      startLoop();
    };

    card.addEventListener("mouseenter", onEnter, { passive: true });
    card.addEventListener("mousemove", onMove, { passive: true });
    card.addEventListener("mouseleave", onLeave, { passive: true });

    return () => {
      card.removeEventListener("mouseenter", onEnter);
      card.removeEventListener("mousemove", onMove);
      card.removeEventListener("mouseleave", onLeave);
      if (animId) cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <div
      ref={cardRef}
      className={`tilt-card relative overflow-hidden rounded-xl transition-shadow duration-300 ${className}`}
      style={{ transformStyle: "preserve-3d", willChange: "transform" }}
      {...props}
    >
      <div
        className="pointer-events-none absolute inset-0 rounded-xl opacity-0 transition-opacity duration-500 z-10"
        style={{
          background: `radial-gradient(350px circle at var(--tilt-x, 50%) var(--tilt-y, 50%), rgba(26,60,94,0.08), transparent 70%)`,
        }}
      />
      <div className="relative z-0">{children}</div>
    </div>
  );
}
