import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/Upload';
import Transactions from './pages/Transactions';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const PAGE_TITLES: Record<string, string> = {
  dashboard: 'Dashboard',
  upload: 'Upload Statement',
  transactions: 'Transactions',
  analytics: 'Analytics',
};

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

function AppContent() {
  const [activePage, setActivePage] = useState('dashboard');
  const [showRegister, setShowRegister] = useState(false);
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    if (showRegister) {
      return <Register onSwitchToLogin={() => setShowRegister(false)} />;
    }
    return <Login onSwitchToRegister={() => setShowRegister(true)} />;
  }

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':    return <Dashboard />;
      case 'upload':       return <UploadPage />;
      case 'transactions': return <Transactions />;
      case 'analytics':    return <Analytics />;
      default:             return <Dashboard />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <TopBar title={PAGE_TITLES[activePage] || 'WealthFlow'} />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}
