import React from 'react'
import { useNavigate } from 'react-router-dom';

const Hero = () => {

    const navigate = useNavigate();

    const goSearch = () => {
    navigate('/search');
    };

    return (
    <div>
        <div className='max-w-[800px] mt-[-96px] w-full h-screen mx-auto text-center flex flex-col justify-center'> 
            <p className='font-bold p-2 text-moss_green'>A Semantic Search Engine</p>
            <h1 className='md:text-7xl sm:text-6xl text-4xl font-bold text-beige md:py-6'>SongSearch</h1>
            <button onClick={goSearch} className='bg-baby_powder w-[200px] rounded-md font-medium my-6 mx-auto py-3 text-eerie_black'>Try it out!</button>
        </div>
    </div>
    )
}

export default Hero
