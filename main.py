#!/usr/bin/python

# Requires Python v3 Interpreter, ffmpeg & ImageMagick (montage)

import os
import sys
import json
import urllib.request
from shutil import rmtree
import math
import random
import string

GRID_WIDTH=5
REPOSITORY="csprite/csprite"
EXCLUDED_USERS=[]

for item in sys.argv[1:]:
	if item.startswith("--grid-width="):
		GRID_WIDTH=int(item.replace("--grid-width=", ''))
	elif item.startswith("--repo="):
		REPOSITORY=item.replace("--repo=", '')
	elif item.startswith("--exclude="):
		EXCLUDED_USERS=item.replace("--exclude=", '').lower().split(",");
		EXCLUDED_USERS=[user.strip() for user in EXCLUDED_USERS if user]
	else:
		print(f"Unknown option: {item}")

outdir = "./images/"
if os.path.exists(outdir) and os.path.isdir(outdir):
	rmtree(outdir, ignore_errors=True)

os.makedirs(outdir)

with urllib.request.urlopen(f"https://api.github.com/repos/{REPOSITORY}/stats/contributors") as res:
	data = res.read()
	j = json.loads(data)
	numImgs = 0
	Files = []
	for i in j:
		login = i["author"]["login"]
		avatar_url = i["author"]["avatar_url"]

		if login.lower() in EXCLUDED_USERS:
			continue

		filePath = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
		_, headers = urllib.request.urlretrieve(avatar_url, filePath)
		newFilePath = outdir + login + "." + headers.get_content_subtype()
		os.rename(filePath, newFilePath)
		Files.append(newFilePath)
		numImgs += 1

	for i, file in enumerate(Files):
		if not file.endswith(".png"):
			newFile = file + ".png"
			os.system(f"ffmpeg -y -i {file} {newFile}")
			Files[i] = newFile

	width=GRID_WIDTH
	height=math.ceil(numImgs / width)
	print(f"Grid: {width}x{height} - {numImgs}")
	os.system(f"montage {' '.join(Files)} -geometry +10+10 -tile {width}x{height} -resize 256x256 contributors.png")

