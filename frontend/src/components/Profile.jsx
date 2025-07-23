import React, { useEffect, useState } from "react";

const Profile = () => {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Not authenticated");
      return;
    }

    fetch("http://localhost:5001/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch user data");
        }
        return res.json();
      })
      .then((data) => setUser(data))
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div className="text-red-500 p-4">{error}</div>;

  if (!user) return <div>Loading profile...</div>;

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">My Profile</h1>
      <p><strong>Display Name:</strong> {user.display_name || "N/A"}</p>
      <p><strong>Email:</strong> {user.email || "N/A"}</p>
      <p><strong>Spotify ID:</strong> {user.spotify_id}</p>
    </div>
  );
};

export default Profile;
