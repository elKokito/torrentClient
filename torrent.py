#!/usr/bin/python3
import urwid as ur
import os
import libtorrent
import kat

DOWNLOAD_PATH = "/home/Downloads/"

class MAIN():
    def __init__(self, widget):
        palette = [
                    ("text", "", "", "", "#00d", "g27"),
                    ("button", "", "", "", "#80f", "#6d8"),
                    ("div", "", "", "", "#666", "#86d"),
                    ("torrent", "", "", "", "#008", "#ff8"),
                    ("pbNormal", "", "", "", "#faf", "#fa6"),
                    ("pbComplete", "", "", "", "g58", "g27"),
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



class torrentWindow(ur.ListBox):

    def __init__(self):
        
        self.display = []
        self.text = ur.Text("herro mister", 'center')
        text = ur.AttrMap(self.text, "text")
        self.display.append(text)
        kat_ = kat.Kat()
        torrent = []
        torrent.extend(kat_.movies())
        torrent.extend(kat_.series())


        for t in torrent:
            label = t["name"] + " " + t["size"] + " " + t["seed"]
            button = ur.Button(label, self.show, t["magnet"])
            put = ur.AttrMap(button, "button")
            self.display.append(put)

        div = ur.Divider(" ", 1 , 1)
        inside = ur.AttrMap(div, "div")
        self.display.append(inside)

        self.session = libtorrent.session()
        self.session.listen_on(6881, 6891)
        self.handle = []

        super(torrentWindow, self).__init__(ur.SimpleFocusListWalker(self.display))

    def show(self, button, magnet):
        text = ur.Text(button.label)
        self.body.pop(self.focus_position)
        textGrid = ur.AttrMap(text, "torrent")

        pb = ur.ProgressBar("pbNormal", "pbComplete")
        grid = ur.GridFlow([pb, textGrid], 119, 0, 0, "center")
        self.body.append(grid)

        params = {"save_path": DOWNLOAD_PATH, "link": magnet}
        handle = libtorrent.add_magnet_uri(self.session, magnet, params)
        self.handle.append((handle, pb))

    def refresh(self):
        for (handle, progressBar) in self.handle:
            if handle.has_metadata():
                if handle.status().state != libtorrent.torrent_status.seeding:
                    progressBar.set_completion(handle.status().progress * 100)
                if handle.status().progress == 1:
                    progressBar.set_completion(1)
                    self.handle.remove((handle, progressBar))


widget = torrentWindow()
window = MAIN(widget)
window.run()


