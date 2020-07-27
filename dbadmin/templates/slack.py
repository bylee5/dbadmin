# utils/slack.py
from slacker import Slacker

def slack_notify(text=None, channel='#gytjdlee_test', username='알림봇', attachments=None):
    token = 'H2Zl9HYH5Pd2K62ehGOUjDMY'
    slack = Slacker(token)
    slack.chat.post_message(text=text, channel=channel, username=username, attachments=attachments)
    #https: // hooks.slack.com / services / T48QLBBKQ / BLP01FSDV / H2Zl9HYH5Pd2K62ehGOUjDMY
