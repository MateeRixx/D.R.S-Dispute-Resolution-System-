import { useRef, useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export default function HeroGraphic({ className = "" }) {
  const svgRef = useRef(null);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        svg.querySelectorAll(".hg-ring"),
        { scale: 0.8, opacity: 0 },
        { scale: 1, opacity: 0.15, duration: 1.8, stagger: 0.3, ease: "power3.out" }
      );
      gsap.fromTo(
        svg.querySelectorAll(".hg-node"),
        { scale: 0, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.6, stagger: 0.08, ease: "back.out(2)", delay: 0.5 }
      );
      gsap.fromTo(
        svg.querySelectorAll(".hg-line"),
        { scaleY: 0, opacity: 0, transformOrigin: "center center" },
        { scaleY: 1, opacity: 0.4, duration: 0.8, stagger: 0.05, ease: "power2.out", delay: 0.8 }
      );
      gsap.fromTo(
        svg.querySelectorAll(".hg-path"),
        { opacity: 0 },
        { opacity: 0.35, duration: 1.5, stagger: 0.15, ease: "power2.out", delay: 1 }
      );

      svg.querySelectorAll(".hg-pulse").forEach((el, i) => {
        gsap.to(el, {
          scale: 1.8,
          opacity: 0,
          duration: 2 + i * 0.3,
          repeat: -1,
          delay: i * 0.5,
          ease: "power2.out",
          transformOrigin: "center center",
        });
      });

      ScrollTrigger.create({
        trigger: svg,
        start: "top bottom",
        end: "bottom top",
        onUpdate: (self) => {
          gsap.set(svg.querySelectorAll(".hg-ring"), { y: -self.progress * 40 });
          gsap.set(svg.querySelectorAll(".hg-node"), { y: -self.progress * 20 });
          gsap.set(svg.querySelectorAll(".hg-pulse"), { y: -self.progress * 20 });
        },
      });
    }, svg);

    return () => ctx.revert();
  }, []);

  return (
    <svg
      ref={svgRef}
      className={className}
      viewBox="0 0 500 500"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="accent-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#1A3C5E" />
          <stop offset="100%" stopColor="#2E5C8A" />
        </linearGradient>
        <linearGradient id="accent-grad-light" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#1A3C5E" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#2E5C8A" stopOpacity="0.1" />
        </linearGradient>
      </defs>

      {/* Background rings */}
      <circle className="hg-ring" cx="250" cy="250" r="200" stroke="#1A3C5E" strokeWidth="0.5" opacity="0.12" />
      <circle className="hg-ring" cx="250" cy="250" r="155" stroke="#1A3C5E" strokeWidth="0.5" opacity="0.1" />
      <circle className="hg-ring" cx="250" cy="250" r="110" stroke="#1A3C5E" strokeWidth="0.5" opacity="0.08" />

      {/* Curved flow paths */}
      <path className="hg-path" d="M250 50 C 250 150, 150 200, 100 250 C 50 300, 100 350, 150 400" stroke="#1A3C5E" strokeWidth="1" opacity="0.3" fill="none" />
      <path className="hg-path" d="M250 50 C 250 150, 350 200, 400 250 C 450 300, 400 350, 350 400" stroke="#2E5C8A" strokeWidth="1" opacity="0.25" fill="none" />
      <path className="hg-path" d="M100 100 C 180 180, 220 140, 250 200 C 280 260, 320 320, 400 400" stroke="#1A3C5E" strokeWidth="0.8" opacity="0.2" fill="none" strokeDasharray="4 4" />

      {/* Center shield/balance shape */}
      <path d="M250 140 L 310 175 L 310 260 C 310 310, 280 350, 250 360 C 220 350, 190 310, 190 260 L 190 175 Z" stroke="url(#accent-grad)" strokeWidth="1.5" opacity="0.25" fill="none" />
      <path d="M250 160 L 290 185 L 290 250 C 290 290, 270 320, 250 330 C 230 320, 210 290, 210 250 L 210 185 Z" stroke="url(#accent-grad)" strokeWidth="1" opacity="0.15" fill="none" />

      {/* Connected nodes */}
      <circle className="hg-node" cx="250" cy="140" r="8" fill="#1A3C5E" opacity="0.7" />
      <circle className="hg-node" cx="190" cy="175" r="5" fill="#2E5C8A" opacity="0.6" />
      <circle className="hg-node" cx="310" cy="175" r="5" fill="#2E5C8A" opacity="0.6" />
      <circle className="hg-node" cx="250" cy="360" r="6" fill="#1A3C5E" opacity="0.6" />
      <circle className="hg-node" cx="160" cy="250" r="4" fill="#2E5C8A" opacity="0.5" />
      <circle className="hg-node" cx="340" cy="250" r="4" fill="#2E5C8A" opacity="0.5" />
      <circle className="hg-node" cx="100" cy="250" r="3" fill="#1A3C5E" opacity="0.4" />
      <circle className="hg-node" cx="400" cy="250" r="3" fill="#1A3C5E" opacity="0.4" />
      <circle className="hg-node" cx="250" cy="100" r="3" fill="#2E5C8A" opacity="0.5" />
      <circle className="hg-node" cx="250" cy="400" r="3" fill="#2E5C8A" opacity="0.4" />

      {/* Connecting lines between nodes */}
      <line className="hg-line" x1="250" y1="148" x2="190" y2="175" stroke="#1A3C5E" strokeWidth="0.8" opacity="0.4" />
      <line className="hg-line" x1="250" y1="148" x2="310" y2="175" stroke="#1A3C5E" strokeWidth="0.8" opacity="0.4" />
      <line className="hg-line" x1="190" y1="175" x2="160" y2="250" stroke="#1A3C5E" strokeWidth="0.6" opacity="0.35" />
      <line className="hg-line" x1="310" y1="175" x2="340" y2="250" stroke="#1A3C5E" strokeWidth="0.6" opacity="0.35" />
      <line className="hg-line" x1="160" y1="250" x2="250" y2="360" stroke="#1A3C5E" strokeWidth="0.6" opacity="0.35" />
      <line className="hg-line" x1="340" y1="250" x2="250" y2="360" stroke="#1A3C5E" strokeWidth="0.6" opacity="0.35" />
      <line className="hg-line" x1="100" y1="250" x2="160" y2="250" stroke="#1A3C5E" strokeWidth="0.5" opacity="0.3" />
      <line className="hg-line" x1="340" y1="250" x2="400" y2="250" stroke="#1A3C5E" strokeWidth="0.5" opacity="0.3" />
      <line className="hg-line" x1="250" y1="100" x2="250" y2="140" stroke="#1A3C5E" strokeWidth="0.5" opacity="0.3" />
      <line className="hg-line" x1="250" y1="360" x2="250" y2="400" stroke="#1A3C5E" strokeWidth="0.5" opacity="0.3" />

      {/* Pulse dots */}
      <circle className="hg-pulse" cx="250" cy="140" r="12" stroke="#1A3C5E" strokeWidth="1" opacity="0.6" fill="none" />
      <circle className="hg-pulse" cx="250" cy="360" r="10" stroke="#2E5C8A" strokeWidth="1" opacity="0.5" fill="none" />
      <circle className="hg-pulse" cx="160" cy="250" r="8" stroke="#1A3C5E" strokeWidth="0.8" opacity="0.4" fill="none" />
      <circle className="hg-pulse" cx="340" cy="250" r="8" stroke="#2E5C8A" strokeWidth="0.8" opacity="0.4" fill="none" />

      {/* Small decorative dots */}
      <circle cx="80" cy="120" r="1.5" fill="#1A3C5E" opacity="0.2" />
      <circle cx="420" cy="120" r="1.5" fill="#1A3C5E" opacity="0.2" />
      <circle cx="80" cy="380" r="1.5" fill="#1A3C5E" opacity="0.2" />
      <circle cx="420" cy="380" r="1.5" fill="#1A3C5E" opacity="0.2" />
      <circle cx="250" cy="50" r="1.5" fill="#1A3C5E" opacity="0.15" />
      <circle cx="250" cy="450" r="1.5" fill="#1A3C5E" opacity="0.15" />
    </svg>
  );
}
