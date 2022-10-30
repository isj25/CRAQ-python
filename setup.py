import os
import json
from re import L
import shutil

configFile = open('config.json')
config = json.load(configFile)

count_replica = config['count_replica']
PORT = config['port']



def create_json_config(path,head,tail,port):
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

    data['port'] = port
    with open(path,'w+') as f:
        json.dump(data,f,indent=4)



# def create_server_config(path,port):
#     data = {"port":port}

#     with open(path,'w+') as f:
#         json.dump(data,f,indent=4)



def SETUP():
    for i in range(count_replica):
        path = './NODE'+str(i)
        os.mkdir(path)
        jsonFile = path+'/config.json'
        if i==0:
            create_json_config(jsonFile,True,False,PORT+i)
        elif i==count_replica-1 :
            create_json_config(jsonFile,False,True,PORT+i)
        else:
            create_json_config(jsonFile,False,False,PORT+i)
        SRC = './server.py'
        DEST = path+'/'
        shutil.copy(SRC,DEST)


def START():
    print('started')
    for i in range(count_replica):
        dir = './NODE'+str(i)
        if os.path.exists(dir):
            COMMAND = "python3 "+dir+"/server.py"
            os.system(COMMAND)



if __name__ == "__main__":
    SETUP()
    START()
   





