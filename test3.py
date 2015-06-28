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

while len(l) > 0:
    a = l[0]
    l = l[1:]
    for comment in a.comments():
        if not type(comment) is praw.objects.MoreComments:
            count += 1
            print comment.body + "\n\nEND\n\n"
        else:
            l.append(comment)

print "\n\n\n\n\n\n\n"
print count
print time.time() - b