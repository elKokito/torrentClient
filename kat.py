from bs4 import BeautifulSoup
import requests
import threading
from queue import Queue

SITE = "https://kickass.to"


class Kat:

    def __init__(self):
        r = requests.get(SITE)
        kat = BeautifulSoup(r.text)

        table = kat.findAll("table", "data")
        movies = table[0]
        series = table[1]
        self.movie = movies.findAll("tr")
        self.movie.pop(0)

        self.serie = series.findAll("tr")
        self.serie.pop(0)

        self.lock = threading.Lock()
        self.queue = None
        self.resultMovie = []
        self.resultSerie = []

    def movies(self):
        self.queue = Queue()
        self.resultMovie = []

        for i in range(len(self.movie)):
            t = threading.Thread(target=self.concatResultMovie)
            t.daemon = True
            t.start()

        for movie in self.movie:
            self.queue.put(movie)

        self.queue.join()
        return self.resultMovie

    def series(self):
        self.queue = Queue()
        self.resultSerie = []

        for i in range(len(self.serie)):
            t = threading.Thread(target=self.concatResultSerie)
            t.daemon = True
            t.start()

        for serie in self.serie:
            self.queue.put(serie)

        self.queue.join()
        return self.resultSerie

    def concatResultMovie(self):
        while True:
            item = self.queue.get()
            self._movies(item)
            self.queue.task_done()

    def concatResultSerie(self):
        while True:
            item = self.queue.get()
            self._series(item)
            self.queue.task_done()

    def _movies(self, entrie):

        try:
            info = {}
            info["title"] = entrie.find('a', class_="cellMainLink").text
            info["size"] = entrie.find("td", class_="nobr center").text
            info["seed"] = entrie.find("td", class_="green center").text
            info["magnet"] = self.getTorrentMagnet_(entrie.find('a', class_="cellMainLink").get("href"))

            with self.lock:
                self.resultMovie.append(info)
        except:
            pass

    def _series(self, entrie):

        try:
            info = {}
            info["title"] = entrie.find('a', class_="cellMainLink").text
            info["size"] = entrie.find("td", class_="nobr center").text
            info["seed"] = entrie.find("td", class_="green center").text
            info["magnet"] = self.getTorrentMagnet_(entrie.find('a', class_="cellMainLink").get("href"))
            with self.lock:
                self.resultSerie.append(info)

        except:
            pass

    def getTorrentMagnet_(self, link):
        torrent = requests.get(SITE + link)
        torrent = BeautifulSoup(torrent.text)
        torrent = torrent.find("a", class_="siteButton giantIcon magnetlinkButton").get("href")
        return torrent

    def search(self, query):
        r = requests.get(SITE + "/usearch/" + query + "/")
        dom = BeautifulSoup(r.text)
        table = dom.find("table", class_="data")
        row = table.findAll("tr")
        row.pop(0)

        result = []
        for entrie in row:
            info = {}
            info["magnet"] = entrie.find("a", class_="imagnet icon16").get("href")
            info["title"] = entrie.find("a", class_="cellMainLink").text
            info["size"] = entrie.find("td", class_="nobr center").text
            info["seed"] = entrie.find("td", class_="green center").text
            result.append(info)

        return result

    def refresh(self):
        r = requests.get(SITE)
        kat = BeautifulSoup(r.text)

        table = kat.findAll("table", "data")
        movies = table[0]
        series = table[1]
        self.movie = movies.findAll("tr")
        self.movie.pop(0)

        self.serie = series.findAll("tr")
        self.serie.pop(0)
