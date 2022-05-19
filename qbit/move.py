
import datetime
import sys
import configparser
import qbittorrentapi

torrentName = sys.argv[1]


def log(log):
    with open("c:/app/btTools/qbit/log/qMove.log", 'a', encoding='utf-8') as logFile:
        logFile.write("\n" + str(datetime.datetime.now()) + " " + log)


log("")
log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
nowString = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
log("move the finish downloding media @ date and time:{}".format(nowString))
log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
log("torrent name: {}".format(torrentName))

config = configparser.ConfigParser()
log("read config.ini")
config.read('C:/app/allConfig/qbit/qbitWeb.ini')
log("connect qbit web ui")
qbt_client = qbittorrentapi.Client(
    host=config['conn']['host'],
    port=config['conn']['port'],
    username=config['conn']['username'],
    password=config['conn']['password'],
)


for torrent in qbt_client.torrents_info():
    if torrent.name == torrentName:
        category = torrent.category
        setPath = ""
        if len(category) > 0 and len(config['targetDir'][torrent.category]) > 0:
            setPath = config['targetDir'][torrent.category.lower()]
        if len(setPath) <= 0 and len(torrent.tags) > 0:
            setPath = config['targetDir'][torrent.tags.lower()]
        if len(setPath) <= 0:
            setPath = config['targetDir']["other"]
        log("move files to target dir. torrentName: '{}', targetDir: '{}'".format(
            torrent.name, setPath))
        torrent.setLocation(setPath)
        log("done!")
