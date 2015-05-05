#!/usr/bin/python3
import urwid as ur
import os
import libtorrent
import kat
import time

DOWNLOAD_PATH = "/home/koki/Downloads/"

class MAIN():
    def __init__(self, widget):
        palette = [
                    ("search",        "", "", "", "#ff0", "g27"),
                    ("button",      "", "", "", "#df6", "#006"),
                    ("div",         "", "", "", "#666", "g19"),
                    ("torrent",     "", "", "", "#008", "#ff8"),
                    ("pbNormal",    "", "", "", "g19", "#fa6"),
                    ("pbComplete",  "", "", "", "g58", "g27"),
                    ("bg",          "", "", "", "#a88", "g15")
                  ]
        self.widget = widget
        self.loop = ur.MainLoop(self.widget, palette=palette, unhandled_input=self.input_filter)
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.set_alarm_in(1.0,self.refresh)

    def input_filter(self, key):
        if 'esc' in key:
            raise ur.ExitMainLoop()

    def refresh(self, loop, *_args):
        loop.set_alarm_in(sec=1.0, callback=self.refresh, user_data=None)
        self.widget.refresh()
        self.loop.draw_screen()

    def run(self):
        self.loop.run()


class torrentWindow(ur.Pile):

    def __init__(self):
        self.kat_ = kat.Kat()
        self.session = libtorrent.session()
        self.session.listen_on(6881, 6891)
        self.handle = []

        self.moviesList = ListTorrent(self.kat_.movies(), self.addTorrent)
        self.seriesList = ListTorrent(self.kat_.series(), self.addTorrent)
        m = ur.BoxAdapter(self.moviesList, 10)
        s = ur.BoxAdapter(self.seriesList, 10)

        self.searchBox = ur.BoxAdapter(ListTorrent([], self.addTorrent),20)
        self.downloadTorrent = ur.BoxAdapter(DownloadTorrent(), 10)

        self.newStuff = ur.Columns([m, s], 1)
        search_ = Search(("search --> "))
        ur.connect_signal(search_, "search", self.search)
        
        self.time = ur.Text(time.strftime("%d/%m/%Y %H:%M:%S"))

        
        super(torrentWindow, self).__init__([
                                                ur.AttrMap(self.time, "search"),
                                                ur.AttrMap(ur.Divider(), "div"),
                                                self.newStuff, 
                                                ur.AttrMap(ur.Divider(), "div"),
                                                ur.AttrMap(search_, "search"), 
                                                ur.AttrMap(ur.Divider(), "div"),
                                                self.searchBox, 
                                                ur.AttrMap(ur.Divider(), "div"), 
                                                self.downloadTorrent])


    def addTorrent(self, button, magnet):

        params = {"save_path": DOWNLOAD_PATH, "link": magnet}
        handle = libtorrent.add_magnet_uri(self.session, magnet, params)
        self.downloadTorrent.original_widget.add(handle)

    def search(self, request):

        result = self.kat_.search(request)
        self.searchBox.original_widget = ListTorrent(result, self.addTorrent)

    def keypress(self, size, key):
        if key == "f5":
            self.kat_.refresh()
            moviesList = ListTorrent(self.kat_.movies(), self.addTorrent)
            seriesList = ListTorrent(self.kat_.series(), self.addTorrent)
            m = ur.BoxAdapter(moviesList, 10)
            s = ur.BoxAdapter(seriesList, 10)
            index = self.widget_list.index(self.newStuff)
            self.widget_list.remove(self.newStuff)
            self.newStuff = ur.Columns([m, s], 1)
            self.widget_list.insert(index, self.newStuff)
            self.time.set_text(time.strftime("%d/%m/%Y %H:%M:%S"))
        return ur.Pile.keypress(self, size, key)

    def refresh(self):
        self.downloadTorrent.original_widget.refresh()

class Search(ur.Edit):

    def __init__(self, text):
        ur.register_signal(Search, ["search"])
        super(Search, self).__init__(text)

    def keypress(self, size, key):
        if key == "enter":
            ur.emit_signal(self, "search", self.get_edit_text())
        return ur.Edit.keypress(self, size, key)


class ListTorrent(ur.ListBox):

    def __init__(self, liste, callback):
        
        display = []
        for t in liste:
            label = t["name"] + " " + t["size"] + " " + t["seed"]
            button = ur.Button(label, callback, t["magnet"])
            put = ur.AttrMap(button, "button")
            display.append(put)

        super(ListTorrent, self).__init__(ur.SimpleFocusListWalker(display))


class DownloadTorrent(ur.ListBox):

    def __init__(self):
        self.torrent = []
        super(DownloadTorrent, self).__init__(ur.SimpleFocusListWalker([]))

    def add(self, torrent):
        pb = ur.ProgressBar("pbNormal", "pbComplete")
        title = ur.Text(repr(torrent.name()))
        self.torrent.append((torrent, pb))
        row = ur.Columns([pb, title])
        self.body.append(row)
        

    def refresh(self):
        for (torrent, progressBar) in self.torrent:
            if torrent.has_metadata():
                if torrent.status().state != libtorrent.torrent_status.seeding:
                    progressBar.set_completion(torrent.status().progress * 100)

                if torrent.status().progress == 1:
                    progressBar.set_completion(100)
                    self.torrent.remove((torrent, progressBar))

class wrapper(ur.Filler):

    def __init__(self, widget):
        self.widget = widget
        super(wrapper, self).__init__(ur.AttrMap(widget,"bg"))

    def refresh(self):
        self.widget.refresh()


widget = wrapper(torrentWindow())
window = MAIN(widget)
window.run()


