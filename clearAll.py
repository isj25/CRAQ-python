import os
import json
import shutil


configFile = open('config.json')
config = json.load(configFile)

count_replica = config['count_replica']




def delete_servers():
    for i in range(count_replica):
        path = './NODE'+str(i)
        shutil.rmtree(path)


if __name__ == "__main__":
    delete_servers()