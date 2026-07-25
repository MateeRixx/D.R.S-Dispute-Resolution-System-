import { useState, useEffect, useRef } from "react";
import { ArrowRight, Check, Menu, X, Shield, FileText, Zap, Gavel, Quote } from "lucide-react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import LoginModal from "../components/LoginModal";
import HeroScene from "../components/HeroScene";
import MarqueeStrip from "../components/MarqueeStrip";

gsap.registerPlugin(ScrollTrigger);

const FEATURES = [
  { icon: Zap, title: "File in seconds", desc: "Submit a chargeback dispute with automated evidence pulled from Razorpay, Shopify, and Shiprocket." },
  { icon: Shield, title: "AI-powered analysis", desc: "OCR and vision models extract every detail from invoices, receipts, and product images." },
  { icon: Gavel, title: "Fair scoring", desc: "A deterministic rule matrix weighs evidence transparently — no hidden bias, no black box." },
  { icon: FileText, title: "Clear verdicts", desc: "Every decision includes a confidence score and a plain-English summary you can actually understand." },
];

const STATS = [
  { raw: 5000, suffix: "+", label: "Disputes resolved" },
  { raw: 99.2, suffix: "%", label: "AI accuracy rate" },
  { raw: 48, prefix: "< ", suffix: "hr", label: "Average resolution" },
  { raw: 50, prefix: "₹", suffix: "Cr+", label: "Dispute value processed" },
];

function animateCounter(el, target, suffix, prefix) {
  const obj = { val: 0 };
  gsap.to(obj, {
    val: target,
    duration: 1.6,
    ease: "power2.out",
    onUpdate() {
      const v = target % 1 === 0 ? Math.floor(obj.val) : obj.val.toFixed(1);
      el.textContent = `${prefix}${v}${suffix}`;
    },
  });
}

function Btn({ children, className = "", as: Tag = "button", ...props }) {
  return <Tag className={`inline-flex items-center justify-center gap-1.5 transition-all duration-200 ${className}`} {...props}>{children}</Tag>;
}

