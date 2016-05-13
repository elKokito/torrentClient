from concurrent.futures import ProcessPoolExecutor
import asyncio
import aiohttp
from pyquery import PyQuery as pq
import time

# global executor and loop
executor = ProcessPoolExecutor()
loop = asyncio.get_event_loop()

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


def kat_parsing(body):
    query = pq(body)
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


async def kat_torrent(base_url, obj: dict):
    body = await aiohttp.get(base_url + obj['href'])
    body = await body.text()
    body = pq(body)
    magnet = body("a.kaGiantButton[title='Magnet link']").attr("href")
    obj.update({"magnet": magnet})

async def pipeline_piratebay(url):
    body = await aiohttp.get(url)
    body = await body.text()
    result = await loop.run_in_executor(executor, pirate_bay_parsing, body)
    return result

async def pipeline_kat(url):
    body = await aiohttp.get(url)
    body = await body.text()
    result = await loop.run_in_executor(executor, kat_parsing, body)
    await asyncio.gather(*[kat_torrent(url, obj) for obj in result])

    return result

def launch_scapping():
    tasks = [
            # pirate bay tv shows
            ("https://thepiratebay.se/top/208", pipeline_piratebay),
            # pirate bay movies
            ("https://thepiratebay.se/top/207", pipeline_piratebay),
            # kickasstorrent all
            ("http://kickasstorrentsim.com/", pipeline_kat)
            ]
    results = loop.run_until_complete(asyncio.gather(*[func(url) for (url, func) in tasks]))
    return results

class TorrentGetter:

    def __init__(self):
        self.last_update = time.time()
        self.torrents = launch_scapping()

    def _update_if_needed(self):
        if time.time() - self.last_update > 60*60:
            self.torrents = launch_scapping()
            self.last_update = time.time()

        def force_update(self):
            self.torrents = launch_scapping
        self.last_update = time.time()

    def get_all_torrents(self):
        self._update_if_needed()
        return self.torrents

    def get_movies(self):
        self._update_if_needed()
        res = self.torrents[1]
        for torrent in self.torrents[2]:
            if torrent['type'] == 'movie':
                res.append(torrent)
        return res

    def get_series(self):
        self._update_if_needed()
        res = self.torrents[0]
        for torrent in self.torrents[2]:
            if torrent['type'] == 'serie':
                res.append(torrent)
        return res
