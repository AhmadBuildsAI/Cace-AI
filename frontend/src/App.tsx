import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/Login';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import ContextGraph from './components/ContextGraph';
import Query from './components/Query';
import AgentTraces from './components/AgentTraces';
import SecurityCenter from './components/SecurityCenter';

const App: React.FC = () => (
  <BrowserRouter>
    <Toaster position="top-right" />
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="graph" element={<ContextGraph />} />
        <Route path="query" element={<Query />} />
        <Route path="traces" element={<AgentTraces />} />
        <Route path="security" element={<SecurityCenter />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
);

export default App;
