# -*- coding: utf-8 -*-
import numpy as np
import websocket
import json
import keras
import cv2
import os
import urllib
import subprocess
from keras.applications.imagenet_utils import preprocess_input

import FinetuneDNN

UPLOAD_PATH="../fireantUI/public/uploads"
DNN_PATH="fireantFGmodel_Dummy.h5"
resnet = keras.models.load_model(DNN_PATH)

def on_message(ws, message):
    fileInfo=json.loads(message)
    print(fileInfo)
    try:
        #download form Web server
        saveFilePath=os.path.join(UPLOAD_PATH, fileInfo["filename"])
        uploadFileURL=urllib.parse.urljoin("http://your.web.server/uploads/",fileInfo["filename"])
        urllib.request.urlretrieve(uploadFileURL,saveFilePath)
        print(saveFilePath)
        print(uploadFileURL)

        #scan virus with Windows Defender.
        subprocess.check_call(["C:/Program Files/Windows Defender/MpCmdRun.exe","-Scan", "-ScanType","3","-File",saveFilePath])

        img = cv2.imread(saveFilePath)

        M = np.float32([[1, 0, 0], [0, 1, 0]])

        img2 = FinetuneDNN.preprocessingAffine(img, M, 1,False,False,False,False,[])
    except subprocess.CalledProcessError:
        print(subprocess.CalledProcessError)
        res={"answer":"cannotRead","filename":fileInfo["filename"]}
        ws.send(json.dumps(res))
        return
    except:
        res={"answer":"cannotRead","filename":fileInfo["filename"]}
        ws.send(json.dumps(res))
        return

    X = [img2]
    X = np.array(X)
    X = preprocess_input(X)
    ans = resnet.predict(X)
    print(ans)
    answer=np.argmax(ans[0])

    if(answer==0):
        res={"answer":"false","filename":fileInfo["filename"]}
    elif(answer==1):
        res={"answer":"true","filename":fileInfo["filename"]}
    elif(answer==2):
        res={"answer":"arigumo","filename":fileInfo["filename"]}
    elif(answer == 3):
        res={"answer":"hillary","filename":fileInfo["filename"]}
    else:
        res={"answer":"unknown","filename":fileInfo["filename"]}

    ws.send(json.dumps(res))

    return

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("Open successfully")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://your.web.server:24564/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()