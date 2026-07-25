import { BrowserRouter, Routes, Route } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import { ToastProvider } from "./components/Toast";
import Landing from "./pages/Landing";
import CustomerPortal from "./pages/CustomerPortal";
import MerchantDashboard from "./pages/MerchantDashboard";
import AdminAuditLog from "./pages/AdminAuditLog";
import AdminAnalytics from "./pages/AdminAnalytics";

export default function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/portal" element={<CustomerPortal />} />
            <Route path="/merchant" element={<MerchantDashboard />} />
            <Route path="/admin" element={<AdminAuditLog />} />
            <Route path="/admin/analytics" element={<AdminAnalytics />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </ErrorBoundary>
  );
}
