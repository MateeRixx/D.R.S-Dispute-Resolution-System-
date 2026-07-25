import { useEffect, useRef, useState } from "react";

export default function CustomCursor() {
  const dotRef = useRef(null);
  const ringRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);
  const [isClicked, setIsClicked] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768 || "ontouchstart" in window);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile, { passive: true });

    const mousePos = { x: -100, y: -100 };
    const dotPos = { x: -100, y: -100 };
    const ringPos = { x: -100, y: -100 };

    const onMouseMove = (e) => {
      mousePos.x = e.clientX;
      mousePos.y = e.clientY;
    };

    const onMouseDown = () => setIsClicked(true);
    const onMouseUp = () => setIsClicked(false);

    window.addEventListener("mousemove", onMouseMove, { passive: true });
    window.addEventListener("mousedown", onMouseDown, { passive: true });
    window.addEventListener("mouseup", onMouseUp, { passive: true });

    const handleMouseOver = (e) => {
      const target = e.target.closest(
        "a, button, [role='button'], input, select, .magnetic-btn, .tilt-card, [data-cursor-hover]"
      );
      setIsHovered(!!target);
    };
    window.addEventListener("mouseover", handleMouseOver, { passive: true });

    const lerp = (s, e, a) => s + (e - s) * a;
    const render = () => {
      dotPos.x = lerp(dotPos.x, mousePos.x, 0.45);
      dotPos.y = lerp(dotPos.y, mousePos.y, 0.45);
      ringPos.x = lerp(ringPos.x, mousePos.x, 0.12);
      ringPos.y = lerp(ringPos.y, mousePos.y, 0.12);

      const dot = dotRef.current;
      const ring = ringRef.current;
      if (dot) dot.style.transform = `translate3d(${dotPos.x}px,${dotPos.y}px,0)`;
      if (ring) ring.style.transform = `translate3d(${ringPos.x}px,${ringPos.y}px,0)`;
      requestAnimationFrame(render);
    };
    requestAnimationFrame(render);

    return () => {
      window.removeEventListener("resize", checkMobile);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("mouseover", handleMouseOver);
    };
  }, []);

  if (isMobile) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      <div
        ref={dotRef}
        className={`fixed top-0 left-0 w-3 h-3 -mt-1.5 -ml-1.5 rounded-full bg-[#1A3C5E] pointer-events-none ${isClicked ? "scale-75" : "scale-100"}`}
        style={{ willChange: "transform" }}
      />
      <div
        ref={ringRef}
        className={`fixed top-0 left-0 rounded-full border pointer-events-none ${isHovered ? "w-[60px] h-[60px] bg-[#1A3C5E]/15 border-[#1A3C5E]/60" : "w-[40px] h-[40px] bg-transparent border-[#1A3C5E]/30"} ${isClicked ? "scale-90" : "scale-100"}`}
        style={{ willChange: "transform" }}
      />
    </div>
  );
}
