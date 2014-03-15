import praw
from pprint import pprint
from textwrap import wrap
from itertools import izip_longest
import time
import signal

def two_column(left, right, leftWidth=16, rightWidth=62, indent=2, separation=2):
    lefts = wrap(left, width=leftWidth)
    rights = wrap(right, width=rightWidth)
    results = []
    for l, r in izip_longest(lefts, rights, fillvalue=''):
       results.append('{0:{1}}{2:{5}}{0:{3}}{4}'.format('', indent, l, separation, r, leftWidth))
    return "\n".join(results)


user_agent = ("bracketMatcher v00.0001 by /u/Iryeress")
r = praw.Reddit(user_agent = user_agent)

class BracketType:
	def __init__(self, open, close, name):
		self.open = open
		self.close = close
		self.name = name

	def o(self):
		return self.open

	def c(self):
		return self.close

	def n(self):
		return self.name

brackets = [
	BracketType("[", "]", "square brackets"),
	BracketType("(", ")", "parentheses"),
	BracketType("{", "}", "braces"),
]


keep_on = True

def kill_handler(sig, frame):
    global keep_on
    keep_on = False
signal.signal(signal.SIGUSR1, kill_handler)

subr = r.get_subreddit('all')
submission_generator = subr.get_new(limit = 1000)
# submission_generator = r.get_new(limit = 1000)
cycles = 0
while (keep_on):
	posts = []
	count = 0
	for submission in submission_generator:
		if count == 0:
			before = submission.name
		title = submission.title
		op_text = submission.selftext
		url = submission.permalink
		status = []
		has_bracket = False
		has_negative = False
		for bracket in brackets:
			opening = title.count(bracket.o()) + op_text.count(bracket.o())
			closing = title.count(bracket.c()) + op_text.count(bracket.c())
			difference = closing - opening
			if difference < 0:
				has_negative = True
			if opening + closing > 0:
				has_bracket = True
			if has_negative:
				status.append(
					'{0:{1}}'.format(difference, '+' if difference else '').rjust(2).ljust(4)
					+ bracket.n()
				)
		if len(status) > 0:
			posts.append([count, url, title, op_text, status])
		count += 1
		if count % 100 == 0:
			print count

	print "The following %d posts may contain unmatched brackets:\n" % (len(posts))
	for post in posts:
		# pprint(posts)
		print two_column("Post No.:", str(post[0]))
		print two_column("URL:", ''.join([i if ord(i) < 128 else ' ' for i in post[1]]))
		print two_column("Title:", ''.join([i if ord(i) < 128 else ' ' for i in post[2]]))
		print two_column("Self Text:", ''.join([i if ord(i) < 128 else ' ' for i in post[3]]))
		for stat in post[4]:
			print "%s" % stat
		print " "
	if not keep_on:
		break
	print "========================================================"
	print "Waiting 1 min, cycle: %d" % cycles
	print "========================================================"
	cycles += 1 
	time.sleep(60)
	submission_generator = subr.get_new(limit = 1000, params = {'before':before})