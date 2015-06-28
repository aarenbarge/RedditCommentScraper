import praw
import time

r = praw.Reddit(user_agent = "Comment scraper testing by u/uva_cs_dev")                                    
r.login()     
a = '3bekjg'
sub = r.get_submission(submission_id=a)
b = time.time()
print "\n"
l = []
count = 0
for comment in sub.comments:
    if type(comment) is praw.objects.MoreComments:
        l.append(comment)
    else:
        count +=1 
        print comment.body + "\n\nEND\n\n"
print "\n\n\n\n\n\n\nOKAY GUYS\n\n"

for comment in l[0].comments():
    if type(comment) is praw.objects.MoreComments:
        l.append(comment)
    else:
        count +=1 
        print comment.body + "\n\nEND\n\n"

print l

now_1 = time.time()
for sub in l:
    for comment in sub.comments():
        print vars(comment)
print "\n\n\n\n\n" + str(time.time() - now_1) + "\n\n\n\n\n"

now_2 = time.time()
new_list = [x.comments() for x in l]
for t in new_list:
    for comment in t:
        print vars(comment)
print"\n\n\n\n\n" + str(time.time() - now_2) + "\n\n\n\n\n"