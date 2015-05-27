#!/usr/bin/python3
import urwid
import kat
import ytsClient
import strikeClient
import zmq
import json


class MAIN():
    def __init__(self, widget):
        palette = [("search",        "", "", "", "#ff0", "g27"),
                   ("button",      "", "", "", "#df6", "#006"),
                   ("div",         "", "", "", "#666", "g19"),
                   ("torrent",     "", "", "", "#008", "#ff8"),
                   ("pbNormal",    "", "", "", "g19", "#fa6"),
                   ("pbComplete",  "", "", "", "g58", "g27"),
                   ("bg",          "", "", "", "#a88", "g15")]
        self.widget = widget
        self.loop = urwid.MainLoop(self.widget, palette=palette, unhandled_input=self.input_filter)
        self.loop.screen.set_terminal_properties(colors=256)
        self.kat = None
        self.yts = None
        self.strike = None
        self.torrent = TorrentWindow()
        self.loop.set_alarm_in(1.0, self.refresh)

    def input_filter(self, key):
        if 'esc' is key:
            raise urwid.ExitMainLoop()
        elif 'ctrl k' == key:
            if not self.kat:
                self.kat = KatWindow()
                urwid.connect_signal(self.kat, 'addTorrent', self.addTorrent)
            self.loop.widget = self.kat
        elif 'ctrl y' == key:
            if not self.yts:
                self.yts = YtsWindow()
                urwid.connect_signal(self.yts, 'addTorrent', self.addTorrent)
            self.loop.widget = self.yts
        elif 'ctrl w' == key:
            if not self.strike:
                self.strike = StrikeWindow()
                urwid.connect_signal(self.strike, 'addTorrent', self.addTorrent)
            self.loop.widget = self.strike
        elif 'ctrl t' == key:
            self.loop.widget = self.torrent
            self.loop.set_alarm_in(0.1, self.refresh)
#        else:
#            self.loop.widget = urwid.Filler(urwid.Text(repr(key), 'center'))

    def refresh(self, loop, *_args):
        if isinstance(self.loop.widget, TorrentWindow):
            self.loop.set_alarm_in(sec=1.0, callback=self.refresh, user_data=None)
            self.loop.widget.refresh()
            self.loop.draw_screen()

    def addTorrent(self, torrent):
        self.torrent.addTorrent(torrent)

    def run(self):
        self.loop.run()


class Search(urwid.Edit):

    def __init__(self, text):
        super(Search, self).__init__(text)

    def keypress(self, size, key):
        if key == "enter":
            urwid.emit_signal(self, "search", self.get_edit_text())
        return urwid.Edit.keypress(self, size, key)


class SearchWidget(urwid.ListBox):

    def __init__(self, msg='Search-----> '):
        self.search = urwid.Edit(msg)
        urwid.register_signal(SearchWidget, 'search')
        super(SearchWidget, self).__init__(urwid.SimpleFocusListWalker([self.search]))

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'search', self.search.get_edit_text())
        return urwid.ListBox.keypress(self, size, key)

    def result(self, result):
        pass


