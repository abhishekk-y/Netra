import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';

import DashboardPage from './components/dashboard/DashboardPage';
import TopologyPage from './components/topology/TopologyPage';
import FlowsPage from './components/flows/FlowsPage';
import AlertsPage from './components/alerts/AlertsPage';
import IncidentsPage from './components/incidents/IncidentsPage';
import IncidentDetail from './components/incidents/IncidentDetail';
import ForecastPage from './components/forecast/ForecastPage';
import PacketsPage from './components/packets/PacketsPage';
import HuntingPage from './components/hunting/HuntingPage';
import AssetsPage from './components/assets/AssetsPage';
import MitrePage from './components/mitre/MitrePage';
import HealthPage from './components/health/HealthPage';
import ReplayPage from './components/forensics/ReplayPage';
import SettingsPage from './components/settings/SettingsPage';
import DeceptionPage from './components/deception/DeceptionPage';

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
          <Route path="health" element={<HealthPage />} />
          <Route path="deception" element={<DeceptionPage />} />
          <Route path="forensics/replay" element={<ReplayPage />} />
          <Route path="replay/:id" element={<ReplayPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
