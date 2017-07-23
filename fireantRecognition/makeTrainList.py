import pandas as pd
import os
import numpy as np

DATASET_DIR="YOUR DATASET DIRECTORY"

neg=pd.read_csv(os.path.join(DATASET_DIR,"negative.txt"))
neg.columns = ['file_name']
negLabels=np.repeat(0, neg.shape[0])
negLabels=pd.DataFrame({"category_id":negLabels})
negList=neg.merge(negLabels,left_index =True,right_index=True)

pos=pd.read_csv(os.path.join(DATASET_DIR,"positive.txt"))
pos.columns = ['file_name']
posLabels=np.repeat(1, pos.shape[0])
posLabels=pd.DataFrame({"category_id":posLabels})
posList=pos.merge(posLabels,left_index =True,right_index=True)
print(posList)

kumo=pd.read_csv(os.path.join(DATASET_DIR,"arigumo.txt"))
kumo.columns = ['file_name']
kumoLabels=np.repeat(2, neg.shape[0])
kumoLabels=pd.DataFrame({"category_id":kumoLabels})
kumoList=kumo.merge(kumoLabels,left_index =True,right_index=True)

if(0):
    hill=pd.read_csv(os.path.join(DATASET_DIR,"hillary.txt"))
    hill.columns = ['file_name']
    hillLabels=np.repeat(3, neg.shape[0])
    hillLabels=pd.DataFrame({"category_id":hillLabels})
    hillList=hill.merge(hillLabels,left_index =True,right_index=True)

dataList=pd.concat([posList, negList,kumoList], ignore_index=True)

#random shuffle
dataList=dataList.reindex(np.random.permutation(dataList.index)).reset_index(drop=True)

dataList.to_csv("datalist.csv")