from __future__ import print_function
import praw
import os
import random

secret = "5qtquiU4ac8S0EJ_9jYzh6x-YR8"
cl_id = "4FGXra_t5mFiEA"

reddit = praw.Reddit(
    client_id=cl_id, client_secret=secret, user_agent='aylmao')


def get_titles(subreddit, number):
    output_dir = "text/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = "%s%s_titles.txt" % (output_dir, subreddit)
    with open(output_file, 'a') as out:
        for submission in reddit.subreddit(subreddit).top(limit=number):
            print(submission.title.encode('utf-8'), file=out, end=' ')
    out.close()


def get_images(subreddit, number):
    output_dir = "pics/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = "%s%s_pics.txt" % (output_dir, subreddit)
    with open(output_file, 'a') as out:
        for submission in reddit.subreddit(subreddit).top(limit=number):
            if '/i.imgur.com/' in submission.url and '.gifv' not in submission.url:
                print(submission.url.encode('utf-8'), file=out)
    out.close()


def choose_image(file):
    images = []
    try:
        with open(file, "r") as ins:
            for line in ins:
                images.append(line)
        ins.close()
    except IOError:
        return 'error'
    return random.choice(images)


# print(get_images("pics", 10))
