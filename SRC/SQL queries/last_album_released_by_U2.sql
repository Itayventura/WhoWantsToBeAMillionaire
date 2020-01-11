########### get me the last album released by U2 ###################

SELECT Albums.album_name
FROM Albums, Artists, ArtistAlbums
WHERE Albums.album_id = ArtistAlbums.album_id
	AND ArtistAlbums.artist_id = Artists.artist_id
	AND Artists.artist_name = 'U2'
	AND Albums.release_date >= ALL (SELECT AL.release_date
										FROM Albums AS AL, ArtistAlbums AS AA
										WHERE AL.album_id = AA.album_id
												AND AA.artist_id = Artists.artist_id)