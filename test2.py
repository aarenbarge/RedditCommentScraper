import os
import sys
import praw #need to install this on the server!
#temporary testing imports
import time
from pprint import pprint, pformat

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

        #write the karma file
        f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/score.txt","w")
        f.write(str(sub.score))
        f.close()
        
        #
        # WRITE OTHERS HERE! ALL MY DATA
        #
        
        #wrap up
        f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/status.txt","w")
        f.write("FINISHED")
        f.close()
        
    except:
        f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/status.txt","w")
        f.write("INCOMPLETE")
        f.close()
    
def get_configuration():
    for line in open('conf.txt', 'r').read().split('\n'):
        hd , tl = line.split('=')
        
        #SUBREDDIT_LIST
        if hd.strip().upper() == 'SUBREDDIT_LIST':
            if tl.strip():
                global SUBREDDIT_LIST
                SUBREDDIT_LIST = []
                for val in tl.strip().split(','):
                    SUBREDDIT_LIST.append(val.strip().lower())
        
        #POST_HOUR_DELAY
        if hd.strip().upper() == 'HOUR_DELAY':
            if tl.strip():
                global POST_HOUR_DELAY
                POST_HOUR_DELAY = int(tl.strip())

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

try:                                                                                                         
    print POST_HOUR_DELAY
    get_configuration()                                                                                                                                                
    r = praw.Reddit(user_agent = "Comment scraper testing by u/uva_cs_dev")                                    
    r.login()                                                                                                  
    
    for sub in SUBREDDIT_LIST:
        STATE_current_subreddit = sub
        CURRENT_SUBREDDIT = sub
        if not os.path.isdir("./data/"+str(CURRENT_SUBREDDIT)):
            init_subreddit_directory(CURRENT_SUBREDDIT)
        subreddit = r.get_subreddit(CURRENT_SUBREDDIT) 
        
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

        STATE_current_list_number = int(open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","r").read())
        
        f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","r")
        all_lines = f.read().splitlines()
        f.close()
        
        lines = [x.split(",")[0] for x in all_lines]
        lines_times = [x.split(",")[1] for x in all_lines]
        lines_check = lines[(len(lines)-100):]

        f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","a")
        for s in subreddit.get_new(limit=100):
            if not ("t3_" + str(s.id)) in lines_check:
                os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/posts/" +str(s.id))
                f.write("t3_" + str(s.id) + "," + str(time.time()) + "\n")
        f.close()
        
        count = 0
        while count < len(lines_times[STATE_current_list_number:]) and time.time() - float(lines_times[STATE_current_list_number:][count]) > POST_HOUR_DELAY*3600:
            count = count + 1
        STATE_lines_to_write.extend(lines[STATE_current_list_number:][:count])
        STATE_current_list_number += count
        open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","w").write(str(STATE_current_list_number))
        print STATE_lines_to_write
        print "ok"
        while len(STATE_lines_to_write) >= 100:
            print "1"
            submissions = r.get_submissions(STATE_lines_to_write[:100])
            print "2"
            STATE_lines_to_write = STATE_lines_to_write[100:]
            print "3"
            for s in submissions:
                write_submission(s)
            print "4"
        print "5"
    try:
        os.remove(PID_FILE_NAME)  
    except:
        print "something went very wrong!"
except:
    #in the event of a crash end gracefully!
    os.remove(PID_FILE_NAME)
    submissions = r.get_submissions(STATE_lines_to_write)
    for s in submissions:
        write_submission(s)
    print "end"
