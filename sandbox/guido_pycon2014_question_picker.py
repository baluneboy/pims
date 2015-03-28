#!/usr/bin/env python

import random

questions = None

def pick_question():
    global questions
    if not questions:
        questions = open('/tmp/questions.txt').read().splitlines()
    return random.choice(questions)

for i in range(4):
    print pick_question() + "?"