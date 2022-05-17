from msilib.schema import tables
import os
import datetime
import configparser
import glob


def log(log):
    with open("C:/app/btTools/autoHardLink.log", 'a', encoding='utf-8') as logFile:
        logFile.write("\n"+log)


log("")
log("")
log("")
log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
nowString = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
log("auto create hard link for media files @ date and time:{}".format(nowString))
log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


config = configparser.ConfigParser()
log("read config.ini")
config.read('C:/app/allConfig/qbit/qbitWeb.ini')


unitNumber = {
    "tb": 1024*1024*1024,
    "mb": 1024*1024,
    "kb": 1024,
}

fileNamesWithDone=[]
with open("C:/app/btTools/autoHardlinkTable.txt", "r", encoding="utf-8") as tableFile:
    fileNamesWithDone = tableFile.read().splitlines()


log("read config.ini>mediaAndExtType")
mediaTypeSelect = dict(config.items("mediaAndExtType"))
for each_key in mediaTypeSelect:
    log(">>> {}".format(each_key))
    log("read config.ini>mediaAndExtType, key: {}, value: {}".format(each_key, config["mediaAndExtType"][each_key]))
    targetDir = config["targetDir"][each_key]
    log("read config.ini>targetDir: '{}'".format(targetDir))
    embyDir = config["embyDir"][each_key]
    log("read config.ini>embyDir: '{}'".format(embyDir))
    extTypesStr = config["mediaAndExtType"][each_key].split(",")
    log("read config.ini>mediaAndExtType: {}".format(extTypesStr))
    hardLinkAtleast = config["hardLinkAtleast"][each_key]
    log("read config.ini>hardLinkAtleast: {}".format(hardLinkAtleast))
    limitSize = 0
    for unitKey in unitNumber:
        unitValue = unitNumber.get(unitKey)
        if unitKey.lower() in hardLinkAtleast.lower():
            unitSizeNum = unitValue
            limitSize = int(hardLinkAtleast.replace(unitKey, "")) * int(unitValue)
            break

    for ext in extTypesStr:
        for file in glob.glob(targetDir + "/**/*." + ext.strip(), recursive=True):
            log("found file: '{}'".format(file))
            fileBaseName = os.path.basename(file)
            if fileBaseName in fileNamesWithDone:
                log("file existed in tableFile. Skip!")
                continue
            fileSize = os.path.getsize(file)
            if fileSize < unitSizeNum:
                log("file size less than {}. Skip!  fileSize: {}".format(
                    unitSizeNum, fileSize))
                continue
            targetLink = embyDir + "/"+fileBaseName
            try:
                log("make hard link from '{}' to '{}'.".format(file, targetLink))
                os.link(file, targetLink)
            except FileExistsError as e:
                log("error. file hard link existed")
            with open("C:/app/btTools/autoHardlinkTable.txt", "a", encoding="utf-8") as tableFile:
                tableFile.write(fileBaseName+"\n")
            log("add fileName to table")
            log("done")
            
