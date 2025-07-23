import React from "react";

const About = () => {
  return (
    <div className="min-h-screen max-w-3xl mx-auto p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-4 text-beige">About SongSearch</h1>
      <p className="mb-2">
        SongSearch is a web app that helps you discover and explore your favorite music using the Spotify API.
      </p>
      <p className="mb-2">
        You can log in with your Spotify account to access personalized features like viewing your playlists and profile.
      </p>
      <p>
        This project is built with React.js on the frontend and Flask on the backend, using modern authentication techniques.
      </p>
    </div>
  );
};

export default About;
