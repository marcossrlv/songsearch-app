// src/components/LoginButton.js
const LoginButton = () => {
  const CLIENT_ID = "529e6a6015224fc1b6608522cb55a352";
  const REDIRECT_URI = "http://localhost:5001/auth/callback"; // Flask route
  const AUTH_ENDPOINT = "https://accounts.spotify.com/authorize";
  const RESPONSE_TYPE = "code";
  const SCOPES = "user-read-email";

  const loginUrl = `${AUTH_ENDPOINT}?client_id=${CLIENT_ID}&response_type=${RESPONSE_TYPE}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${SCOPES}`;

  return (
    <div>
      <a href={loginUrl}>
        <button>Login with Spotify</button>
      </a>
    </div>
  );
};

export default LoginButton;
