CREATE TABLE IF NOT EXISTS playlists (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  last_accessed TIMESTAMPTZ
);

INSERT INTO playlists (id, name) VALUES 
('7wPNQbWwFH3vNXrWQyuRxT', 'para ti'),
('4O16iGSENRFnw3XvQkn6nA', 'Vinilo International True Hits'),
('1LHpQPcRyplY2NbJHcfoV7', 'Pop Hits 2025 | Top & Rising Stars'),
('32YBOPBNc2Ywhp2qLDeuZu', 'Dark pop x afterparty'),
('0QWvkN6kWZF2Va4OK5pGKX', 'Alt Pop Innovators');
