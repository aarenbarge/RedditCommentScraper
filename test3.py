import praw
import time

r = praw.Reddit(user_agent = "Comment scraper testing by u/uva_cs_dev")                                    
r.login()     
a = '3baq6m'
sub = r.get_submission(submission_id=a)
print vars(sub)
b = time.time()
print "\n"
l = []
count = 0
for comment in praw.helpers.flatten_tree(sub.comments):
    if type(comment) is praw.objects.MoreComments:
        print "appending a more comment"
        print comment
        if comment.count > 20:
            l.append(comment)
    else:
        count +=1 
        print comment.body
        print "END"

print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
print l
print "\n\n\n\n"

while len(l) > 0:
    a = l[0]
    l = l[1:]
    print a.count
    if len(a.comments()) > 0:
        for comment in praw.helpers.flatten_tree(a.comments()):
            if not type(comment) is praw.objects.MoreComments:
                count += 1
                print comment.body + "\n\nEND\n\n"
            else:
                if comment.count > 20:
                    l.append(comment)

print "\n\n\n\n\n\n\n"
print count
print time.time() - b