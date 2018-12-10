# -*- coding:utf-8 -*-
import sys
import platform
import datetime
import requests
import json
import re
import os
import tornado
import tornado.web
import tornado.ioloop
import tornado.escape
from tornado.httpserver import HTTPServer


reload(sys)
sys.setdefaultencoding('utf-8')


class SentenceProcessor():
    """
    处理前端请求
    提供待标注句子
    存储已标注句子
    """
    @classmethod
    def prepare_sentence_list(cls, sent_file):
        """
        返回待标注句子列表
        :param sent_file:
        :return:
        """
        sent_list = []
        with open(sent_file, 'r') as in_file:
            for line in in_file.readlines():
                sent_list.append(line.strip())
        return sent_list

    @classmethod
    def start_label(cls, sent_list, sent_id=None):
        """
        启动标注，如果句子id为None，则从头开始标
        :param sent_list:
        :param sent_id:
        :return:结果dict
        """
        if sent_id is None or sent_id == '':
            sent_id = 0
        res_dict = {"sentence": sent_list[int(sent_id)], "sent_id": int(sent_id)}
        return res_dict


    @classmethod
    def next_sent(cls, old_sent, old_sent_id, polarity, meta_type, labeled_file, sent_list):
        """
        保存已标注的句子
        :param old_sent:
        :param old_sent_id:
        :param labeled_file:
        :param sent_list:
        :return:结果dict
        """
        if old_sent_id is None or old_sent_id == '' or old_sent_id == 'undefined':
            old_sent_id = '0'

        with open(labeled_file, 'a') as out_file:
            out_file.write(old_sent_id+'\t'+old_sent+'\t'+polarity+'\t'+meta_type+'\n')

        res_dict = {"sentence": sent_list[int(old_sent_id)+1], "sent_id": int(old_sent_id)+1}
        return res_dict

global_sent_list = SentenceProcessor.prepare_sentence_list("sent_2_label.txt")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        target = self.get_argument("target")
        if target == "start":
            sent_id = self.get_argument('sent_id')
            res = SentenceProcessor.start_label(global_sent_list, sent_id)
            res_json = tornado.escape.json_encode(res)
            self.write(res_json)
        elif target == 'next':
            old_sent_id = self.get_argument('sent_id')
            old_sent = self.get_argument('old_sent')
            polarity = self.get_argument('polarity')
            meta_type = self.get_argument('type')
            res = SentenceProcessor.next_sent(old_sent, old_sent_id, polarity, meta_type, 'sent_labeled.txt', global_sent_list)
            res_json = tornado.escape.json_encode(res)
            self.write(res_json)

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

