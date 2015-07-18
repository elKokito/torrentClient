import requests


class StrikeClient:

    def search(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query)
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        for item in res['torrents']:
            item['size'] = self._getSize(item['size'])
        return {'result': res['torrents']}

    def searchTV(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query + '&category=TV')
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        for item in res['torrents']:
            item['size'] = self._getSize(item['size'])
        return {'result': res['torrents']}

    def searchMovie(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query + '&category=Movies')
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        for item in res['torrents']:
            item['size'] = self._getSize(item['size'])
        return {'result': res['torrents']}

    def searchMusic(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query + '&category=Music')
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        for item in res['torrents']:
            item['size'] = self._getSize(item['size'])
        return {'result': res['torrents']}

    def _getSize(self, size):
        if size/(1000*1000) > 1000:
            return str(size/(1000*1000*1000)) + "Gb"
        else:
            return str(size/(1000*1000)) + "Mb"
