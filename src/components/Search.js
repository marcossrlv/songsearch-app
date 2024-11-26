import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const Search = () => {
  const navigate = useNavigate();
  const [tracks, setTracks] = useState([]);
  const [text, setText] = useState('');

  const getReturnedParamsFromSpotifyAuth = (hash) => {
    const stringAfterHashtag = hash.substring(1);
    const paramsInUrl = stringAfterHashtag.split("&");
    const paramsSplitUp = paramsInUrl.reduce((accumulater, currentValue) => {
      console.log(currentValue);
      const [key, value] = currentValue.split("=");
      accumulater[key] = value;
      return accumulater;
    }, {});
  
    return paramsSplitUp;
  };

  useEffect(() => {
    if (window.location.hash) {
      const { access_token, expires_in, token_type } =
        getReturnedParamsFromSpotifyAuth(window.location.hash);

      localStorage.clear();

      localStorage.setItem("accessToken", access_token);
      localStorage.setItem("tokenType", token_type);
      localStorage.setItem("expiresIn", expires_in);
    }
  });

  const handleLogout = () => {
    window.localStorage.clear();
    navigate('/');
  };
  
  const handleFindout = () => {
    api.post('/', { text: text })
      .then(response => {
        console.log(response.data);
        setTracks(response.data);
      })
      .catch(error => console.error('Error fetching tracks:', error));
  }

  const handleInputChange = (event) => {
    setText(event.target.value);
  }

  const openLink = (url) => {
    window.open(url, '_blank')
  }

  return (
    <div className='m-5'>
      <div className="flex flex-col">
        <article class="prose m-4">
          <h1>Semantic music search</h1>
        </article>
        <div className='flex'>
          <input type="text" onChange={handleInputChange} placeholder="Type here" className="input input-bordered w-full m-2" />
          <button className="btn btn-circle btn-outline gap-2 m-2" onClick={handleFindout}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="h-4 w-4 opacity-70">
              <path fillRule="evenodd"
                d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z"
                clipRule="evenodd" />
            </svg>
          </button>
        </div>
        <div className='flex flex-col lg:flex-row'>
          {tracks.map((track) => (
          <div className="card bg-base-100 w-96 shadow-xl m-4">
            <figure>
              <img
                src={track.image}
                alt={track.name} />
            </figure>
            <div className="card-body">
              <h2 className="card-title">{track.name} - {track.artist}</h2>
              <h3>Score: {(track.score * 100).toFixed(2)}%</h3>
              <div className="card-actions justify-end">
                <button onClick={() => openLink(track.url)} className="btn btn-primary">Listen</button>
                <button className="btn btn-primary">Save</button>
              </div>
            </div>
          </div>
          ))}
        </div>
        <div className='flex flex-row space-x-3 m-4'>
          <button className="btn btn-xs sm:btn-sm md:btn-md lg:btn-lg" onClick={handleLogout}>Logout</button>
        </div>
      </div>
    </div>
  );
};

export default Search;
