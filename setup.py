import os
import json
from re import L

configFile = open('config.json')
config = json.load(configFile)

count_replica = config['count_replica']




def create_json_config(path,head,tail):
    data = {}
   
    if head:
        data['head'] = True
    else:
        data['head'] = False

    if tail:
        data['tail'] = True
    else:
        data['tail'] = False
    

    if (not head and not tail):
        data['head'] = False
        data['tail'] = False

    with open(path,'w+') as f:
        json.dump(data,f,indent=4)





for i in range(count_replica):
    path = './NODE'+str(i)
    os.mkdir(path)
    jsonFile = path+'/config.json'
    if i==0:
        create_json_config(jsonFile,True,False)
    elif i==count_replica-1 :
        create_json_config(jsonFile,False,True)
    else:
        create_json_config(jsonFile,False,False)





