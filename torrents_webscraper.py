from concurrent.futures import ProcessPoolExecutor
# use ThreadPoolExecutor for dev and debug
# ProcessPoolExecutor will deadlock in bpython (or any interpreter)

from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
from pyquery import PyQuery as pq
import time
import sys

def kat_parsing(body):
    results = []
    query = pq(body)
    query("div.mainpart table.doublecelltable table.data.frontPageWidget")
    movies = pq(query("div.mainpart table.doublecelltable table.data.frontPageWidget")[0])
    movies_list = list(movies.find(".odd"))
    movies_list.extend(movies.find(".even"))
    results = []
    for movie in movies_list:
        movie = pq(movie)
        title = movie("a.cellMainLink").text()
        size = movie("td[class='nobr center']").text()
        seed = movie("td[class='green center']").text()
        href = movie("a.cellMainLink").attr("href")
        results.append({
            "title": title,
            "size": size,
            "seed": seed,
            "href": href,
            "type": "movie"
            })


    series = pq(query("div.mainpart table.doublecelltable table.data.frontPageWidget")[1])
    series_list = list(series.find(".odd"))
    series_list.extend(series.find(".even"))
    for serie in series_list:
        serie = pq(serie)
        title = serie("a.cellMainLink").text()
        size = serie("td[class='nobr center']").text()
        seed = serie("td[class='green center']").text()
        href = serie("a.cellMainLink").attr("href")
        results.append({
            "title": title,
            "size": size,
            "seed": seed,
            "href": href,
            "type": "serie"
            })

    return results

def pirate_bay_parsing(body):
    query = pq(body)
    tbody = query("table#searchResult")[0]
    rows = pq(tbody)
    rows = rows("tr")
    rows.pop(0)

    results = []

    for row in rows:
        entrie = pq(row)
        title = entrie("a.detLink").attr("title")
        magnet = entrie("a[title='Download this torrent using magnet']").attr("href")
        info = entrie("font.detDesc").text()
        seeds = entrie("td[align='right']")[0].text
        results.append({"title": title,
                        "magnet": magnet,
                        "info": info,
                        "seeds": seeds})
    return results

class TorrentGetter:

    def __init__(self):
        self.last_update = time.time()
        self.executor = PoolExecutor()
        self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self.loop)

        self.default_tasks = [
                # pirate bay tv shows
                ("https://thepiratebay.se/top/208", self._pipeline_piratebay),
                # pirate bay movies
                ("https://thepiratebay.se/top/207", self._pipeline_piratebay),
                # kickasstorrent all
                ("http://kickasstorrentsim.com/", self._pipeline_kat)
                ]
        self.torrents = self._launch_scrapping(self.default_tasks)

    def force_update(self):
        self.executor = PoolExecutor()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.last_update = time.time()
        self._launch_scrapping(self.default_tasks)

    def get_all_torrents(self):
        self._update_if_needed()
        return self.torrents

    def get_movies(self):
        self._update_if_needed()
        res = []
        for torrent in self.torrents:
            if torrent != None and 'type' in torrent:
                if torrent['type'] == 'movie':
                    res.append(torrent)
            else:
                res.append(torrent)
        return res

    def get_series(self):
        self._update_if_needed()
        res = []
        for torrent in self.torrents:
            if torrent != None and 'type' in 'torrent':
                if torrent['type'] == 'serie':
                    res.append(torrent)
            else:
                res.append(torrent)
        return res

    def search(self, query):
        self.executor = PoolExecutor()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        tasks = [
                # ('http://kickasstorrentsim.com/usearch/' + query, self._pipekat),
                ('https://thepiratebay.org/search/' + query, self._pipeline_piratebay)
                ]
        return self._launch_scrapping(tasks)

    def _update_if_needed(self):
        if time.time() - self.last_update > 60*60:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.executor = PoolExecutor()
            new_torrents = self._launch_scrapping(self.default_tasks)
            if new_torrents != []:
                self.torrents = new_torrents
            self.last_update = time.time()


    async def _kat_torrent(self, base_url, obj):
        body = await aiohttp.get(base_url + obj['href'])
        body = await body.text()
        body = pq(body)
        magnet = body("a.kaGiantButton[title='Magnet link']").attr("href")
        obj.update({"magnet": magnet})

    async def _pipeline_piratebay(self, url):
        body = await aiohttp.get(url)
        body = await body.text()
        result = await self.loop.run_in_executor(self.executor, pirate_bay_parsing, body)
        return result

    async def _pipeline_kat(self, url):
        body = await aiohttp.get(url)
        body = await body.text()
        result = await self.loop.run_in_executor(self.executor, kat_parsing, body)
        await asyncio.gather(*[self._kat_torrent(url, obj) for obj in result])

        return result

    def _launch_scrapping(self, tasks):
        try:
            results = self.loop.run_until_complete(asyncio.gather(*[func(url) for (url, func) in tasks]))
            return results[0]
        except:
            print('error occured in torrent webscrapper')
            print(sys.exc_info()[0])

if __name__ == "__main__":
    PoolExecutor = ProcessPoolExecutor
    # t = TorrentGetter()
    # print(t.torrents)
elif __name__ == "__console__":
    PoolExecutor = ThreadPoolExecutor
else:
    PoolExecutor = ProcessPoolExecutor
