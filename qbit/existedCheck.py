import configparser
import datetime
import glob
import os
import re
import qbittorrentapi
from os.path import exists


def log(log):
    with open("c:/app/btTools/qbit/log/existedCheck.log", 'a', encoding='utf-8') as logFile:
        logFile.write("\n" + str(datetime.datetime.now()) + " " + log)



states = {
    'allocating': 'allocating',
    'checkingDL': 'checkingDL',
    'checkingResumeData': 'checkingResumeData',
    'checkingUP': 'checkingUP',
    'downloading': 'downloading',
    'error': 'error',
    'forcedDL': 'forcedDL',
    'forcedMetaDL': 'forcedMetaDL',
    'forcedUP': 'forcedUP',
    'metaDL': 'metaDL',
    'missingFiles': 'missingFiles',
    'moving': 'moving',
    'pausedDL': 'pausedDL',
    'pausedUP': 'pausedUP',
    'queuedDL': 'queuedDL',
    'queuedUP': 'queuedUP',
    'stalledDL': 'stalledDL',
    'stalledUP': 'stalledUP',
    'unknown': 'unknown',
    'uploading': 'uploading'
}


def printStatusChangeLog(name,  state):
    if state in states:
        state_name = states[state]
    else:
        state_name = "Unknown state: " + str(state)

    log(("Name: {}, State(stateName): {}({})").format(
        name, state, state_name))



tableFilePath = "C:/app/btTools/qbit/existMovieNameTable.txt"
def shouldScanMoviesExsited():
    isTableFileExisted = exists(tableFilePath)
    if isTableFileExisted is False:
        return True
    m_time = os.path.getmtime(tableFilePath)
    dt_m = datetime.datetime.fromtimestamp(m_time)
    mins20PastFromModifyTime = dt_m + datetime.timedelta(minutes=20)
    now_time = datetime.datetime.now()
    timeModifyOverTime = mins20PastFromModifyTime < now_time
    isEmpty = False
    with open(tableFilePath, "r", encoding="utf-8") as openFile:
        lines = openFile.readlines()
        isEmpty = 0 == len(lines)
    return timeModifyOverTime or isEmpty
    


def findExistMovieNames(shouldScanMoviesExsited):
    if shouldScanMoviesExsited:
        # rewrite
        movieFormatExts = ['3g2', '3gp', '3gp2', '3gpp', 'amr', 'amv', 'asf', 'avi', 'bdmv', 'bik', 'd2v', 'divx', 'drc', 'dsa', 'dsm', 'dss', 'dsv', 'evo', 'f4v', 'flc', 'fli', 'flic', 'flv', 'hdmov', 'ifo', 'ivf', 'm1v', 'm2p', 'm2t', 'm2ts', 'm2v', 'm4b', 'm4p', 'm4v', 'mkv', 'mp2v', 'mp4', 'mp4v', 'mpe', 'mpeg', 'mpg', 'mpls', 'mpv2', 'mpv4', 'mov', 'mts', 'ogm', 'ogv', 'pss', 'pva', 'qt', 'ram', 'ratdvd', 'rm', 'rmm', 'rmvb', 'roq', 'rpm', 'smil', 'smk', 'swf', 'tp', 'tpr', 'ts', 'vob', 'vp6', 'webm', 'wm', 'wmp', 'wmv']
        mydict = {
            'E:/movie/film/': movieFormatExts,
            'E:/download/movie/': movieFormatExts,
        }
        fileNameTable = []
        for destination, extensions in mydict.items():
            for ext in extensions:
                for file in glob.glob(destination + '**/*.' + ext,  recursive=True):
                    fileNameTable.append(file[file.rindex("\\")+1::] + "\n")

        with open(tableFilePath, 'w', encoding='utf-8') as tableFile:
            tableFile.writelines(fileNameTable)
        return fileNameTable
    else:
        with open(tableFilePath, "r", encoding="utf-8") as tableFile:
            return tableFile.readlines()


def getGroupByRegFromTorrentName(tName, reg):
    resolutionPatternT = re.compile(reg)
    try:
        group = resolutionPatternT.search(tName)
        if len(group.group(0)) > 0 and len(group.group(1)) > 0:
            return group
        else:
            return None
    except Exception as e:
        pass


