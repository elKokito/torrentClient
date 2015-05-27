process=$(ps aux | grep 'python3.*server.py' | grep -ci -v 'grep')
if [ $? -gt 0 ];
then
    python3 $(dirname "${BASH_SOURCE[0]}")/shellInteractive/torrentClient/server.py & 
fi
python3 $(dirname "${BASH_SOURCE[0]}")/shellInteractive/torrentClient/torrent.py
