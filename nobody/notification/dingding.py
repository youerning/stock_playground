# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
from ..settings import config
from dingtalkchatbot.chatbot import DingtalkChatbot


webhook = config["DING_WEBHOOK"]
chatbot = DingtalkChatbot(webhook)
