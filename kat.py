from bs4 import BeautifulSoup
import requests

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

	def movies(self):

		result = []
		for entrie in self.movie:
			info = {}
			info["name"] = entrie.find('a', class_="cellMainLink").text
			info["size"] = entrie.find("td", class_="nobr center").text
			info["seed"] = entrie.find("td", class_="green center").text
			info["magnet"] = self.getTorrentMagnet_(entrie.find('a', class_="cellMainLink").get("href"))
			result.append(info)

		return result
		
	def series(self):

		result = []
		for entrie in self.serie:
			info = {}
			info["name"] = entrie.find('a', class_="cellMainLink").text
			info["size"] = entrie.find("td", class_="nobr center").text
			info["seed"] = entrie.find("td", class_="green center").text
			info["magnet"] = self.getTorrentMagnet_(entrie.find('a', class_="cellMainLink").get("href"))
			result.append(info)

		return result

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
			info["magnet"]  = entrie.find("a", class_="imagnet icon16").get("href")
			info["name"] 	= entrie.find("a", class_="cellMainLink").text
			info["size"] 	= entrie.find("td", class_="nobr center").text
			info["seed"]	= entrie.find("td", class_="green center").text
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