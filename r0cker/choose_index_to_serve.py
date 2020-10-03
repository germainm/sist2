import argparse
import json
from pathlib import Path
import subprocess

parser=argparse.ArgumentParser(description='Choose index to serve on the webserver')
parser.add_argument('dir_index', type=str, metavar='Directory index path',  nargs="+", help='the index directory path')
args=parser.parse_args()
list_indices={}
indices=[]

print(args.dir_index)

for arg in args.dir_index:
    with open(Path(arg)/"descriptor.json") as descriptor_file:
        descriptor=json.load(descriptor_file)
        descriptor['id']=descriptor['uuid']
        del descriptor['uuid']
        indices.append(descriptor)


list_indices["indices"]=indices

with open("indices.json","w") as indices_file:
    json.dump(list_indices,indices_file)



config_filename="config.json"
with open(config_filename) as config_file:
        config=json.load(config_file)
        rootdir=config['rootdir']
        server=config['server_address']
        user=config['user']

script=f"""
#!/bin/sh
scp indices.json {user}@{server}:{rootdir}/indices.json
"""

script=script.lstrip()
with open("copy_indices_to_serve_to_server_script.sh","w") as script_file:
        script_file.write(script)
subprocess.run(["chmod","u+x","copy_indices_to_serve_to_server_script.sh"], check=True)
subprocess.run(["/home/germain/sist2/sist2-2.8.4/scripts/copy_indices_to_serve_to_server_script.sh"],check=True)

