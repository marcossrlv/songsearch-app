import React, { useState, useEffect } from 'react';

const prompts = [
    "I’ll be there for you, through all the highs and lows.",
    "You left me standing in the rain, with no one to call my own.",
    "I’m gonna rise above it all, no one can bring me down.",
    "Tonight we’re gonna light up the sky, dancing until the morning light.",
    "I remember those summer nights, we were young and free.",
    "Take me to the mountains, where the air is clear.",
    "We won’t follow the rules, we’re gonna make our own path.",
    "I look in the mirror, searching for who I’ve become.",
    "We stand together, fighting for justice in a world that’s broken.",
    "I’m surrounded by people, but I still feel all alone.",
    "Even when the storm is raging, I’ll find my way to the light.",
    "Pack your bags, let’s chase the sunrise across the world.",
    "I’ll keep dreaming of the stars, reaching higher than before.",
    "Through thick and thin, we’ve been by each other’s side.",
    "I long for the day when we live in harmony, no more fighting.",
    "I hope everything will get better."
];

const ButtonList = ({ handleSearch }) => {
    const [randomPrompts, setRandomPrompts] = useState([]);
  
    useEffect(() => {
      const generatePrompts = () => {
        // Crea una copia del array de prompts
        const promptsCopy = [...prompts];
        const promptsList = [];
    
        // Asegúrate de no agregar prompts repetidos
        while (promptsList.length < 4 && promptsCopy.length > 0) {
          const randomIndex = Math.floor(Math.random() * promptsCopy.length);
          // Agrega el elemento aleatorio a la lista
          promptsList.push(promptsCopy[randomIndex]);
          // Elimina el elemento seleccionado de la copia
          promptsCopy.splice(randomIndex, 1);
        }
    
        setRandomPrompts(promptsList);
      };
    
      generatePrompts(); 
    }, []);     
  
    return (
      <div className="w-full">
        <ul className="flex flex-col p-4 gap-6 h-full max-h-[500px] overflow-y-auto">
          {randomPrompts.map((prompt, index) => (
            <li key={index} className="w-full">
              <button
                className='btn rounded-xl btn-outline hover:bg-beige border-beige text-beige h-14 w-auto text-sm sm:text-sm md:text-base flex items-center justify-center lg:h-12'
                onClick={() => handleSearch(prompt)}
              >
                {prompt}
              </button>
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  export default ButtonList;