export default function Landing() {
  const [loginOpen, setLoginOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const progressRef = useRef(null);
  const navRef = useRef(null);
  const heroRef = useRef(null);
  const featuresRef = useRef(null);
  const statsRef = useRef(null);
  const quoteRef = useRef(null);

  useEffect(() => {
    document.fonts.ready.then(() => ScrollTrigger.refresh());
    const onResize = () => ScrollTrigger.refresh();
    window.addEventListener("resize", onResize, { passive: true });

    const ctx = gsap.context(() => {
      if (progressRef.current) {
        gsap.to(progressRef.current, {
          scaleX: 1, ease: "none",
          scrollTrigger: { trigger: document.documentElement, start: "top top", end: "bottom bottom", scrub: 0.1 },
        });
      }

      if (navRef.current) {
        gsap.fromTo(navRef.current, { yPercent: -100, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.6, ease: "power3.out", delay: 0.1 });
      }

      const hero = heroRef.current;
      if (hero) {
        const badge = hero.querySelector(".hero-badge");
        const words = hero.querySelectorAll(".word-span");
        const subtext = hero.querySelector(".hero-subtext");
        const ctas = hero.querySelector(".hero-ctas");
        const trust = hero.querySelector(".hero-trust");
        const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
        if (badge) tl.fromTo(badge, { y: 15, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, delay: 0.1 });
        if (words.length > 0) tl.fromTo(words, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, stagger: 0.05 }, "-=0.2");
        if (subtext) tl.fromTo(subtext, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5 }, "-=0.3");
        if (ctas) tl.fromTo(ctas, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5 }, "-=0.3");
        if (trust) tl.fromTo(trust, { y: 15, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4 }, "-=0.2");
      }

      const features = featuresRef.current;
      if (features) {
        gsap.fromTo(
          features.querySelectorAll(".feature-card"),
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.5, stagger: 0.08, ease: "power2.out", scrollTrigger: { trigger: features, start: "top 85%" } }
        );
      }

      const stats = statsRef.current;
      if (stats) {
        ScrollTrigger.create({
          trigger: stats, start: "top 85%", once: true,
          onEnter: () => {
            stats.querySelectorAll(".stat-item").forEach((el, i) => {
              const s = STATS[i];
              gsap.fromTo(el, { y: 30, opacity: 0 }, {
                y: 0, opacity: 1, duration: 0.5, delay: i * 0.08, ease: "power2.out",
                onStart() { const num = el.querySelector(".stat-num"); if (num) animateCounter(num, s.raw, s.suffix, s.prefix || ""); },
              });
            });
          },
        });
      }

      const quote = quoteRef.current;
      if (quote) {
        gsap.fromTo(
          quote.querySelector(".quote-text"), { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.7, ease: "power3.out", scrollTrigger: { trigger: quote, start: "top 85%" } }
        );
      }
    }, heroRef);

    return () => { window.removeEventListener("resize", onResize); ctx.revert(); };
  }, []);

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#F8F6F3] text-[#1C1917]">
      <div ref={progressRef} className="fixed top-0 left-0 right-0 h-[2px] bg-[#1A3C5E] z-50 origin-left scale-x-0 pointer-events-none" />

      <nav ref={navRef} className="fixed top-0 inset-x-0 z-40 h-16 bg-[#F8F6F3]/95 backdrop-blur-md border-b border-[#E3DFD8]">
        <div className="max-w-6xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#1A3C5E] flex items-center justify-center shadow-sm">
              <span className="text-white text-xs font-bold">D</span>
            </div>
            <span className="font-bold text-[#1C1917] tracking-tight">DRS</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="relative text-sm text-[#6B6560] hover:text-[#1C1917] transition-colors group py-1">
              Features
              <span className="absolute bottom-0 left-0 w-0 h-[1.5px] bg-[#1A3C5E] transition-all duration-200 group-hover:w-full" />
            </a>
            <a href="#stats" className="relative text-sm text-[#6B6560] hover:text-[#1C1917] transition-colors group py-1">
              Impact
              <span className="absolute bottom-0 left-0 w-0 h-[1.5px] bg-[#1A3C5E] transition-all duration-200 group-hover:w-full" />
            </a>
            <Btn onClick={() => setLoginOpen(true)} className="text-sm font-medium text-white bg-[#1A3C5E] hover:bg-[#2E5C8A] px-4 py-2 rounded-lg shadow-sm">
              Sign in
            </Btn>
          </div>
          <button className="md:hidden text-[#1C1917]" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
        {mobileOpen && (
          <div className="md:hidden bg-white border-b border-[#E3DFD8] px-6 py-4 space-y-3 shadow-lg">
            <a href="#features" className="block text-sm text-[#6B6560]" onClick={() => setMobileOpen(false)}>Features</a>
            <a href="#stats" className="block text-sm text-[#6B6560]" onClick={() => setMobileOpen(false)}>Impact</a>
            <button onClick={() => { setLoginOpen(true); setMobileOpen(false); }} className="w-full text-sm font-medium text-white bg-[#1A3C5E] px-4 py-2 rounded-lg">Sign in</button>
          </div>
        )}
      </nav>

      <section ref={heroRef} className="relative min-h-screen flex items-center px-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#EBF0F5]/30 via-transparent to-transparent pointer-events-none" />
        <div className="max-w-6xl mx-auto w-full">
          <div className="grid grid-cols-1 lg:grid-cols-12 items-center gap-12">
            <div className="lg:col-span-7 max-w-2xl">
              <div className="hero-badge inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EBF0F5] text-[#2E5C8A] text-xs font-semibold mb-6">
                <Shield className="w-3.5 h-3.5" /> AI-powered dispute resolution
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-[1.08] tracking-tight text-[#1C1917]">
                <span className="inline-block overflow-hidden"><span className="word-span inline-block mr-2.5">Fair</span></span>
                <span className="inline-block overflow-hidden"><span className="word-span inline-block mr-2.5">resolutions,</span></span>
                <br className="hidden sm:inline" />
                <span className="inline-block overflow-hidden"><span className="word-span inline-block mr-2.5 gradient-text">powered</span></span>
                <span className="inline-block overflow-hidden"><span className="word-span inline-block mr-2.5 gradient-text">by</span></span>
                <span className="inline-block overflow-hidden"><span className="word-span inline-block gradient-text">AI</span></span>
              </h1>
              <p className="hero-subtext text-base md:text-lg text-[#6B6560] mt-5 max-w-xl leading-relaxed">
                India's first automated chargeback resolution platform — transparent, unbiased, and built for D2C e-commerce.
              </p>
              <div className="hero-ctas flex items-center gap-4 mt-8 flex-wrap">
                <Btn onClick={() => setLoginOpen(true)} className="px-5 py-2.5 rounded-lg bg-[#1A3C5E] text-white font-medium text-sm hover:bg-[#2E5C8A] shadow-md hover:-translate-y-0.5">
                  Get started <ArrowRight className="w-4 h-4" />
                </Btn>
                <Btn as="a" href="#features" className="px-5 py-2.5 rounded-lg border border-[#E3DFD8] text-[#6B6560] text-sm font-medium hover:border-[#1C1917]/30 hover:text-[#1C1917] bg-white/50">
                  Learn more
                </Btn>
              </div>
              <div className="hero-trust flex items-center gap-5 mt-10 text-xs text-[#9C958E] font-medium flex-wrap">
                <span className="flex items-center gap-1.5"><Check className="w-3.5 h-3.5 text-[#059669]" /> PCI compliant</span>
                <span className="flex items-center gap-1.5"><Check className="w-3.5 h-3.5 text-[#059669]" /> Zero bias</span>
                <span className="flex items-center gap-1.5"><Check className="w-3.5 h-3.5 text-[#059669]" /> Instant results</span>
              </div>
            </div>
            <div className="lg:col-span-5 hidden lg:block relative">
              <HeroScene />
              <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-[#EBF0F5]/60 blur-3xl -z-10" />
              <div className="absolute -bottom-4 -left-4 w-32 h-32 rounded-full bg-[#1A3C5E]/5 blur-3xl -z-10" />
            </div>
          </div>
        </div>
      </section>

      <MarqueeStrip />

      <section id="features" ref={featuresRef} className="relative py-28 md:py-36 px-6 bg-[#FFFFFF]">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#F8F6F3]/20 to-[#F0EEEA]/30 pointer-events-none" />
        <div className="max-w-6xl mx-auto">
          <div className="max-w-xl mb-14">
            <p className="text-xs font-semibold text-[#2E5C8A] uppercase tracking-[0.12em] mb-3">How it works</p>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] tracking-tight">Everything you need, end to end.</h2>
            <p className="text-[#6B6560] mt-3 leading-relaxed">From filing to verdict — every step is automated, auditable, and completely transparent.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            {FEATURES.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="feature-card bg-[#F0EEEA] rounded-xl p-6 border border-[#E3DFD8]/60 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-200">
                <div className="w-10 h-10 rounded-lg bg-[#EBF0F5] flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-[#2E5C8A]" />
                </div>
                <h3 className="font-bold text-[#1C1917] text-base mb-2">{title}</h3>
                <p className="text-sm text-[#6B6560] leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="stats" ref={statsRef} className="relative py-28 md:py-36 px-6 bg-[#F8F6F3]">
        <div className="absolute inset-0 bg-gradient-to-b from-[#F0EEEA]/40 via-transparent to-[#EBF0F5]/20 pointer-events-none" />
        <div className="max-w-6xl mx-auto">
          <div className="max-w-xl mb-14">
            <p className="text-xs font-semibold text-[#2E5C8A] uppercase tracking-[0.12em] mb-3">Our impact</p>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] tracking-tight">Built to handle the scale of Indian e-commerce.</h2>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
            {STATS.map(({ label }) => (
              <div key={label} className="stat-item bg-[#FFFFFF] rounded-xl p-6 md:p-8 border border-[#E3DFD8] shadow-sm hover:-translate-y-0.5 hover:shadow-md transition-all duration-200">
                <p className="stat-num text-3xl md:text-4xl font-extrabold text-[#1A3C5E] tracking-tight">0</p>
                <p className="text-sm font-medium text-[#6B6560] mt-2">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section ref={quoteRef} className="relative py-32 md:py-44 px-6 bg-[#1A3C5E] text-white overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none">
          <Quote className="w-80 h-80 opacity-[0.06] text-white" />
        </div>
        <div className="quote-text max-w-3xl mx-auto text-center relative z-10">
          <Quote className="w-10 h-10 mx-auto mb-6 text-[#EBF0F5] opacity-60" />
          <blockquote className="text-xl md:text-2xl lg:text-3xl font-medium leading-relaxed tracking-tight text-[#F8F6F3]">
            "DRS has fundamentally changed how we handle chargebacks. What used to take weeks now resolves in under 48 hours — with transparent reasoning we can share with our customers."
          </blockquote>
          <div className="mt-8">
            <p className="font-bold text-base text-white">Aditya Sharma</p>
            <p className="text-sm text-[#EBF0F5]/70 mt-0.5">Head of Payments, D2C Brands India</p>
          </div>
        </div>
      </section>

      <section className="relative py-32 md:py-40 px-6 bg-[#F0EEEA] overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-[#1A3C5E]/[0.03] via-transparent to-transparent pointer-events-none" />
        <div className="max-w-2xl mx-auto text-center relative">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1C1917] tracking-tight">Ready to resolve disputes fairly?</h2>
          <p className="text-[#6B6560] mt-4 max-w-md mx-auto leading-relaxed">Join thousands of merchants and customers who trust DRS for transparent, AI-powered chargeback resolution.</p>
          <div className="mt-10">
            <Btn onClick={() => setLoginOpen(true)} className="px-8 py-3.5 rounded-xl bg-[#1A3C5E] text-white font-semibold text-sm hover:bg-[#2E5C8A] shadow-lg hover:-translate-y-0.5">
              Get started <ArrowRight className="w-4 h-4" />
            </Btn>
          </div>
        </div>
      </section>

      <footer className="py-10 px-6 bg-[#1A3C5E]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#EBF0F5]/60">
          <div className="flex items-center gap-2 font-medium text-[#EBF0F5]/80">
            <div className="w-5 h-5 rounded bg-[#EBF0F5]/20 flex items-center justify-center">
              <span className="text-[#EBF0F5] text-[9px] font-bold">D</span>
            </div>
            DRS — Dispute Resolution System
          </div>
          <p>&copy; {new Date().getFullYear()} DRS. All rights reserved.</p>
        </div>
      </footer>

      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </div>
  );
}
