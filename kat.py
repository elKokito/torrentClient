from pyquery import PyQuery as pq
import requests
import threading
from queue import Queue

SITE = "http://kat.cr"


class Kat:

    def __init__(self):
        r = requests.get(SITE)
        d = pq(r.content)
        movies = pq(d("div.mainpart table.doublecelltable table.data.frontPageWidget")[0])
        series = pq(d("div.mainpart table.doublecelltable table.data.frontPageWidget")[1])

        self.movie = list(movies.find(".odd"))
        self.movie.extend(movies.find(".even"))

        self.serie = list(series.find(".odd"))
        self.serie.extend(series.find(".even"))

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
            item = pq(entrie)
            info["title"] = item.find("a.cellMainLink").text()
            info["size"] = item.find("td.nobr.center").text()
            info["seed"] = item.find("td.green.center").text()
            info["magnet"] = self.getTorrentMagnet_(item.find("a.cellMainLink").attr("href"))

            with self.lock:
                self.resultMovie.append(info)
        except:
            pass

    def _series(self, entrie):

        try:
            info = {}
            item = pq(entrie)
            info["title"] = item.find("a.cellMainLink").text()
            info["size"] = item.find("td.nobr.center").text()
            info["seed"] = item.find("td.green.center").text()
            info["magnet"] = self.getTorrentMagnet_(item.find("a.cellMainLink").attr("href"))

            with self.lock:
                self.resultSerie.append(info)

        except:
            pass

    def getTorrentMagnet_(self, link):
        torrent = requests.get(SITE + link)
        torrent = pq(torrent.content)
        magnet = torrent.find(".kaGiantButton[title='Magnet link']").attr("href")
        return magnet

    def search(self, query):
        r = requests.get(SITE + "/usearch/" + query + "/")
        dom = pq(r.content)
        table = dom.find("table.data")
        row = table.find("tr")
        row.pop(0)

        result = []
        for entrie in row:
            info = {}
            entrie = pq(entrie)
            info["magnet"] = entrie.find("a[title='Torrent magnet link']").attr("href")
            info["title"] = entrie.find("a.cellMainLink").text()
            info["size"] = entrie.find("td.nobr.center").text()
            info["seed"] = entrie.find("td.green.center").text()
            result.append(info)

        return result

    def refresh(self):
        r = requests.get(SITE)
        d = pq(r.content)

        movies = pq(d("div.mainpart table.doublecelltable table.data.frontPageWidget")[0])
        series = pq(d("div.mainpart table.doublecelltable table.data.frontPageWidget")[1])
        self.movie = list(movies.find(".odd"))
        self.movie.extend(movies.find(".even"))
        self.serie = list(series.find(".odd"))
        self.serie.extend(series.find(".even"))