class StrikeWindow(urwid.ListBox):

    def __init__(self):
        self.st = strikeClient.StrikeClient()
        urwid.register_signal(StrikeWindow, 'addTorrent')
        body = self.initializeView()
        super(StrikeWindow, self).__init__(urwid.SimpleFocusListWalker(body))

    def initializeView(self):
        search = SearchWidget('Search anything----> ')
        urwid.connect_signal(search, 'search', self._search)
        searchTV = SearchWidget('Search TV----> ')
        urwid.connect_signal(searchTV, 'search', self._searchTV)
        searchMovie = SearchWidget('Search Movie----> ')
        urwid.connect_signal(searchMovie, 'search', self._searchMovie)
        searchMusic = SearchWidget('Search Music----> ')
        urwid.connect_signal(searchMusic, 'search', self._searchMusic)
        return [urwid.BoxAdapter(search, 5),
                urwid.BoxAdapter(searchTV, 5),
                urwid.BoxAdapter(searchMovie, 5),
                urwid.BoxAdapter(searchMusic, 5)]

    def _search(self, query):
        res = self.st.search(query)
        if not res['result']:
            self.showResult(urwid.Text('nothing found', 'center'))
        else:
            body = list(map(self.makeResultList, res['result']))
            self.showResult(urwid.Pile(body))
        self.body.append(urwid.Text(repr(query)))

    def _searchTV(self, query):
        res = self.st.searchTV(query)
        if not res['result']:
            self.showResult(urwid.Text('nothing found', 'center'))
        else:
            body = list(map(self.makeResultList, res['result']))
            self.showResult(urwid.Pile(body))
        self.body.append(urwid.Text(repr(query)))

    def _searchMovie(self, query):
        res = self.st.searchMovie(query)
        if not res['result']:
            self.showResult(urwid.Text('nothing found', 'center'))
        else:
            body = list(map(self.makeResultList, res['result']))
            self.showResult(urwid.Pile(body))
        self.body.append(urwid.Text(repr(query)))

    def _searchMusic(self, query):
        res = self.st.searchMusic(query)
        if not res['result']:
            self.showResult(urwid.Text('nothing found', 'center'))
        else:
            body = list(map(self.makeResultList, res['result']))
            self.showResult(urwid.Pile(body))
        self.body.append(urwid.Text(repr(query)))

    def showResult(self, widget):
        self.body.clear()
        self.body.append(widget)

    def makeResultList(self, torrent):
        title = urwid.Button(repr(torrent['torrent_title']), self.addTorrent, {'title': torrent['torrent_title'],
                                                                               'magnet': torrent['magnet_uri']})
        size = urwid.Text(repr(torrent['size']), 'center')
        seed = urwid.Text(repr(torrent['seeds']), 'center')
        return urwid.Columns([title, size, seed])

    def addTorrent(self, button, info):
        urwid.emit_signal(self, 'addTorrent', info)

    def keypress(self, size, key):
        if 'tab' == key:
            self.body.clear()
            self.body.append(urwid.Pile(self.initializeView()))
        else:
            return urwid.ListBox.keypress(self, size, key)


class KatWindow(urwid.ListBox):

    def __init__(self):
        self.kat = kat.Kat()
        self.search = SearchWidget()

        urwid.connect_signal(self.search, 'search', self.makeSearch)
        urwid.register_signal(KatWindow, 'addTorrent')

        body = self.initializeView()
        super(KatWindow, self).__init__(urwid.SimpleFocusListWalker(body))

    def initializeView(self):
        movie = list(map(self.mapTorrent, self.kat.movies()))
        serie = list(map(self.mapTorrent, self.kat.series()))
        body = [urwid.Columns([urwid.Pile(movie), urwid.Pile(serie)]), urwid.BoxAdapter(self.search, 1)]
        return body

    def mapTorrent(self, movie):
        c1 = urwid.Button(movie['title'], self.addTorrent, movie)
        c2 = urwid.Text(repr(movie['seed']))
        c3 = urwid.Text(repr(movie['size']))
        return urwid.Columns([c1, c2, c3])

    def addTorrent(self, button, torrent):
        urwid.emit_signal(self, 'addTorrent', torrent)

    def makeSearch(self, search):
        res = self.kat.search(search)
        res = list(map(self.mapTorrent, res))
        self.body.clear()
        self.body.extend(self.initializeView())
        self.body.append(urwid.Pile(res))

    def keypress(self, size, key):
        if key is 'ctrl r':
            self.kat.refresh()
            self.body.clear()
            self.body.extend(self.initializeView())
        else:
            return urwid.ListBox.keypress(self, size, key)


