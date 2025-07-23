import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';  // adjust path
import LoginButton from './LoginButton';

const Navbar = () => {
  const navigate = useNavigate();
  const { token, logout: authLogout } = useAuth();

  const goHome = () => {
    navigate('/');
  };

  const goProfile = () => {
    navigate('/profile');  // or wherever your profile page is
  };

  const goAbout = () => {
    navigate('/about');
  };

  const logout = () => {
    authLogout();
    navigate('/'); // redirect to home after logout
  };

  return (
    <div className='flex justify-between items-center h-24 max-w-[1240px] mx-auto px-4'>
      <h1 className='w-full text-3xl font-bold text-beige'>
        <button onClick={goHome}>SongSearch</button>
      </h1>
      <ul className='flex items-center gap-6'>
        <li className='p-4 text-beige'>
          <button onClick={goAbout}>About</button>
        </li>
        {!token ? (
          <li className='p-4 text-beige'><LoginButton>Login</LoginButton></li>
        ) : (
          <>
            <li className='p-4 text-beige'><button onClick={goProfile}>Profile</button></li>
            <li className='p-4 text-beige'><button onClick={logout}>Logout</button></li>
          </>
        )}
      </ul>
    </div>
  );
};

export default Navbar;
