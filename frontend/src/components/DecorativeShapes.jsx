import { useRef, useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function DotGrid({ className = "", opacity = 0.3 }) {
  return (
    <svg className={`pointer-events-none absolute inset-0 w-full h-full ${className}`} viewBox="0 0 1200 800" preserveAspectRatio="none">
      <defs>
        <pattern id="dot-grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
          <circle cx="20" cy="20" r="1" fill="currentColor" opacity={opacity} />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#dot-grid)" />
    </svg>
  );
}

export function FloatingRing({ className = "", size = 300, thickness = 1, opacity = 0.12, speed = 1 }) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      gsap.to(el, {
        y: -20,
        duration: 4 / speed,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
      gsap.to(el, {
        rotate: 360,
        duration: 30 / speed,
        repeat: -1,
        ease: "none",
      });
    }, el);
    return () => ctx.revert();
  }, [speed]);

  return (
    <svg
      ref={ref}
      className={`pointer-events-none absolute ${className}`}
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      fill="none"
    >
      <circle cx={size / 2} cy={size / 2} r={size * 0.42} stroke="currentColor" strokeWidth={thickness} opacity={opacity} />
    </svg>
  );
}

export function FloatingDots({ className = "" }) {
  const ref = useRef(null);

  useEffect(() => {
    const els = ref.current?.querySelectorAll(".fd");
    if (!els?.length) return;
    const ctx = gsap.context(() => {
      els.forEach((el, i) => {
        gsap.to(el, {
          y: -12 + i * 3,
          x: i % 2 === 0 ? 8 : -8,
          duration: 3 + i * 0.5,
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut",
          delay: i * 0.4,
        });
      });
    }, ref.current);
    return () => ctx.revert();
  }, []);

  return (
    <svg ref={ref} className={`pointer-events-none absolute ${className}`} width="200" height="200" viewBox="0 0 200 200" fill="none">
      <circle className="fd" cx="30" cy="50" r="3" fill="currentColor" opacity="0.15" />
      <circle className="fd" cx="170" cy="30" r="2.5" fill="currentColor" opacity="0.12" />
      <circle className="fd" cx="150" cy="160" r="4" fill="currentColor" opacity="0.1" />
      <circle className="fd" cx="60" cy="170" r="2" fill="currentColor" opacity="0.18" />
      <circle className="fd" cx="100" cy="20" r="2" fill="currentColor" opacity="0.08" />
      <circle className="fd" cx="180" cy="100" r="3" fill="currentColor" opacity="0.12" />
      <circle className="fd" cx="20" cy="130" r="2.5" fill="currentColor" opacity="0.15" />
    </svg>
  );
}

export function ParallaxLayer({ children, className = "", speed = 0.2 }) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      ScrollTrigger.create({
        trigger: el.parentElement,
        start: "top bottom",
        end: "bottom top",
        onUpdate: (self) => {
          gsap.set(el, { y: self.progress * speed * 200 });
        },
      });
    }, el);
    return () => ctx.revert();
  }, [speed]);

  return (
    <div ref={ref} className={`pointer-events-none absolute ${className}`}>
      {children}
    </div>
  );
}

export function AmbientGradient({ className = "" }) {
  return (
    <div className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}>
      <div className="absolute -top-1/2 -right-1/4 w-[600px] h-[600px] rounded-full bg-drs-accent/3 blur-[120px] animate-gradient-shift" />
      <div className="absolute -bottom-1/2 -left-1/4 w-[500px] h-[500px] rounded-full bg-drs-accent-soft/3 blur-[100px] animate-gradient-shift" style={{ animationDelay: "-4s" }} />
    </div>
  );
}
