import Navbar from "./Navbar";

export default function PortalLayout({ children }) {
  return (
    <div className="min-h-screen bg-drs-bg">
      <Navbar />
      <main className="pt-14">{children}</main>
    </div>
  );
}
