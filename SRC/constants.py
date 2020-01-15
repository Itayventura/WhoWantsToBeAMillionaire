""" database credentials """
DB_USERNAME = 'DbMysql02'
DB_PASSWORD = 'neworder'
DB_HOST = 'mysqlsrv1.cs.tau.ac.il'
#DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'DbMysql02'

""" entities tables """
TRACKS = 'Tracks'
ALBUMS = 'Albums'
ARTISTS = 'Artists'
MOVIES = 'Movies'
GENRES = 'Genres'

""" ER tables """
ALBUM_TRACKS = 'AlbumTracks'
ARTIST_ALBUMS = 'ArtistAlbums'
ARTIST_TRACKS = 'ArtistTracks'
MOVIE_TRACKS = 'MovieTracks'
TRACKS_GENRES = 'TracksGenres'

MUSIXMATCH_URL = 'https://api.musixmatch.com/ws/1.1'
MUSIXMATCH_API_KEY = 'f1ed26e2ca739a996575ce0465ecc571'

MUSICBRAINZ_URL = 'http://musicbrainz.org/ws/2'

GENIUS_URL = 'https://api.genius.com'
GENIUS_API_KEY = 'JcdMNbQcAaiRz00B_YjtDUSCfm-NGAtwfae_WI-KfWvUpf6ZozUhYFlVFpGkE6LP'

TUNEFIND_URL = 'https://www.tunefind.com'

""" QUESTIONS """
QUESTION_LAST_ALBUM = 'What is {artist}\'s last album?'
