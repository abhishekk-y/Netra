import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';

// Placeholder components until we build them
const DashboardPage = () => <div className="p-4">Dashboard Page</div>;
const TopologyPage = () => <div className="p-4">Topology Page</div>;
const FlowsPage = () => <div className="p-4">Flows Page</div>;
const AlertsPage = () => <div className="p-4">Alerts Page</div>;
const IncidentsPage = () => <div className="p-4">Incidents Page</div>;
const IncidentDetail = () => <div className="p-4">Incident Detail</div>;
const ForecastPage = () => <div className="p-4">Forecast Page</div>;
const PacketsPage = () => <div className="p-4">Packets Page</div>;
const HuntingPage = () => <div className="p-4">Hunting Page</div>;
const AssetsPage = () => <div className="p-4">Assets Page</div>;
const MitrePage = () => <div className="p-4">ATT&CK Matrix Page</div>;
const DNSPage = () => <div className="p-4">DNS Page</div>;
const TLSPage = () => <div className="p-4">TLS Page</div>;
const DeceptionPage = () => <div className="p-4">Deception Page</div>;
const HealthPage = () => <div className="p-4">Health Page</div>;
const SettingsPage = () => <div className="p-4">Settings Page</div>;
const ReplayPage = () => <div className="p-4">Replay Page</div>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="topology" element={<TopologyPage />} />
          <Route path="flows" element={<FlowsPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="incidents/:id" element={<IncidentDetail />} />
          <Route path="forecast" element={<ForecastPage />} />
          <Route path="packets" element={<PacketsPage />} />
          <Route path="hunting" element={<HuntingPage />} />
          <Route path="assets" element={<AssetsPage />} />
          <Route path="mitre" element={<MitrePage />} />
          <Route path="dns" element={<DNSPage />} />
          <Route path="tls" element={<TLSPage />} />
          <Route path="deception" element={<DeceptionPage />} />
          <Route path="health" element={<HealthPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="replay/:id" element={<ReplayPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
