import requests


class StrikeClient:

    def search(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query)
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        return {'result': res['torrents']}

    def searchTV(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query + '&category=TV')
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        return {'result': res['torrents']}

    def searchMovie(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query + '&category=Movies')
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        return {'result': res['torrents']}

    def searchMusic(self, query):
        query = query.replace(' ', '+')
        res = requests.get('http://getstrike.net/api/v2/torrents/search/?phrase=' + query + '&category=Music')
        res = res.json()
        if res['statuscode'] == 404:
            return {'result': None}
        res['torrents'].sort(key=lambda t: t['seeds'], reverse=True)
        return {'result': res['torrents']}
