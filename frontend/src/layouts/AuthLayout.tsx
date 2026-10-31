import React from 'react';
import { Outlet } from 'react-router-dom';

export const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#070a13] flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient background light orbs */}
      <div className="ambient-orb-indigo top-10 left-10" />
      <div className="ambient-orb-cyan bottom-10 right-10" />

      <div className="w-full max-w-md z-10">
        <Outlet />
      </div>
    </div>
  );
};

