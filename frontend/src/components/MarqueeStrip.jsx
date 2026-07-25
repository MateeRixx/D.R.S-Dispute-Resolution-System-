export default function MarqueeStrip() {
  const marqueeText =
    "Fair · Fast · Transparent · AI-Powered · Zero Bias · PCI Compliant · ₹50Cr+ Resolved · ";

  return (
    <div className="w-full bg-[#F0EEEA] border-y border-[#E3DFD8] py-3.5 overflow-hidden select-none cursor-default">
      <div className="flex w-[200%] animate-marquee whitespace-nowrap text-sm font-bold text-[#1A3C5E] tracking-wider uppercase gpu-layer">
        <span className="w-1/2 inline-block px-4">{marqueeText}{marqueeText}</span>
        <span className="w-1/2 inline-block px-4">{marqueeText}{marqueeText}</span>
      </div>
    </div>
  );
}
