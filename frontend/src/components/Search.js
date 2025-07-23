import React, { useEffect, useState, useRef } from 'react';
import api from '../api';
import LyricsCard from './LyricsCard';
import Navbar from './Navbar';
import ButtonList from './ButtonList';

const Search = () => {
  const [tracks, setTracks] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [results, setResults] = useState([]);
  const [text, setText] = useState('');
  const [dialogState, setDialogState] = useState(false);
  const [trackData, setTrackData] = useState({});
  const [chunkData, setChunkData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const resultsRef = useRef(null);

  useEffect(() => {
    const fetchTracks = async () => {
        if (results.length > 0) {
            try {

              const trackPromises = results.map(track =>
                api.get(`/tracks/${track.track_id}`)
              );

              const trackResponses = await Promise.all(trackPromises);
              const trackData = trackResponses.map(response => response.data);
              setTracks(trackData);

            } catch (error) {

              console.error("Error fetching tracks:", error);
            }
        }
    };

    // Definir la función asincrónica para obtener los chunks
    const fetchChunks = async () => {
      if (results.length > 0) {
          try {
              // Recorremos los resultados y agrupamos los chunks por track_id
              const trackPromises = results.map(async (track) => {

                  // Obtenemos las promesas para cada chunk de este track
                  const chunkPromises = track.chunks.map(chunk =>
                      api.get(`/chunks/${chunk.chunk_id}`)
                  );
                  
                  // Esperamos a que se resuelvan todas las promesas de chunks
                  const chunkResponses = await Promise.all(chunkPromises);
                  
                  // Extraemos los datos de las respuestas y los agrupamos con el track
                  const chunkData = chunkResponses.map(response => response.data);

                  return {
                      track_id: track.track_id,  // Incluimos el track_id
                      chunks: chunkData          // Guardamos los chunks
                  };
              });
              const trackData = await Promise.all(trackPromises);
              setChunks(trackData);
          } catch (error) {
              console.error("Error fetching chunks:", error);
          }
      }
    };
    fetchTracks();
    fetchChunks();
  }, [results]);

  useEffect(() => {
    if (tracks.length > 0) {
      executeScroll();
    }
  }, [tracks]);
  
  const handleSearch = (promptText) => {
    setIsLoading(true);
    api.post('/recommend', { text: promptText })
      .then(response => {
        setResults(response.data);
        setIsLoading(false);
      })
      .catch(error => console.error('Error fetching tracks:', error));
  }

  const handleInputChange = (event) => {
    setText(event.target.value);
  }

  const executeScroll = () => resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })

  function openDialog(track) {
    const trackId = track.track_id; 
    setTrackData(track);       
    const trackChunks = chunks.find(chunk => chunk.track_id === trackId);
    if (trackChunks) {
        console.log(trackChunks);
        setChunkData(trackChunks.chunks);  
    } else {
        console.log('No se encontraron chunks para este track');
    }
    setDialogState(true);
  }

  function closeDialog() {
    setDialogState(false);
  }

  return (
    <div className='min-h-screen'>
      <LyricsCard track={trackData} chunks={chunkData} openDialog={dialogState} closeDialog={closeDialog}></LyricsCard>
      <div className="flex flex-1 p-4 m-4 justify-center items-center">
        <article className="prose text-center">
          <h2 className="text-beige">Search a song</h2>
          <h3 className="text-beige">By story, concept or emotion</h3>
        </article>
      </div>
      <div className="flex flex-col">
        <div className='flex'>
          <input type="text" onChange={handleInputChange} placeholder="Type here" className="input input-bordered w-full m-2 text-beige border-beige placeholder-beige focus:border-baby_powder" />
          <button className="btn btn-circle btn-outline gap-2 m-2 hover:bg-beige border-beige" onClick={() => handleSearch(text)}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="h-5 w-5 text-beige hover:text-eerie_black">
              <path fillRule="evenodd"
                d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z"
                clipRule="evenodd" />
            </svg>
          </button>
        </div>
        <ButtonList handleSearch={handleSearch}></ButtonList>
        {isLoading ? (
          <div className="flex justify-center items-center">
            <div className="w-16 h-16 border-4 border-t-4 border-beige border-solid rounded-full animate-spin"></div>
            <span className="ml-4">Loading...</span>
          </div>
        ) : (
        <div className='flex flex-col lg:flex-row' ref={resultsRef}>
          {tracks.map((track, index) => (
          <button className='card bg-base-100 w-96 shadow-xl m-4' onClick={() => openDialog(track)}>
            <figure>
              <img
                src={track.cover}
                alt={track.title} />
            </figure>
            <div className="card-body text-beige items-center">
              <h2 className="card-title">{track.title} - {track.artist}</h2>
              <h3>Score: {(results[index].score * 100).toFixed(2)}%</h3>
            </div>
          </button>
          ))}
        </div>
        )}
      </div>
    </div>
  );
};

export default Search;
