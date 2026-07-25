import { useRef, useEffect } from "react";
import gsap from "gsap";

export default function MagneticButton({
  children,
  className = "",
  onClick,
  as = "button",
  href,
  ...props
}) {
  const btnRef = useRef(null);
  const textRef = useRef(null);

  useEffect(() => {
    // Disable magnetic effect on mobile screens
    if (window.innerWidth < 768) return;

    const btn = btnRef.current;
    const text = textRef.current;
    if (!btn) return;

    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;
    let isHovering = false;
    let animId;

    const maxOffset = 12; // Max 12px translation

    const lerp = (start, end, amt) => start + (end - start) * amt;

    const updateLoop = () => {
      if (isHovering) {
        currentX = lerp(currentX, targetX, 0.15);
        currentY = lerp(currentY, targetY, 0.15);

        btn.style.transform = `translate3d(${currentX.toFixed(2)}px, ${currentY.toFixed(
          2
        )}px, 0)`;

        if (text) {
          text.style.transform = `translate3d(${(currentX * 0.4).toFixed(
            2
          )}px, ${(currentY * 0.4).toFixed(2)}px, 0)`;
        }
      }
      animId = requestAnimationFrame(updateLoop);
    };

    const onMouseMove = (e) => {
      const rect = btn.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const deltaX = e.clientX - centerX;
      const deltaY = e.clientY - centerY;

      const distance = Math.hypot(deltaX, deltaY);
      const angle = Math.atan2(deltaY, deltaX);
      const clampedDistance = Math.min(distance, maxOffset * 2.5);

      targetX = Math.cos(angle) * (clampedDistance * 0.35);
      targetY = Math.sin(angle) * (clampedDistance * 0.35);
    };

    const onMouseEnter = () => {
      isHovering = true;
    };

    const onMouseLeave = () => {
      isHovering = false;
      targetX = 0;
      targetY = 0;
      currentX = 0;
      currentY = 0;

      // Elastic spring return on leave using lightweight GSAP tween
      gsap.to(btn, {
        x: 0,
        y: 0,
        duration: 0.5,
        ease: "elastic.out(1, 0.4)",
      });

      if (text) {
        gsap.to(text, {
          x: 0,
          y: 0,
          duration: 0.5,
          ease: "elastic.out(1, 0.4)",
        });
      }
    };

    btn.addEventListener("mousemove", onMouseMove, { passive: true });
    btn.addEventListener("mouseenter", onMouseEnter, { passive: true });
    btn.addEventListener("mouseleave", onMouseLeave, { passive: true });

    animId = requestAnimationFrame(updateLoop);

    return () => {
      btn.removeEventListener("mousemove", onMouseMove);
      btn.removeEventListener("mouseenter", onMouseEnter);
      btn.removeEventListener("mouseleave", onMouseLeave);
      cancelAnimationFrame(animId);
    };
  }, []);

  const Component = as === "a" ? "a" : "button";

  return (
    <Component
      ref={btnRef}
      href={href}
      onClick={onClick}
      className={`magnetic-btn inline-flex items-center justify-center transition-shadow duration-300 ${className}`}
      style={{ willChange: "transform", backfaceVisibility: "hidden" }}
      {...props}
    >
      <span
        ref={textRef}
        className="magnetic-text inline-flex items-center gap-1.5 pointer-events-none"
        style={{ willChange: "transform", backfaceVisibility: "hidden" }}
      >
        {children}
      </span>
    </Component>
  );
}
