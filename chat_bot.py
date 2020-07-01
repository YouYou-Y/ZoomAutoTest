import json
import urllib
import urllib.request
from enum import Enum
from json import JSONDecodeError
import sys

from http_requst import HttpRequest

sys.path.append(r'C:\Users\daisy\AppData\Local\Programs\Python\Python37-32\Lib\site-packages')
from urllib.error import URLError, HTTPError

# from misc.global_vars import CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID, ROBOT_JID, AlertLevel
#from misc.http_requst import HttpRequest


class AlertLevel(Enum):
    info = 1
    warning = 2
    error = 3

CLIENT_ID = 'NQMtd4AiS92M3Os8gkuBlQ'
CLIENT_SECRET = 'GvPFR2lLD1zhakzUKOB1HaMLkqP1y3iw'
ACCOUNT_ID = '3CnfUsOYRymSVbu39Gtrmg'
ROBOT_JID = 'v1q9zzjec1tg23suzx-8owsw@xmpp.zoom.us'
TO_JID_PERSONAL_MONITOR = '3afe5f125ec24d7099bad92c291aeea7@conference.xmpp.zoom.us'
TO_JID_PERSONAL_MONITOR = '953b0d29ba414d4ab8c1316e56bd87d3@conference.xmpp.zoom.us'
TO_JID_ENV_MONITOR = '953b0d29ba414d4ab8c1316e56bd87d3@conference.xmpp.zoom.us'
TO_JID_PUBLIC_NOTIFICATION = '2c8f03b5a6754d0d880b68e30a58144c@conference.xmpp.zoom.us'


class ChatBot:
    def __init__(self, group_id, logger=None):
        self.group_id = group_id
        self.access_token = None
        self.logger = logger

    def set_logger(self, logger):
        self.logger = logger

    def post_message(self, header: str, msg, level=AlertLevel.info, access_token=None):
        is_success = False

        if self.group_id is None:
            if self.logger is not None:
                self.logger.error('ChatBot.post_message, invalid group ID')
                return False

        vt = type(msg)
        if vt != str and vt != dict:
            if self.logger is not None:
                self.logger.error('ChatBot.post_message, invalid msg type')
            return False

        if access_token is None:
            # if self.logger is not None:
            #     self.logger.error('ChatBot.post_message, invalid access token')
            # return False
            access_token = self.get_chat_bot_access_token()

        if self.logger is not None:
            self.logger.info(f'ChatBot.post_message, access_token: {access_token}')

       # color = '#000000'
        color = 'FF0000'

        bold = False
        if level == AlertLevel.warning or level == AlertLevel.error:
            bold = True
        if level == AlertLevel.error:
            #color = '#ff9966'
            color = 'ff0000'
        if level == AlertLevel.warning:
            #color = '#ffcc00'
            color = '#ffa500'
        style = {'color': color, 'bold': bold}
        http_headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        body = {}
        if vt == str:
            body = self.get_str_body(msg, header, style, color)
            if self.logger is not None:
                self.logger.info(f'ChatBot.post_message, message body type: string')
        elif vt == dict:
            body = self.get_dict_body(msg, header, style)
            if self.logger is not None:
                self.logger.info(f'ChatBot.post_message, message body type: dictionary')

        http_request = HttpRequest('https://api.zoom.us/v2/im/chat/messages')
        http_request.set_logger(self.logger)
        http_request.set_timeout(30)
        is_success = http_request.request(http_headers, body, 'POST')
        if is_success:
            if self.logger is not None:
                self.logger.info(f'ChatBot.post_message, post message to chat group successfully')
        else:
            if self.logger is not None:
                self.logger.error(f'ChatBot.post_message, post message to group chat fail, http_status_code: {http_request.http_status_code}, response: \n{http_request.response}')
        return is_success

    def get_str_body(self, msg, header, style, color):
        body = {
            'account_id': ACCOUNT_ID,
            'robot_jid': ROBOT_JID,
            'to_jid': self.group_id,
            'content': {
                'head': {'text': header, 'style': style},
                'body': [{'type': 'section', 'sidebar_color': color, 'sections': [{'type': 'message', 'text': msg, 'style': style}]}]
            }
        }
        return body

    def get_dict_body(self, msg, header, style):
        if type(msg) != dict:
            return

        items = []
        for k, v in msg.items():
            items.append({'key': k, 'value': f'{v}'})

        body = {
            'account_id': ACCOUNT_ID,
            'robot_jid': ROBOT_JID,
            'to_jid': self.group_id,
            'content': {
                'head': {'text': header, 'style': style},
                'body': [{'type': 'fields', 'items': items}]
            }
        }
        return body

    def get_chat_bot_access_token(self):
        if self.logger is not None:
            self.logger(f'ChatBot.get_access_token, start retrieve access token')
        access_token = None
        url_access_token = f'https://api.zoom.us/oauth/token?grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}'
        access_token = ''
        http_request = HttpRequest(url_access_token)
        http_request.set_logger(self.logger)
        http_request.set_timeout(30)
        api_result = http_request.request(method='POST')
        if not api_result:
            if self.logger is not None:
                self.logger.error(f'Utils.get_chat_bot_access_token, get access token failed: {http_request.error}')
        else:
            try:
                req_dict = json.loads(http_request.response)
                if 'access_token' in req_dict:
                    access_token = req_dict['access_token']
            except (JSONDecodeError, TypeError) as e:
                if self.logger is not None:
                    self.logger.error(
                        f'Utils.get_chat_bot_access_token, decode response to json failed, reponse: {http_request.response}, error: {e}')

        return access_token