class YtsWindow(urwid.ListBox):

    def __init__(self):
        self.tm = ytsClient.ytsClient()
        self.search = SearchWidget()

        urwid.connect_signal(self.search, 'search', self.makeSearch)
        urwid.register_signal(YtsWindow, 'addTorrent')

        body = self.initializeView()
        super(YtsWindow, self).__init__(urwid.SimpleFocusListWalker(body))

    def initializeView(self):
        body = list(map(self.mapMovie, self.tm.getMovieList()))
        body.append(urwid.BoxAdapter(self.search, 1))
        return body

    def mapMovie(self, movie):
        c1 = urwid.Text(repr(movie["title_long"]))
        c2 = urwid.Text(repr(movie["date_uploaded"]))

        seed = max(movie["torrents"], key=lambda x: x["seeds"])
        c3 = urwid.Text(repr(seed["seeds"]), 'center')
        c4 = urwid.Text(repr(seed["size"]))
        buttonS = urwid.Button("seed", self.addTorrent, {"movie": movie, "torrent": seed})

        quality = max(movie["torrents"], key=lambda x: x["size_bytes"])
        c5 = urwid.Text(repr(quality["seeds"]), 'center')
        c6 = urwid.Text(repr(quality["size"]))
        buttonQ = urwid.Button("quality", self.addTorrent, {"movie": movie, "torrent": quality})
        return urwid.Columns([(50, c1), (30, c2), (8, buttonS), (15, c3), (15, c4), (11, buttonQ), (15, c5), (15, c6)])

    def addTorrent(self, button, torrent):
        info = {"title": torrent["movie"]["title"],
                "magnet": self.tm.getMagnet(torrent["torrent"])}
        urwid.emit_signal(self, 'addTorrent', info)

    def makeSearch(self, search):
        res = self.tm.search(search)
        if len(res) > 0:
            res = list(map(self.mapMovie, res))
            res = urwid.Pile(res)
        else:
            res = urwid.Text('nothing found')
        self.body.clear()
        self.body.extend(self.initializeView())
        self.body.append(res)

    def keypress(self, size, key):
        if key is 'ctrl r':
            self.tm.refresh()
            self.body.clear()
            self.body.extend(self.initializeView())
        else:
            return urwid.ListBox.keypress(self, size, key)


class TorrentWindow(urwid.ListBox):

    def __init__(self):
        self.torrent = []

        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("ipc:///tmp/zmq")
        msg = json.dumps({'call': "getList"})
        self.socket.send_string(msg)
        torrents = self.socket.recv_string()
        torrents = json.loads(torrents)
        body = self.initializeView(torrents)

        super(TorrentWindow, self).__init__(urwid.SimpleFocusListWalker(body))

    def initializeView(self, torrents):
        body = []
        for torrent in torrents:
            title = urwid.Text(repr(torrent[0]))
            progressBar = urwid.ProgressBar("pbNormal", "pbComplete")
            self.torrent.append((torrent[0], progressBar))
            body.append(urwid.Columns([progressBar, title]))
        return body

    def addTorrent(self, info):
        msg = {"call": "addTorrent", "torrent": info}
        msg = json.dumps(msg)
        self.socket.send_string(msg)
        self.socket.recv_string()

        pb = urwid.ProgressBar("pbNormal", "pbComplete")
        title = urwid.Text(repr(info["title"]))
        self.torrent.append((info["title"], pb))
        row = urwid.Columns([pb, title])
        self.body.append(row)

    def refresh(self):
        for (title, progressBar) in self.torrent:
            msg = {"call": "getTorrent", "info": title}
            self.socket.send_string(json.dumps(msg))
            msg = json.loads(self.socket.recv_string())
            if msg["res"] == 1:
                progressBar.set_completion(100)
            else:
                progressBar.set_completion(msg["res"] * 100)

    def keypress(self, size, key):
        if key == 'r':
            self.refresh()
        else:
            return urwid.ListBox.keypress(self, size, key)


window = MAIN(urwid.Filler(urwid.Text("watsup shinigan", 'center')))
window.run()
