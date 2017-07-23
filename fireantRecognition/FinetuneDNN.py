import pandas as pd
import numpy as np
import random
import numpy as np
import cv2
import gc
import os

from PIL import Image

random.seed(1337)
REPEAT=50
MAX_SAMPLES=2756
TRAIN_SAMPLES=2600
VAL_SAMPLES=156
RESIZE_SIZE=224

DATASET_DIR="YOUR DATASET DIRECTORY"

DNN_PATH="fireantFGmodel.h5"

#前処理用関数
def preprocessingAffine(img,M,scale,hasNoise,hasBlur,hasVflip,hasHflip,hasShaei):
    from keras.preprocessing import image

    img2 = cv2.resize(img, (RESIZE_SIZE, RESIZE_SIZE), interpolation=cv2.INTER_NEAREST)
    img2 = cv2.warpAffine(img2, M, (RESIZE_SIZE, RESIZE_SIZE),borderMode=cv2.borderInterpolate(2, 10, cv2.BORDER_REFLECT_101))

    if(hasBlur):
        img2=cv2.GaussianBlur(img2, (3, 3), 1.0)
    if(hasVflip):
        img2=cv2.flip(img2, 0)
    if(hasHflip):
        img2=cv2.flip(img2, 1)


    if(	len(hasShaei) != 0):
        base = .3 * RESIZE_SIZE
        pts1 = np.float32([[0,0], [RESIZE_SIZE, 0], [RESIZE_SIZE,RESIZE_SIZE], [0,RESIZE_SIZE]])
        pts2=np.float32([[-base,-base], [RESIZE_SIZE+base, -base], [RESIZE_SIZE+base,RESIZE_SIZE+base], [-base,RESIZE_SIZE+base]])
        for i in hasShaei:
            pts2[i]=pts1[i]
        M = cv2.getPerspectiveTransform(pts1, pts2)

        img2 = cv2.warpPerspective(img2, M, (RESIZE_SIZE, RESIZE_SIZE))


    img2 =cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    img2 = Image.fromarray(img2)
    img2=image.img_to_array(img2)

    return img2

#finetuningする基のモデルを生成する関数
def createModel():
    from keras import applications
    from keras.models import Model
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Activation, Convolution2D, Flatten, MaxPooling2D,Input
    from keras.optimizers import SGD

    inputs = Input(shape=(RESIZE_SIZE, RESIZE_SIZE, 3))
    base_model = applications.ResNet50(include_top=False, weights='imagenet')(inputs)

    x=Flatten()(base_model)
    predictions=Dense(3, activation='softmax')(x)

    model = Model(inputs=inputs, outputs=predictions)

    for layer in model.layers[:(len(model.layers)*1//3)]:
        layer.trainable = False

    model.compile(loss='categorical_crossentropy',
                  optimizer="adadelta",
                  metrics=['accuracy'])

    return model



def prepro(tmp):
    key, row=tmp[0]
    M=tmp[1]
    scale=tmp[2]
    hasNoise=tmp[3]
    hasBlur=tmp[4]
    hasVflip=tmp[5]
    hasHflip=tmp[6]
    hasShaei=tmp[7]

    img = cv2.imread(os.path.join(DATASET_DIR, row["file_name"]))
    img2 = preprocessingAffine(img, M, scale,hasNoise,hasBlur,hasVflip,hasHflip,hasShaei)

    return (img2, row["category_id"])

if __name__ == "__main__":
    from keras.utils import np_utils
    from multiprocessing import Pool
    from keras.applications.imagenet_utils import preprocess_input

    pool = Pool(8)
    orgTable = pd.read_csv("datalist.csv", header=0)

    model = createModel()
    for i in range(REPEAT):
        print("trial")
        print(i)

        trainTable=orgTable.take(random.sample(range(TRAIN_SAMPLES),TRAIN_SAMPLES))
        validTable=orgTable.take(random.sample(range(TRAIN_SAMPLES,TRAIN_SAMPLES+VAL_SAMPLES),VAL_SAMPLES))

        #前処理部分
        transX=RESIZE_SIZE*(random.random()-0.5)*2*0.2
        transY = RESIZE_SIZE * (random.random() - 0.5) * 2*0.2
        scale=1+(random.random()-0.5)*2*0.4
        deg=int(180*(random.random()-0.5))
        R = cv2.getRotationMatrix2D((RESIZE_SIZE / 2, RESIZE_SIZE / 2), deg, 1)
        M = np.float32([[R[0,0], R[0,1], transX], [R[1,0], R[1,1], transY]])
        hasNoise = random.random() <0.2
        hasBlur = random.random() <0.4
        hasVflip = False
        hasHflip = random.random() <0.3
        rand=int(random.random()*3+0.4)
        hasShaei =[]

        data=pool.map(prepro,[(i,M,scale,hasNoise,hasBlur,hasVflip,hasHflip,hasShaei) for i in trainTable.iterrows()])

        X_train=[x for x,y in data]
        Y_train=[y for x,y in data]
        X_train=np.array(X_train)
        X_train = preprocess_input(X_train)
        Y_train=np_utils.to_categorical(Y_train, 3)

        data=pool.map(prepro,[(i,M,scale,hasNoise,hasBlur,hasVflip,hasHflip,hasShaei) for i in validTable.iterrows()])

        X_val=[x for x,y in data]
        Y_val=[y for x,y in data]
        X_val=np.array(X_val)
        X_val = preprocess_input(X_val)
        Y_val=np_utils.to_categorical(Y_val, 3)

        #学習部分
        model.fit(X_train, Y_train, batch_size=32, epochs=3, verbose=1, validation_data=(X_val, Y_val))
        model.save(DNN_PATH)

        del X_val
        del X_train
        gc.collect()
