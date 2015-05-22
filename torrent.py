#!/usr/bin/python3
import urwid
import libtorrent
import kat
import ytsClient

DOWNLOAD_PATH = "/home/koki/Downloads/"


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
        elif 'ctrl t' == key:
            self.loop.widget = self.torrent
        else:
            self.loop.widget = urwid.Filler(urwid.Text(repr(key)))


    def refresh(self, loop, *_args):
        self.loop.set_alarm_in(sec=1.0, callback=self.refresh, user_data=None)
        self.torrent.refresh()
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

    def __init__(self):
        self.search = urwid.Edit("Search-----> ")
        urwid.register_signal(SearchWidget, 'search')
        super(SearchWidget, self).__init__(urwid.SimpleFocusListWalker([self.search]))

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'search', self.search.get_edit_text())
        return urwid.ListBox.keypress(self, size, key)

    def result(self, result):
        pass


class KatWindow(urwid.ListBox):

    def __init__(self):
        self.kat = kat.Kat()
        self.search = SearchWidget()

        urwid.connect_signal(self.search, 'search', self.makeSearch)
        urwid.register_signal(KatWindow, 'addTorrent')

        movie = list(map(self.mapMovie, self.kat.movies()))
        serie = list(map(self.mapSerie, self.kat.series()))
        body = [urwid.Columns([urwid.Pile(movie), urwid.Pile(serie)]), urwid.BoxAdapter(self.search, 1)]
        super(KatWindow, self).__init__(urwid.SimpleFocusListWalker(body))

    def mapMovie(self, movie):
        c1 = urwid.Button(movie['title'], self.addTorrent, movie)
        c2 = urwid.Text(repr(movie['seed']))
        c3 = urwid.Text(repr(movie['size']))
        return urwid.Columns([c1, c2, c3])

    def mapSerie(self, serie):
        c1 = urwid.Button(serie['title'], self.addTorrent, serie)
        c2 = urwid.Text(repr(serie['seed']))
        c3 = urwid.Text(repr(serie['size']))
        return urwid.Columns([c1, c2, c3])

    def addTorrent(self, button, torrent):
        urwid.emit_signal(self, 'addTorrent', torrent)

    def makeSearch(self, search):
        return 0


class YtsWindow(urwid.ListBox):

    def __init__(self):
        self.tm = ytsClient.ytsClient()
        self.search = SearchWidget()

        urwid.connect_signal(self.search, 'search', self.makeSearch)
        urwid.register_signal(YtsWindow, 'addTorrent')

        body = list(map(self.mapMovie, self.tm.getMovieList()))
        body.append(urwid.BoxAdapter(self.search, 10))

        super(YtsWindow, self).__init__(urwid.SimpleFocusListWalker(body))

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
        pass


class TorrentWindow(urwid.ListBox):

    def __init__(self):
        self.torrent = []
        self.session = libtorrent.session()
        self.session.listen_on(6881, 6891)
        self.text = urwid.Text("debug")

        super(TorrentWindow, self).__init__(urwid.SimpleFocusListWalker([self.text]))

    def addTorrent(self, info):
        params = {"save_path": DOWNLOAD_PATH, "link": info["magnet"]}
        handle = libtorrent.add_magnet_uri(self.session, info["magnet"], params)
        pb = urwid.ProgressBar("pbNormal", "pbComplete")
        title = urwid.Text(repr(info["title"]))
        self.torrent.append((handle, pb))
        row = urwid.Columns([pb, title])
        self.body.append(row)

    def refresh(self):
        for (torrent, progressBar) in self.torrent:
            if torrent.has_metadata():
                if torrent.status().state != libtorrent.torrent_status.seeding:
                    progressBar.set_completion(torrent.status().progress * 100)

                if torrent.status().progress == 1:
                    progressBar.set_completion(100)
                    self.torrent.remove((torrent, progressBar))


window = MAIN(urwid.Filler(urwid.Text("watsup shinigan", 'center')))
window.run()
