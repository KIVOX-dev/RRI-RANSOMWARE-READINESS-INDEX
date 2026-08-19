import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import AssessmentFlow from "@/pages/AssessmentFlow";
import BackupResiliencePage from "@/pages/BackupResiliencePage";
import Benchmarking from "@/pages/Benchmarking";
import Canary from "@/pages/Canary";
import Dashboard from "@/pages/Dashboard";
import DetectionMatrixPage from "@/pages/DetectionMatrixPage";
import DwellTime from "@/pages/DwellTime";
import Evidence from "@/pages/Evidence";
import Ledger from "@/pages/Ledger";
import Login from "@/pages/Login";
import LogGaps from "@/pages/LogGaps";
import Oversight from "@/pages/Oversight";
import Overview from "@/pages/Overview";
import Profile from "@/pages/Profile";
import Register from "@/pages/Register";
import Remediation from "@/pages/Remediation";
import RegulatoryCompliance from "@/pages/RegulatoryCompliance";
import Reports from "@/pages/Reports";
import Settings from "@/pages/Settings";
import Trends from "@/pages/Trends";
import Verification from "@/pages/Verification";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/overview" element={<ProtectedRoute><Overview /></ProtectedRoute>} />
      <Route path="/assessment" element={<ProtectedRoute><AssessmentFlow /></ProtectedRoute>} />
      <Route path="/evidence" element={<ProtectedRoute><Evidence /></ProtectedRoute>} />
      <Route path="/verification" element={<ProtectedRoute><Verification /></ProtectedRoute>} />
      <Route path="/backup-resilience" element={<ProtectedRoute><BackupResiliencePage /></ProtectedRoute>} />

      <Route path="/detection-matrix" element={<ProtectedRoute><DetectionMatrixPage /></ProtectedRoute>} />
      <Route path="/log-gaps" element={<ProtectedRoute><LogGaps /></ProtectedRoute>} />
      <Route path="/canary" element={<ProtectedRoute><Canary /></ProtectedRoute>} />
      <Route path="/dwell-time" element={<ProtectedRoute><DwellTime /></ProtectedRoute>} />
      <Route path="/regulatory-compliance" element={<ProtectedRoute><RegulatoryCompliance /></ProtectedRoute>} />

      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/remediation" element={<ProtectedRoute><Remediation /></ProtectedRoute>} />
      <Route path="/trends" element={<ProtectedRoute><Trends /></ProtectedRoute>} />
      <Route path="/benchmarking" element={<ProtectedRoute><Benchmarking /></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />

      <Route path="/oversight" element={<ProtectedRoute><Oversight /></ProtectedRoute>} />
      <Route path="/ledger" element={<ProtectedRoute><Ledger /></ProtectedRoute>} />

      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

      <Route path="/" element={<Navigate to="/overview" replace />} />
      <Route path="*" element={<Navigate to="/overview" replace />} />
    </Routes>
  );
}
