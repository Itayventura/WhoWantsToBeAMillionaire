#Find all artists who played more albums than the average num of albums for an artist.
#Return their name, ordered by their name.

SELECT Artists.artist_name
FROM Albums, Artists, ArtistAlbums
WHERE Albums.album_id = ArtistAlbums.album_id 
	AND ArtistAlbums.artist_id = Artists.artist_id
GROUP BY Artists.artist_id 
HAVING COUNT(DISTINCT Albums.album_id) > ANY(SELECT AVG(`count`)
													  	 FROM (SELECT COUNT(distinct X.album_id) AS `count`
      														 FROM Albums AS X,  ArtistAlbums AS Y, Artists AS Z
																 WHERE X.album_id = Y.album_id
																 	AND Y.artist_id = Z.artist_id
																 GROUP BY Z.artist_id
    															 ) nested) 
ORDER BY Artists.artist_name