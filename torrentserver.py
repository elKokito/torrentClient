import zmq
import json
import libtorrent
import argparse
import os
from collections import namedtuple

home = os.path.dirname(os.path.realpath(__file__))
with open(home + '/config.json') as conf:
    config = json.load(conf)
d = namedtuple('config', config['download'].keys())
download_path = d(**config['download'])


class Server:

    def __init__(self, verbose=False):

        self.session = libtorrent.session()
        self.session.listen_on(6881, 6891)

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("ipc:///tmp/zmq")

        self.torrent = []

        self.verbose = verbose

    def run(self):

        while True:
            msg = self.socket.recv_string()
            msg = json.loads(msg)
            if self.verbose:
                print("message received")
                print(msg)
            if msg["call"] == "getTorrent":
                self.getTorrent(msg["info"])

            elif msg["call"] == "addTorrent":
                self.addTorrent(msg["torrent"])

            elif msg["call"] == "addTorrentMovie":
                self.addTorrentMovie(msg["torrent"])

            elif msg["call"] == "addTorrentSerie":
                self.addTorrentSerie(msg["torrent"])

            elif msg["call"] == "getList":
                self.getList()

    def getTorrent(self, title):
        res = [(t, h) for (t, h) in self.torrent if t == title][0]
        handle = res[1]
        msg = {"res": handle.status().progress}
        if self.verbose:
            print("senging:")
            print(msg)
        self.socket.send_string(json.dumps(msg))

    def addTorrent(self, info):
        params = {"save_path": download_path.default, "link": info["magnet"]}
        handle = libtorrent.add_magnet_uri(self.session, info["magnet"], params)
        self.torrent.append((info["title"], handle))
        msg = {"res": "ok"}
        if self.verbose:
            print("sending:")
            print(msg)
        self.socket.send_string(json.dumps(msg))

    def addTorrentMovie(self, info):
        params = {"save_path": download_path.movie, "link": info["magnet"]}
        handle = libtorrent.add_magnet_uri(self.session, info["magnet"], params)
        self.torrent.append((info["title"], handle))
        msg = {"res": "ok"}
        if self.verbose:
            print("sending:")
            print(msg)
        self.socket.send_string(json.dumps(msg))

    def addTorrentSerie(self, info):
        params = {"save_path": download_path.serie, "link": info["magnet"]}
        handle = libtorrent.add_magnet_uri(self.session, info["magnet"], params)
        self.torrent.append((info["title"], handle))
        msg = {"res": "ok"}
        if self.verbose:
            print("sending:")
            print(msg)
        self.socket.send_string(json.dumps(msg))

    def getList(self):
        msg = list(map(self.mapTorrent, self.torrent))
        if self.verbose:
            print('sending:')
            print(msg)
        msg = json.dumps(msg)
        self.socket.send_string(msg)

    def mapTorrent(self, torrent):
        return (torrent[0], torrent[1].status().progress)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', action='store_true')
    args = parser.parse_args()
    if args.verbosity:
        server = Server(True)
    else:
        server = Server()
    server.run()
