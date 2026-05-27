import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AgentDetail from './pages/AgentDetail'
import Traces from './pages/Traces'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents/:id" element={<AgentDetail />} />
        <Route path="/traces" element={<Traces />} />
      </Routes>
    </Layout>
  )
}

export default App
