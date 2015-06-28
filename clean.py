import os
import sys
import shutil
if os.path.isfile("./tmp/pidfiles/mydaemon2.pid"):
    os.remove("./tmp/pidfiles/mydaemon2.pid")
shutil.rmtree("./data")
os.mkdir("./data")
shutil.copytree('./values/funny', './data/funny')
shutil.copytree('./values/worldnews', './data/worldnews')
shutil.copy('./values/init.txt', './data/init.txt')
