import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { RegistryPage } from './pages/RegistryPage'
import { SessionsPage } from './pages/SessionsPage'
import { SessionDetailPage } from './pages/SessionDetailPage'
import { PoliciesPage } from './pages/PoliciesPage'
import { RegulationsPage } from './pages/RegulationsPage'
import { ViolationsPage } from './pages/ViolationsPage'
import { IncidentsPage } from './pages/IncidentsPage'
import { ReportsPage } from './pages/ReportsPage'
import { SettingsPage } from './pages/SettingsPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/registry" element={<RegistryPage />} />
        <Route path="/sessions" element={<SessionsPage />} />
        <Route path="/sessions/:id" element={<SessionDetailPage />} />
        <Route path="/policies" element={<PoliciesPage />} />
        <Route path="/regulations" element={<RegulationsPage />} />
        <Route path="/violations" element={<ViolationsPage />} />
        <Route path="/incidents" element={<IncidentsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
