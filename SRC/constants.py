""" database credentials """
DB_USERNAME = 'DbMysql02'
DB_PASSWORD = 'neworder'
# DB_HOST = 'mysqlsrv1.cs.tau.ac.il'
DB_HOST = '127.0.0.1'
DB_PORT = 3305  # 3306
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
QUESTION_ARTIST_WITH_MORE_ALBUMS_THAN_AVG = 'Which artist has more albums than the average?'
QUESTION_AVG_TRACKS_IN_ALBUM_FOR_ARTIST = 'What is the average tracks number in {artist}\'s albums?'
QUESTION_MOVIE_WITH_MOST_PLAYED_TRACKS_FROM_GENRE = 'What is the movie with the most played tracks from genre \'{genre}\'?'
QUESTION_ARTIST_WITH_MAINLY_TRACKS_FROM_SPECIFIC_GENRE = 'To which of the following artists most of their tracks are from genre {genre}?'
QUESTION_ARTIST_WITH_ALBUM_RELEASED_IN_SPECIFIC_DECADE_WITH_LOVE_SONG = 'Which of the following artists has an album released' \
                                                                        ' in the {decade}\'s that has a track which contains the word \'love\'?'
QUESTION_HIGHEST_RATED_ARTIST_WITHOUT_MOVIE_TRACKS = 'Which of the following is the highest rated artist that his tracks have not been played in any movie?'