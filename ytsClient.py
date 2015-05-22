import requests


class ytsClient:

    def __init__(self):
        r = requests.get("https://yts.to/api/v2/list_movies.json?limit=50&sort_by=date_added")
        r2 = requests.get("https://yts.to/api/v2/list_upcoming.json")
        self.movieList = r.json()["data"]["movies"]
        self.upcoming = r2.json()["data"]["upcoming_movies"]

    def getMovieList(self):
        return self.movieList

    def getUpcoming(self):
        return self.upcoming

    def search(self, query):
        r = requests.get("https://yts.to/api/v2/list_movies.json?query_term=" + query + "&sort_by=seeds")
        return r.json()["data"]["movies"]

    def getMovieDetail(self, movieId):
        r = requests.get("https://yts.to/api/v2/movie_details.json?movie_id=" + movieId)
        return r.json()["data"]["movies"]

    def getSimilarMovies(self, movieId):
        r = requests.get("https://yts.to/api/v2/movie_suggestions.json?movie_id=" + movieId)
        return r.json()["data"]["movies"]

    def refresh(self):
        r = requests.get("https://yts.to/api/v2/list_movies.json?limit=50&sort_by=date_added")
        r2 = requests.get("https://yts.to/api/v2/list_upcoming.json")
        self.movieList = r.json()["data"]["movies"]
        self.upcoming = r2.json()["data"]["upcoming_movies"]

    def getMagnet(self, info):
        torrent_hash = info["hash"]
        dn = info["url"]
        tracker1 = "udp://open.demonii.com:1337"
        tracker2 = "udp://tracker.istole.it:80"
        tracker3 = "http://tracker.yify-torrents.com/announce"
        tracker4 = "udp://tracker.publicbt.com:80"
        tracker5 = "udp://tracker.openbittorrent.com:80"
        tracker6 = "udp://tracker.coppersurfer.tk:6969"
        tracker7 = "udp://exodus.desync.com:6969"
        tracker8 = "http://exodus.desync.com:6969/announce"

        return "magnet:?xt=urn:btih:" + torrent_hash + "&dn=" + dn + "&tr=" + tracker1 + "&tr=" + tracker2 \
            + "&tr=" + tracker3 + "&tr=" + tracker4 + "&tr=" + tracker5 + "&tr=" + tracker6 + "&tr=" + tracker7 \
            + "&tr=" + tracker8

    def query(self, query):
        pass
