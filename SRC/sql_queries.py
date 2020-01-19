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

get_random_genre = """
SELECT * 
FROM Genres 
ORDER BY RAND() 
LIMIT 1
"""

get_artist_with_mainly_tracks_from_specific_genre = """
    (SELECT artist_name
     FROM Artists
     WHERE EXISTS
             (SELECT DISTINCT 1
              FROM
                  (SELECT ArtistTracks.artist_id,
                          COUNT(ArtistTracks.track_id) AS num
                   FROM TracksGenres,
                        ArtistTracks
                   WHERE ArtistTracks.track_id = TracksGenres.track_id
                       AND TracksGenres.genre_id = '%s'
                   GROUP BY ArtistTracks.artist_id) AS total_pop_count_for_artist,

                  (SELECT ArtistTracks.artist_id,
                          COUNT(ArtistTracks.track_id) AS num
                   FROM ArtistTracks
                   GROUP BY ArtistTracks.artist_id) AS total_tracks_count_for_artist
              WHERE Artists.artist_id = total_pop_count_for_artist.artist_id
                  AND total_pop_count_for_artist.artist_id = total_tracks_count_for_artist.artist_id
                  AND total_pop_count_for_artist.num > 0.5 * total_tracks_count_for_artist.num)
     ORDER BY RAND()
     LIMIT 1)
UNION
    (SELECT artist_name
     FROM Artists
     WHERE NOT EXISTS
             (SELECT DISTINCT 1
              FROM
                  (SELECT ArtistTracks.artist_id,
                          COUNT(ArtistTracks.track_id) AS num
                   FROM TracksGenres,
                        ArtistTracks
                   WHERE ArtistTracks.track_id = TracksGenres.track_id
                       AND TracksGenres.genre_id = '%s'
                   GROUP BY ArtistTracks.artist_id) AS total_pop_count_for_artist,

                  (SELECT ArtistTracks.artist_id,
                          COUNT(ArtistTracks.track_id) AS num
                   FROM ArtistTracks
                   GROUP BY ArtistTracks.artist_id) AS total_tracks_count_for_artist
              WHERE Artists.artist_id = total_pop_count_for_artist.artist_id
                  AND total_pop_count_for_artist.artist_id = total_tracks_count_for_artist.artist_id
                  AND total_pop_count_for_artist.num > 0.5 * total_tracks_count_for_artist.num)
     ORDER BY RAND()
     LIMIT 3)
"""

get_artist_with_album_released_in_specific_decade_with_love_song = """
    (SELECT Artists.artist_name
     FROM Artists
     WHERE artist_id = ANY
             (SELECT ArtistAlbums.artist_id
              FROM ArtistAlbums,
                   Albums
              WHERE ArtistAlbums.album_id = Albums.album_id
                  AND Albums.release_date >= %s
                  AND Albums.release_date < %s
                  AND Albums.album_id = ANY
                      (SELECT AlbumTracks.album_id
                       FROM AlbumTracks,
                            Tracks
                       WHERE AlbumTracks.track_id = Tracks.track_id
                           AND Tracks.lyrics LIKE '%love%'))
     ORDER BY RAND()
     LIMIT 1)
UNION
    (SELECT Artists.artist_name
     FROM Artists
     WHERE artist_id = ANY
             (SELECT ArtistAlbums.artist_id
              FROM ArtistAlbums,
                   Albums
              WHERE ArtistAlbums.album_id = Albums.album_id
                  AND Albums.release_date >= %s
                  AND Albums.release_date < %s
                  AND Albums.album_id != ANY
                      (SELECT AlbumTracks.album_id
                       FROM AlbumTracks,
                            Tracks
                       WHERE AlbumTracks.track_id = Tracks.track_id
                           AND Tracks.lyrics LIKE '%love%'))
     ORDER BY RAND()
     LIMIT 3)
"""