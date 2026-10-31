import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/common/Sidebar';
import { Navbar } from '../components/common/Navbar';

export const MainLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen bg-[#070a13] text-slate-100 relative overflow-x-hidden">
      {/* Ambient background refraction orbs */}
      <div className="ambient-orb-indigo -top-20 -left-20" />
      <div className="ambient-orb-cyan top-40 right-10" />

      {/* Persistent Left Sidebar */}
      <Sidebar />

      {/* Main View Area */}
      <div className="flex-1 flex flex-col min-w-0 z-10">
        <Navbar />
        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

