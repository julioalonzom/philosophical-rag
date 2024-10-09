import React from 'react';
import { Link } from 'react-router-dom';

const NavBar = ({ user, setUser }) => {
  const handleLogout = () => {
    // Implement logout logic here
    setUser(null);
  };

  return (
    <nav className="bg-blue-500 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white text-2xl font-bold">PhilosophyGPT</Link>
        <div>
          {user ? (
            <>
              <span className="text-white mr-4">Welcome, {user.username}</span>
              <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded">Logout</button>
            </>
          ) : (
            <Link to="/login" className="bg-green-500 text-white px-4 py-2 rounded">Login</Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default NavBar;