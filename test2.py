import os
import sys
import praw #need to install this on the server!
import time
from pprint import pprint, pformat #need to install on the server!
import shutil
import logging

###########################################################################
##                                                                       ##
##                              Variables                                ##
##                                                                       ##
###########################################################################

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
    logging.info('starting cleanup()')
    global STATE_cleaned
    global STATE_current_subreddit
    global STATE_current_count

    if STATE_cleaned != 0:
        logging.info('cleanup() called again, exiting')
        return
    STATE_cleaned = 1
    logging.info('starting cleanup()')
    if os.path.isfile(PID_FILE_NAME):
        logging.info('deleted PID file on exit')
        os.remove(PID_FILE_NAME)
    else:
        logging.info('could not delete PID file on exit, was not found')
    try:
        f = open("./data/"+str(STATE_current_subreddit) + "/bin/start.txt","w")
        f.write(str(STATE_current_list_number+STATE_current_count))
        f.close()
    except:
        logging.warning('Unable to write [ %d ] to ./data/%s/bin/start.txt on exit',STATE_current_list_number+STATE_current_count,STATE_current_subreddit)
    logging.info('finished cleanup()')
    sys.exit()

def write_submission(sub):
    global STATE_current_subreddit
    logging.info('writing submission id: %s to subreddit: %s', str(sub.id), str(STATE_current_subreddit))
    if os.path.isfile("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/status.txt"):
        logging.warning('id: %s has been written before, exiting', str(sub.id))
        return
    else:
        f = open("./data/" + str(STATE_current_subreddit) + "/posts/" + str(sub.id) + "/status.txt","w")
        f.write("INPROGRESS")
        f.close()
    try:
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
        logging.info('Writing finishd succesfully id: %s', str(sub.id))

    except:
        e = sys.exc_info()[0]
        logging.error( "Error: %s in write_submission id: %d", str(e), int(sub.id) )
        cleanup()

def get_configuration():
    global LOG_FILE_NAME
    logging.basicConfig(filename='./logs/general_logfile.log',level=logging.DEBUG)
    logging.info('\n\n\nNEW LOGGING CREATED\n')
    for line in open('conf.txt', 'r').read().split('\n'):
        hd , tl = line.split('=')

        #GET LIST OF SUBREDDITS
        if hd.strip().upper() == 'SUBREDDIT_LIST':
            logging.info('overriding default subreddit list...')
            if tl.strip():
                global SUBREDDIT_LIST
                SUBREDDIT_LIST = []
                for val in tl.strip().split(','):
                    logging.info('(+) added sub: %s to the list of subreddits',val.strip().lower())
                    SUBREDDIT_LIST.append(val.strip().lower())

        #POST_HOUR_DELAY
        if hd.strip().upper() == 'HOUR_DELAY':
            logging.info('overriding default hour display...')
            if tl.strip():
                global POST_HOUR_DELAY
                logging.info('setting hour display to %d', int(tl.strip()))
                POST_HOUR_DELAY = int(tl.strip())

        #LOG VALUES THEN EXIT
        logging.info('finished configuration:\n    HOUR_DELAY: %s\n    SUBREDDIT_LIST: %s',POST_HOUR_DELAY,', '.join(SUBREDDIT_LIST))
        return

def init_subreddit_directory(CURRENT_SUBREDDIT, r):
    try:
        os.makedirs("./data/"+str(CURRENT_SUBREDDIT))
        os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/bin")
        os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/posts")

        list_file = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt", "w")

        subreddit = r.get_subreddit(CURRENT_SUBREDDIT)
        subs = subreddit.get_new(limit=100)
        first_time = -1.0
        last_time = 0.0
        for s in subs:
            if first_time < 0:
                first_time = s.created_utc
            last_time = s.created_utc
            os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/posts/" +str(s.id))
            list_file.write("t3_" + str(s.id) + "," + str(time.time()) + "\n")
        list_file.close()

        start_file = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt", "w")
        start_file.write("0")
        start_file.close()

        time_file = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/time.txt", "w")
        time_file.write(str((first_time - last_time)/1.5))
        time_file.close()

        last_time = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/lasttime.txt", "w")
        last_time.write(str(time.time()))
        last_time.close()
    except:
        shutil.rmtree("./data/" + str(CURRENT_SUBREDDIT))



