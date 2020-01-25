CREATE TABLE Genres (
genre_id INT UNSIGNED,
genre_name VARCHAR(100) NOT NULL,
PRIMARY KEY(genre_id)
);

CREATE TABLE Movies (
movie_id VARCHAR(100),
movie_name VARCHAR(100) NOT NULL,
PRIMARY KEY(movie_id)
);

CREATE TABLE Artists (
artist_id INT UNSIGNED,
artist_name VARCHAR(100) NOT NULL,
artist_type ENUM("Person", "Group", "Orchestra", "Choir", "Character", "Other"),
artist_rating TINYINT,
start_date DATE,
end_date DATE,
PRIMARY KEY (artist_id)
);

CREATE TABLE Albums (
album_id INT UNSIGNED,
album_name VARCHAR(100) NOT NULL,
release_date DATE,
artist_id INT UNSIGNED,
PRIMARY KEY (album_id),
FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);

CREATE TABLE Tracks (
track_id INT UNSIGNED,
track_name VARCHAR(100) NOT NULL,
track_rating TINYINT,
lyrics TEXT,
artist_id INT UNSIGNED,
PRIMARY KEY (track_id),
FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);

CREATE TABLE TracksGenres (
track_id INT UNSIGNED,
genre_id INT UNSIGNED,
PRIMARY KEY (track_id, genre_id),
FOREIGN KEY (track_id) REFERENCES Tracks(track_id),
FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE AlbumTracks (
track_id INT UNSIGNED,
album_id INT UNSIGNED,
PRIMARY KEY (track_id),
FOREIGN KEY (track_id) REFERENCES Tracks(track_id),
FOREIGN KEY (album_id) REFERENCES Albums(album_id)
);

CREATE TABLE MovieTracks (
track_id INT UNSIGNED,
movie_id VARCHAR(100),
PRIMARY KEY (track_id, movie_id),
FOREIGN KEY (track_id) REFERENCES Tracks(track_id),
FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);