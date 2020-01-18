get_random_row = """
SELECT * FROM `%s`
ORDER BY RAND()
LIMIT 1
"""


get_artist_name_by_id = """
SELECT artist_name
FROM Artists
WHERE artist_id = %s
"""

get_artist_last_album = """
SELECT Albums.album_name
FROM Albums, Artists, ArtistAlbums
WHERE Albums.album_id = ArtistAlbums.album_id
    AND ArtistAlbums.artist_id = Artists.artist_id
	AND Artists.artist_id = '%s'
	AND Albums.release_date >= ALL (SELECT AL.release_date
	                                FROM Albums AS AL, ArtistAlbums AS AA
	                                WHERE AL.album_id = AA.album_id
	                                AND AA.artist_id = Artists.artist_id)
"""

get_artist_albums = """
(SELECT albums.album_name 
 FROM   albums, 
        artists, 
        artistalbums 
 WHERE  albums.album_id = artistalbums.album_id 
        AND artistalbums.artist_id = artists.artist_id 
        AND artists.artist_id = '%s' 
        AND albums.release_date >= ALL (SELECT AL.release_date 
                                        FROM   albums AS AL, 
                                               artistalbums AS AA 
                                        WHERE  AL.album_id = AA.album_id 
                                               AND AA.artist_id = 
                                                   artists.artist_id)) 
UNION 
(SELECT albums.album_name 
 FROM   albums, 
        artists, 
        artistalbums 
 WHERE  albums.album_id = artistalbums.album_id 
        AND artistalbums.artist_id = artists.artist_id 
        AND artists.artist_id = '%s' 
        AND albums.release_date < (SELECT albums.release_date 
                                   FROM   albums, 
                                          artists, 
                                          artistalbums 
                                   WHERE  albums.album_id = 
                                          artistalbums.album_id 
                                          AND artistalbums.artist_id = 
                                              artists.artist_id 
                                          AND 
                artists.artist_id = '%s' 
                                          AND albums.release_date >= ALL 
                                              (SELECT AL.release_date 
                                               FROM   albums AS AL, 
                                                      artistalbums AS AA 
                                               WHERE  AL.album_id = AA.album_id 
                                                      AND AA.artist_id = 
                                                          artists.artist_id)) 
 LIMIT  3) 
 """

get_random_wrong_answers = """
SELECT `%s` FROM `%s`
WHERE %s != "%s"
LIMIT 3
"""

get_artist_with_more_albums_than_avg = """
(SELECT Artists.artist_name
     FROM Artists,
          ArtistAlbums
     WHERE ArtistAlbums.artist_id = Artists.artist_id
     GROUP BY Artists.artist_id
     HAVING COUNT(DISTINCT ArtistAlbums.album_id) >
         (SELECT AVG(nested.`count`)
          FROM
              (SELECT COUNT(DISTINCT album_id) AS `count`
               FROM ArtistAlbums
               GROUP BY artist_id) AS nested)
     ORDER BY RAND()
     LIMIT 1)
UNION
    (SELECT Artists.artist_name
     FROM Artists,
          ArtistAlbums
     WHERE ArtistAlbums.artist_id = Artists.artist_id
     GROUP BY Artists.artist_id
     HAVING COUNT(DISTINCT ArtistAlbums.album_id) <=
         (SELECT AVG(nested.`count`)
          FROM
              (SELECT COUNT(DISTINCT album_id) AS `count`
               FROM ArtistAlbums
               GROUP BY artist_id) AS nested)
     ORDER BY RAND()
     LIMIT 3)
"""

get_avg_tracks_for_artist_albums = """
SELECT AVG(tracks_count.num),
       tracks_count.artist_name
FROM
    (SELECT COUNT(AlbumTracks.track_id) AS num,
            rand_artist.artist_name AS artist_name
     FROM
         (SELECT artist_id,
                 artist_name
          FROM Artists
          ORDER BY RAND()
          LIMIT 1) AS rand_artist,
          ArtistAlbums,
          AlbumTracks
     WHERE ArtistAlbums.album_id = AlbumTracks.album_id
         AND rand_artist.artist_id = ArtistAlbums.artist_id
     GROUP BY ArtistAlbums.album_id) AS tracks_count
GROUP BY tracks_count.artist_name
"""

get_movie_with_most_played_tracks_in_genre = """
SELECT top_movie.movie_name,
       Movies.movie_name,
       top_movie.genre_name
FROM
    (SELECT Movies.movie_name,
            Movies.movie_id,
            rand_genre.genre_name
     FROM
         (SELECT genre_id AS genre_id,
                 genre_name AS genre_name
          FROM Genres
          ORDER BY RAND()
          LIMIT 1) AS rand_genre,
          MovieTracks,
          Tracks,
          TracksGenres,
          Movies
     WHERE MovieTracks.track_id = Tracks.track_id
         AND Tracks.track_id = TracksGenres.track_id
         AND rand_genre.genre_id = TracksGenres.genre_id
         AND Movies.movie_id = MovieTracks.movie_id
     GROUP BY MovieTracks.movie_id,
              rand_genre.genre_id
     ORDER BY COUNT(MovieTracks.track_id) DESC
     LIMIT 1) AS top_movie,
     Movies
WHERE Movies.movie_id != top_movie.movie_id
ORDER BY RAND()
LIMIT 3
"""