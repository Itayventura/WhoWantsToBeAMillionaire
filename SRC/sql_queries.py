'''------------------------COMPLEX QUERIES-------------------------'''

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
                           AND MATCH (lyrics) AGAINST ('Love' IN NATURAL LANGUAGE MODE)))
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
                           AND MATCH (lyrics) AGAINST ('Love' IN NATURAL LANGUAGE MODE)))
     ORDER BY RAND()
     LIMIT 3)
"""

get_highest_rated_artist_without_movie_tracks = """
SELECT *
FROM
    (SELECT artist_rating,

         (SELECT artist_name
          FROM Artists
          WHERE NOT EXISTS
                  (SELECT 1
                   FROM MovieTracks,
                        ArtistTracks
                   WHERE Artists.artist_id = ArtistTracks.artist_id
                       AND MovieTracks.track_id = ArtistTracks.track_id)
              AND Artists.artist_rating = ratings.artist_rating
          ORDER BY rand()
          LIMIT 1) AS artist_name
     FROM
         (SELECT DISTINCT artist_rating
          FROM Artists) AS ratings
     ORDER BY rand()
     LIMIT 4) AS random_artists
ORDER BY artist_rating DESC
"""

'''------------------------SIMPLE QUERIES-------------------------'''

get_random_track_lyrics = """
SELECT Tracks.track_name, Artists.artist_name, Tracks.lyrics
FROM Tracks, Artists, ArtistTracks
WHERE Tracks.lyrics IS NOT NULL
AND Tracks.lyrics != '(instumental)'
AND Tracks.track_id = ArtistTracks.track_id
AND ArtistTracks.artist_id = Artists.artist_id
ORDER BY RAND()
LIMIT 1
"""

get_the_most_rated_artist = """
SELECT correct_artist.artist_name,
       Artists.artist_name
FROM
    (SELECT Artists.artist_name,
            Artists.artist_rating
     FROM Artists
     ORDER BY RAND()
     LIMIT 1) AS correct_artist,
     Artists
WHERE Artists.artist_rating < correct_artist.artist_rating
ORDER BY RAND()
LIMIT 3
"""

get_first_released_album_out_of_four = """
SELECT correct_album.album_name,
       Albums.album_name
FROM
    (SELECT Albums.album_name,
            Albums.release_date
     FROM Albums
     ORDER BY RAND()
     LIMIT 1) AS correct_album,
     Albums
WHERE Albums.release_date > correct_album.release_date
ORDER BY RAND()
LIMIT 3
"""

get_track_in_movie = """
SELECT answer.movie_name,
       answer.track_name,
       Tracks.track_name
FROM
    (SELECT Tracks.track_name,
            Movies.movie_name,
            Movies.movie_id
     FROM Tracks,
          MovieTracks,
          Movies
     WHERE Tracks.track_id = MovieTracks.track_id
         AND MovieTracks.movie_id = Movies.movie_id
     ORDER BY RAND()
     LIMIT 1) AS answer,
     Tracks,
     MovieTracks
WHERE Tracks.track_id = MovieTracks.track_id
    AND MovieTracks.movie_id != answer.movie_id
ORDER BY RAND()
LIMIT 3
"""

get_movie_without_track = """
SELECT Tracks.track_name,
       answer.movie_name,
       Movies.movie_name
FROM
    (SELECT played_track.track_id,
            Movies.movie_name
     FROM
         (SELECT MovieTracks.track_id
          FROM MovieTracks
          GROUP BY MovieTracks.track_id
          HAVING COUNT(*) >= 3
          ORDER BY RAND()
          LIMIT 1) played_track,
          MovieTracks,
          Movies
     WHERE MovieTracks.movie_id = Movies.movie_id
         AND MovieTracks.track_id != played_track.track_id
     ORDER BY RAND()
     LIMIT 1) AS answer,
     Movies,
     MovieTracks,
     Tracks
WHERE MovieTracks.track_id = answer.track_id
    AND Movies.movie_id = MovieTracks.movie_id
    AND Tracks.track_id = answer.track_id
ORDER BY RAND()
LIMIT 3
"""

get_track_of_specific_artist = """
SELECT answer.track_name,
       answer.artist_name,
       Tracks.track_name
FROM
    (SELECT Tracks.track_name,
            Artists.artist_name,
            ArtistTracks.artist_id
     FROM Tracks,
          Artists,
          ArtistTracks
     WHERE Artists.artist_id = ArtistTracks.artist_id
     AND ArtistTracks.track_id = Tracks.track_id
     ORDER BY RAND()
     LIMIT 1) answer,
     Tracks,
     ArtistTracks
WHERE ArtistTracks.artist_id != answer.artist_id
AND ArtistTracks.track_id = Tracks.track_id
ORDER BY RAND()
LIMIT 3
"""

get_year_of_birth_of_specific_artist = """
SELECT Artists.artist_name,
       Artists.start_date
FROM Artists
WHERE Artists.artist_type = 'Person'
ORDER BY RAND()
LIMIT 1
"""

'''------------------------full text query-------------------------'''

get_song_that_contain_a_word_from_list_of_words = """
(SELECT track_name
FROM Tracks
WHERE MATCH (lyrics) AGAINST ('%s' IN NATURAL LANGUAGE MODE)
ORDER BY RAND()
LIMIT 1)

UNION 

(SELECT track_name
FROM Tracks
WHERE track_name
  not in (SELECT track_name
            FROM Tracks
            WHERE MATCH (lyrics) AGAINST ('%s' IN NATURAL LANGUAGE MODE))
ORDER BY RAND()
LIMIT 3)
"""