########### get me all songs that was released in the same date as other songs in the same genre #######
######### my comment - there is not intersect in mysql. this is the way of doing intersect ##########

SELECT X.track_name
FROM Tracks AS X, Artists AS Y, TracksGenres AS TG, Albums AS Z
WHERE X.artist_id = Y.artist_id
	AND X.track_id = TG.track_id
	AND X.album_id = Z.album_id
	AND EXISTS(SELECT *
				FROM Albums AS A, TracksGenres AS B
				WHERE B.genre_id = TG.genre_id
				AND Z.release_date = A.release_date
				AND B.track_id <> TG.track_id)