start = time.time()
pid = str(os.getpid())
if os.path.isfile(PID_FILE_NAME):
    print "%s already exists, exiting" % PID_FILE_NAME
    sys.exit()
else:
    file(PID_FILE_NAME, 'w').write(pid)
user = sys.argv[1]
pas = sys.argv[2]

get_configuration()
r = praw.Reddit(user_agent = "Comment scraper testing by u/uva_cs_dev")
r.login(username=user, password=pas)
while True:
    for sub in SUBREDDIT_LIST:
        print "Starting " + str(sub)
        STATE_current_subreddit = sub
        CURRENT_SUBREDDIT = sub

        logging.info('Starting new subreddit: %s', str(sub) )
        if not os.path.isdir("./data/"+str(CURRENT_SUBREDDIT)):
            init_subreddit_directory(CURRENT_SUBREDDIT, r)
            logging.info('Created new directory for subreddit: %s', str(sub) )
        old_time = time.time()
        req_time = 1000000000000.0
        try:
            print "here"
            old_time = float(open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/lasttime.txt","r").read())
            req_time = float(open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/time.txt","r").read())
        except:
            try:
                shutil.rmtree("./data/" + str(CURRENT_SUBREDDIT))
                init_subreddit_directory(CURRENT_SUBREDDIT, r)
            except:
                print "ok"
        print time.time()
        print old_time
        print req_time
        if time.time() - old_time > req_time:
            f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/lasttime.txt","w")
            f.write(str(time.time()))
            f.close()
            subreddit = r.get_subreddit(CURRENT_SUBREDDIT)
            STATE_current_list_number = int(open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","r").read())
            logging.info('The current list number for sub: %s is %d', str(sub), STATE_current_list_number)
            if STATE_current_list_number > 1000:
                logging.info('The list is being refactored')
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
                logging.info('The list finished refactoring')
            STATE_current_list_number = int(open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","r").read())
            f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","r")
            all_lines = f.read().splitlines()
            f.close()
            lines = [x.split(",")[0] for x in all_lines]
            lines_times = [x.split(",")[1] for x in all_lines]
            lines_check = lines
            f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/list.txt","a")
            logging.info('finished reading in list of ids with value: [ ' + ", ".join(lines) + "]")
            try:
                logging.info('begging routine to get new posts')
                for s in subreddit.get_new(limit=100):
                    if not ("t3_" + str(s.id)) in lines_check:
                        os.makedirs("./data/"+str(CURRENT_SUBREDDIT)+"/posts/" +str(s.id))
                        f.write("t3_" + str(s.id) + "," + str(time.time()) + "\n")
                        logging.info('(+) id: %s added to the list for sub: %s', str(s.id), str(CURRENT_SUBREDDIT))
                    else:
                        break
                f.close()
                logging.info('added all new posts to list')

                logging.info('starting routine to scrape adequately old posts')
                count = 0
                while count < len(lines_times[STATE_current_list_number:]) and time.time() - float(lines_times[STATE_current_list_number:][count]) > POST_HOUR_DELAY*3600:
                    count += 1
                logging.info('number of posts to write: %d', count)
                lines_to_write = lines[STATE_current_list_number:][:count]
                logging.info('list of submission ids to write, subreddit: %s list: [ ' + ", ".join(lines_to_write) + "]", CURRENT_SUBREDDIT)
                submissions = r.get_submissions(lines_to_write[:100])
                for s in submissions:
                    logging.info('beginning to write submission id: %s', str(s.id))
                    write_submission(s)
                    STATE_current_count +=1
                STATE_current_count = 0
                logging.info('finished writing all submissions')
                f = open("./data/"+str(CURRENT_SUBREDDIT) + "/bin/start.txt","w")
                f.write(str(STATE_current_list_number+count))
                f.close()
                logging.info('finished updating current list number in subreddit: %s', CURRENT_SUBREDDIT)
                #STATE_current_list_number += count
            except:
                print "failed"
                logging.error('subreddit: %s returned an error, should be deleted from the list', CURRENT_SUBREDDIT)
                f = open("invalid_subs.txt","a")
                f.write(CURRENT_SUBREDDIT + "\n")
                f.close()

os.remove(PID_FILE_NAME)
end = time.time()
f = open("logtimes.txt","a")
f.write(str(start) + ": " + str(end - start) + "\n")
f.close()
