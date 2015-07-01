import os
import sys
import praw #need to install this on the server!
import time
from pprint import pprint, pformat
import shutil

###########################################################################
##                                                                       ##
##                              Variables                                ##
##                                                                       ##
###########################################################################

#This is a comment

#Global Variables
PID_FILE_NAME = "./tmp/pidfiles/mydaemon2.pid" # Default value
SUBREDDIT_LIST = ["worldnews"] # Default value
DEFAULT_LIST_BUFFER_VAL = 0
POST_HOUR_DELAY = 24

#State Variables
STATE_current_subreddit = ""
STATE_current_list_number = 0
STATE_lines_to_write = []
STATE_current_count = 0
STATE_cleaned = 0
STATE_most_recent_id = ""

def cleanup():
    global STATE_cleaned
    global STATE_current_subreddit
    global STATE_current_count

    if STATE_cleaned != 0:
        return
    STATE_cleaned = 1
    f = open("./data/"+str(STATE_current_subreddit) + "/bin/start.txt","w")
    f.write(str(STATE_current_list_number+STATE_current_count))
    f.close()
    os.remove(PID_FILE_NAME)
    sys.exit()

def write_submission(sub):
    # SHOULD CHECK WHETHER IT HAS BEEN WRITTEN BEFORE
    global STATE_current_subreddit

    if os.path.isfile("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/status.txt"):
        return
    else:
        f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/status.txt","w")
        f.write("INPROGRESS")
        f.close()
    try:
        #write a generic file
        f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/pprint.txt","w")
        f.write(pformat(vars(sub)))
        f.close()

        l = []
        os.makedirs("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/comments")
        for comment in praw.helpers.flatten_tree(sub.comments):
            if type(comment) is praw.objects.MoreComments:
                if comment.count > 20:
                    l.append(comment)
            else:
                f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/comments/" + str(comment.id) + ".txt","w")
                f.write(pformat(vars(comment)))
                f.close()

        while len(l) > 0:
            a = l[0]
            l = l[1:]
            for comment in praw.helpers.flatten_tree(a.comments()):
                if not type(comment) is praw.objects.MoreComments:
                    f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/comments/" + str(comment.id) + ".txt","w")
                    f.write(pformat(vars(comment)))
                    f.close()
                else:
                    if comment.count > 20:
                        l.append(comment)
        f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/status.txt","w")
        f.write("FINISHED")
        f.close()

    except:
        cleanup()

def get_configuration():
    for line in open('conf.txt', 'r').read().split('\n'):
        hd , tl = line.split('=')
        print "here"
        #SUBREDDIT_LIST
        if hd.strip().upper() == 'SUBREDDIT_LIST':
            print "hi"
            if tl.strip():
                print "ok"
                global SUBREDDIT_LIST
                SUBREDDIT_LIST = []
                print tl.strip().split(',')
                for val in tl.strip().split(','):
                    print "34"
                    SUBREDDIT_LIST.append(val.strip().lower())
        print "75"
        #POST_HOUR_DELAY
        if hd.strip().upper() == 'HOUR_DELAY':
            print "22"
            if tl.strip():
                print "91"
                global POST_HOUR_DELAY
                print "kk"
                POST_HOUR_DELAY = int(tl.strip())
        print POST_HOUR_DELAY
        print SUBREDDIT_LIST

def init_subreddit_directory(CURRENT_SUBREDDIT):

    os.makedirs("./data/"+str(CURRENT_SUBREDDIT))
    os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/bin")
    os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/posts")

    list_file = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt", "w")
    for i in range (0,DEFAULT_LIST_BUFFER_VAL):
        list_file.write("xxxxx\n")
    list_file.close()

    start_file = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt", "w")
    start_file.write("0")
    start_file.close()



pid = str(os.getpid())
if os.path.isfile(PID_FILE_NAME):
    print "%s already exists, exiting" % PID_FILE_NAME
    sys.exit()
else:
    file(PID_FILE_NAME, 'w').write(pid)
user = sys.argv[1]
pas = sys.argv[2]

#try:
print "1"
get_configuration()
print "2"
r = praw.Reddit(user_agent = "Comment scraper testing by u/uva_cs_dev")
print user, pas
r.login(username=user, password=pas)
for sub in SUBREDDIT_LIST:
    print "2"
    STATE_current_subreddit = sub
    CURRENT_SUBREDDIT = sub
    print "Starting... " + str(sub)
    if not os.path.isdir("./data/"+str(CURRENT_SUBREDDIT)):
        init_subreddit_directory(CURRENT_SUBREDDIT)
    subreddit = r.get_subreddit(CURRENT_SUBREDDIT)
    print "3"
    STATE_current_list_number = int(open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","r").read())
    if STATE_current_list_number > 1000:
        f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","r")
        lines = f.read().splitlines()
        f.close()
        f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","w")
        for line in lines[STATE_current_list_number:]:
            f.write(line + "\n")
        f.close()
        f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","w")
        f.write("0")
        f.close()
    print "4"
    STATE_current_list_number = int(open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","r").read())
    f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","r")
    all_lines = f.read().splitlines()
    f.close()
    lines = [x.split(",")[0] for x in all_lines]
    lines_times = [x.split(",")[1] for x in all_lines]
    lines_check = lines
    f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","a")
    print lines_check
    for s in subreddit.get_new(limit=100):
        print "href"
        print str(s.id)
        if not ("t3_" + str(s.id)) in lines_check:
            print "333333"
            os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/posts/" +str(s.id))
            print "55555555"
            f.write("t3_" + str(s.id) + "," + str(time.time()) + "\n")
            print "00000"
        print "oeeei"
    print "oijf"
    f.close()
    print "5"
    count = 0
    while count < len(lines_times[STATE_current_list_number:]) and time.time() - float(lines_times[STATE_current_list_number:][count]) > POST_HOUR_DELAY*3600:
        count += 1
    lines_to_write = lines[STATE_current_list_number:][:count]
    submissions = r.get_submissions(lines_to_write[:100])
    print "6"
    for s in submissions:
        write_submission(s)
        STATE_current_count +=1
    STATE_current_count = 0
    print "7"
    f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","w")
    f.write(str(STATE_current_list_number+count))
    f.close()
    STATE_current_list_number += count

#    try:
os.remove(PID_FILE_NAME)
#    except:
print "what>?"
#except:
#    cleanup()
