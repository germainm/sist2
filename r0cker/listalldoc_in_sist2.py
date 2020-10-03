# coding:utf-8

from elasticsearch import Elasticsearch
import json
from pathlib import Path
import argparse
import urllib.parse
import subprocess


rewrite={}

parser=argparse.ArgumentParser(description='Build apache2 dbm file.')
parser.add_argument('dir_index', type=str, metavar='Directory index path',  help='the index directory path')
args=parser.parse_args()
print(args.dir_index)

config_filename="config.json"
with open(config_filename) as config_file:
    config=json.load(config_file)
    
dbm_txt_path=config['dbm_txt_path']
compiled_dbm_txt_path=config['compiled_dbm_txt_path']
server=config['server_address']
user=config['user']

dbm_txt_file=Path(args.dir_index)/"dbm_file.txt"
dbm_txt_file=str(dbm_txt_file)

script1=f"""
#!/bin/sh

scp  {user}@{server}:{dbm_txt_path} {dbm_txt_path} 
"""

script1=script1.lstrip()
with open("copy_server_dbm_script.sh","w") as copy_dbm_script:
    copy_dbm_script.write(script1)
subprocess.run(["chmod","u+x","copy_server_dbm_script.sh"], check=True)
subprocess.run(["/home/germain/sist2/sist2-2.8.4/scripts/copy_server_dbm_script.sh"], check=True)
try:
    with open(dbm_txt_file,"r") as dbm_file:
        for line in dbm_file:
            items=line.split() #default to split with spaces
            if len(items)==2:
                rewrite[items[0]]=items[1]
except FileNotFoundError:
    pass
print("total number of rewrite: %s", str(len(rewrite)))

descriptor=Path(args.dir_index)/"descriptor.json"
with open(descriptor) as descriptor_file:
    index_desc=json.load(descriptor_file)
    print("index uuid: %s", index_desc["uuid"])
    index_uuid=index_desc["uuid"]




#list all document in es
index="sist2"
timeout=1000
size = 1000
body = {"query" : {"match": {"index":index_uuid}}}

es = Elasticsearch(
    ['http://192.168.2.13:9200'],
	http_auth=('admin', 'majuliedamourxxx69'),
	verify_certs=False,
        port=9200,
	retry_on_timeout=True,
	timeout=30
)

# Process hits here
def process_hits(hits):
    for item in hits:
        print(json.dumps(item, indent=2))
        fullpath=Path(item["_source"]["index"])/"content"/item["_source"]["path"]/item["_source"]["name"]
        print(fullpath) 
        rewrite[item["_id"]]=urllib.parse.quote(str(fullpath))

# Check index exists
if not es.indices.exists(index=index):
    print("Index " + index + " not exists")
    exit()

# Init scroll by search
data = es.search(
    index=index,
    scroll='2m',
    size=size,
    body=body
)
# Get the scroll ID
sid = data['_scroll_id']
scroll_size = len(data['hits']['hits'])
ids=set({})
while scroll_size > 0:
    "Scrolling..."
    
    # Before scroll, process current batch of hits
    process_hits(data['hits']['hits'])
    
    data = es.scroll(scroll_id=sid, scroll='2m')

    # Update the scroll ID
    sid = data['_scroll_id']

    # Get the number of results that returned in the last scroll
    scroll_size = len(data['hits']['hits'])

with open(dbm_txt_file,"w") as dbm_file:
    for (uuid, path) in rewrite.items():
        dbm_file.write("%s %s\r\n" % (uuid,path))


#now, it is time top copy the dbm_file to the server

script2=f"""
#!/bin/sh
scp {dbm_txt_file} {user}@{server}:{dbm_txt_path}
ssh {user}@{server} 'httxt2dbm -i {dbm_txt_path} -o {compiled_dbm_txt_path}'
"""

script2=script2.lstrip()
with open("copy_dbm_file_to_server_script.sh","w") as copy_dbm_script:
    copy_dbm_script.write(script2)
subprocess.run(["chmod","u+x","copy_dbm_file_to_server_script.sh"], check=True)
subprocess.run(["/home/germain/sist2/sist2-2.8.4/scripts/copy_dbm_file_to_server_script.sh"]i, check=True)

