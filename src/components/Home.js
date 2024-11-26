import React from 'react';
import Result from './Result';

const CLIENT_ID = '7fe9a7334bff4915ac8fbc939f3f26db';
const REDIRECT_URI = 'http://localhost:3000/search';
const AUTH_ENDPOINT = 'https://accounts.spotify.com/authorize';
const RESPONSE_TYPE = 'token';
const SCOPES = ['user-read-private']

const Home = () => {
  const handleLogin = () => {
    window.location = `${AUTH_ENDPOINT}?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=${RESPONSE_TYPE}&scope=${SCOPES}`;
  }
  return (
    <div className='background'>
      <div className='flex-container'>
        <h1>Project codename AMBAR</h1>
        <button onClick={handleLogin}>Login with Spotify</button>
      </div>
    </div>
  );
};

export default Home;
