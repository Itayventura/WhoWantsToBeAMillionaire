SELECT AVG(number_of_songs) AS average_songs_per_album
FROM(SELECT Albums.tracks_count AS number_of_songs
		FROM Albums, ArtistAlbums, Artists
		WHERE Albums.album_id = ArtistAlbums.album_id
			 AND ArtistAlbums.artist_id = Artists.artist_id
			 AND Artists.artist_name = 'U2'
		GROUP BY Albums.album_id) AS num_of_songs_table