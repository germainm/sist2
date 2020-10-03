import json
import subprocess
import argparse
from pathlib import Path


parser = argparse.ArgumentParser (description='Copy index(es) to web server')
parser.add_argument('directories', metavar='dirs', nargs='+', help='list of directories with indexes')
args=parser.parse_args()

print(args.directories)

with open("config.json") as config:
    parameters=json.load(config)
    print(parameters["server_address"])
    server=parameters["server_address"]
    user=parameters["user"]
    password=parameters["password"]
    server_root_dir=parameters["rootdir"]

for dir in args.directories:
    json_descriptor_file=Path(dir)/"descriptor.json"
    with open(json_descriptor_file) as descriptor:
        index_descriptor=json.load(descriptor) 
        uuid=index_descriptor["uuid"]
        index_root_dir=index_descriptor["root"]
        script1=f"""
#!/bin/sh
ssh {user}@{server} 'mkdir -p {server_root_dir}/{uuid}/{{content,csv,thumbs}}'

scp -r {index_root_dir}/* {user}@{server}:{server_root_dir}/{uuid}/content
scp -r {dir}/thumbnails/* {user}@{server}:{server_root_dir}/{uuid}/thumbs
scp {dir}/*.csv {user}@{server}:{server_root_dir}/{uuid}/csv

    """
    script1=script1.lstrip()
    with open("script1","w") as myscript:
        myscript.write(script1)
    subprocess.run(["chmod","u+x","script1"],check=True)
    subprocess.run(["/home/germain/sist2/sist2-2.8.4/scripts/script1"],check=True)
    print(script1)