def getMovieObjFromTorrentName(name):
    # 格式1
    #name = "The Gift (2000) [1080p] [BluRay] [5.1] [YTS.MX]"
    # 格式2
    #name =  "Wrong.Turn.2003.1080p.BluRay.x265-RARBG"

    yearRegType = {
        1: "\s\((\d{4})\)",
        2: "\.(\d{4})"
    }
    resolutionRegType = {
        1: "\s\[(\d{3,4}[P|p])\]",
        2: "\.(\d{3,4}[P|p])"
    }

    movieT = {}

    try:
        resolutionTGroup = getGroupByRegFromTorrentName(
            name, resolutionRegType.get(1))
        yearTGroup = getGroupByRegFromTorrentName(name, yearRegType.get(1))
        if resolutionTGroup is not None and yearTGroup is not None:
            movieT = {
                "name": name[0:name.index(yearTGroup.group(1))-1].strip(),
                "year": yearTGroup.group(1),
                "reso": resolutionTGroup.group(1),
                "originNameT": name
            }
            return movieT
    except:
        log("!!!Error processing torrentName: {}".format(name))
        pass

    try:
        resolutionTGroup = getGroupByRegFromTorrentName(
            name, resolutionRegType.get(2))
        yearTGroup = getGroupByRegFromTorrentName(name, yearRegType.get(2))
        if resolutionTGroup is not None and yearTGroup is not None:
            movieT = {
                "name": name[0:name.index(yearTGroup.group(1))-1].replace(".", " ").strip(),
                "year": yearTGroup.group(1),
                "reso": resolutionTGroup.group(1),
                "originNameT": name
            }
            return movieT
    except:
        pass

    return None


def getJustLetterAndNumber(originStr):
    newStr = ""
    if originStr is None or originStr.strip() == "":
        return newStr
    for x in originStr:
        if x.isalpha() or x.isnumeric():
            newStr += "{}".format(x)
    return newStr


def getDuplicateMovieNames(existMoiveNames, name, state):
    if(state in ['moving', 'pausedDL', 'pausedUP', 'uploading']):
        return None
    for existMoiveName in existMoiveNames:
        try:
            if existMoiveName != None:
                movieObjT = getMovieObjFromTorrentName(name)
                namePattern = re.compile(u'\(([0-9]{4})\)')
                yearM = namePattern.search(existMoiveName).group(1)
                resoPattern = re.compile(u' (\d{3,4}[P|p]) ')
                resoM = resoPattern.search(existMoiveName).group(1)
                if getJustLetterAndNumber(movieObjT.get("name")).lower() in getJustLetterAndNumber(existMoiveName).lower(): # and movieObjT.get("year") == yearM and movieObjT.get("reso").lower() == resoM.lower():
                    log("DuplicateMovie Found : {}".format(movieObjT))
                    return movieObjT
        except Exception as e:
            pass

    log("No duplicateMovie Found.")
    # do stop and delete the job
    return None


def stopTask(torrent, state):
    torrent.pause()


def getTorrents():
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
    return qbt_client.torrents_info()

def callCheck(torrent):
    try:
        name = torrent.name
        state = torrent.state
        printStatusChangeLog(name, state)
        existMovies = findExistMovieNames(
            shouldScanMoviesExsited=shouldScanMoviesExsited())
        duplicateMovieName = getDuplicateMovieNames(existMovies, name, state)
        if duplicateMovieName is not None:
            log("Should Stop and delete the job.")
            stopTask(torrent=torrent, state=state)
        else:
            log("No need stop and delete the job.")
    except Exception as e:
        return False
    return True

log("\n\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
nowString = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
log("check movie existed @ date and time:{}".format(nowString))
log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

torrentCheckedTableFile = 'C:/app/btTools/qbit/torrentCheckedTable.txt'
isTorrentCheckedTableFileExsited = exists(torrentCheckedTableFile)
fileNamesWithDone=[]
if isTorrentCheckedTableFileExsited is True:
    with open(torrentCheckedTableFile, "r", encoding="utf-8") as tableFile:
        fileNamesWithDone = tableFile.read().splitlines()
torrents =getTorrents()
for torrent in torrents:
    if torrent.name in fileNamesWithDone:
        log("torrent existed in tableFile. Skip! :{}".format(torrent.name))
        continue
    result = callCheck(torrent)
    if result is True:
        with open(torrentCheckedTableFile, "a", encoding="utf-8") as tableFile:
            tableFile.write(torrent.name+"\n")
        log("Done")
        log("")
    else:
        log("!!!Failed")
        log("")