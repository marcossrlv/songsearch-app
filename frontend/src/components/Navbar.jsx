import React from 'react'
import { useNavigate } from 'react-router-dom';

const Navbar = () => {

  const navigate = useNavigate();

  const goHome = () => {
    navigate('/');
  };

  return (
    <div className='flex justify-between items-center h-24 max-w-[1240px] mx-auto px-4'>
      <h1 className='w-full text-3xl font-bold text-beige'><button onClick={goHome}>SongSearch</button></h1>
      <ul className='flex'>
        <li className='p-4 text-beige'><button>About</button></li>
      </ul>
    </div>
  )
}

export default Navbar
