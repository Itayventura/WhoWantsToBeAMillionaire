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

get_random_wrong_answers = """
SELECT `%s` FROM `%s`
WHERE %s != "%s"
LIMIT 3
"""