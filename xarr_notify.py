import json
import os
import re
import logging
import requests
import yaml
import movie_db_api

# 请在 config.yml 文件中配置
QYWX = {}


# 企业微信 APP 推送
def wecom_app(title, content, media_url=''):
    try:
        if not QYWX:
            logging.info("QYWX_AM 并未设置！！\n取消推送")
            return
        # QYWX_AM_AY = re.split(',', QYWX)
        # if 4 < len(QYWX_AM_AY) > 5:
        #     print("QYWX_AM 设置错误！！\n取消推送")
        #     return
        corpid = QYWX['corpid']
        corpsecret = QYWX['secret']
        touser = QYWX['touser']
        agentid = QYWX['agentid']
        try:
            media_id = QYWX['media_id']
        except:
            media_id = ''
        wx = WeCom(corpid, corpsecret, agentid)
        # 如果没有配置 media_id 默认就以 text 方式发送
        if media_url:
            response = wx.send_news(title, content, media_url, touser)
        elif not media_id:
            message = title + '\n\n' + content
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)
        if response == 'ok':
            logging.info('推送成功！')
        else:
            logging.info('推送失败！错误信息如下：\n', response)
    except Exception as e:
        logging.info(e)


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0"
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace('\n', '<br/>'),
                        "digest": message
                    }
                ]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_news(self, title, message, meida_url, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "news",
            "agentid": self.AGENTID,
            "news": {
                "articles": [
                    {
                        "title": title,
                        "picurl": meida_url,
                        "author": "Author",
                        "description": message,
                        "url": 'http://192.168.123.6:7878/'
                    }
                ]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


class Smms:

    @classmethod
    def get_token(cls, username, password):
        """
        提供用户名和密码返回用户的 API Token，若用户没有生成 Token 则会自动为其生成一个。
        :param username: 用户名/邮件地址
        :param password: 密码
        :return: API Token
        """
        url = 'https://sm.ms/api/v2/token'
        data = {'username': username, 'password': password}
        re = requests.post(url, data=data)

        if json.loads(re.content)['success']:
            token = json.loads(re.content)['data']['token']
            return token
        else:
            raise KeyError

    @classmethod
    def upload(cls, image, token=None):
        """
        图片上传接口。
        :param image: 图片的地址
        :param token: API Token
        :return: 返回图片上传后的URL
        """
        url = 'https://sm.ms/api/v2/upload'
        params = {'format': 'json', 'ssl': True}
        files = {'smfile': open(image, 'rb')}
        headers = {'Authorization': token}
        if token:
            re = requests.post(url, headers=headers, files=files, params=params)
        else:
            re = requests.post(url, files=files, params=params)
        re_json = json.loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']['url']
            else:
                return re_json['images']
        except KeyError:
            if re_json['code'] == 'unauthorized':
                # raise ConnectionRefusedError
                return None
            if re_json['code'] == 'flood':
                # raise ConnectionAbortedError
                return None

    @classmethod
    def get_history(cls, token):
        """
        提供 API Token，获得对应用户的所有上传图片信息。
        :param token: API Token
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/upload_history'
        params = {'format': 'json', 'ssl': True}
        headers = {'Authorization': token}
        re = requests.get(url, headers=headers, params=params)
        re_json = json.loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']
            else:
                # raise KeyError
                return None
        except KeyError:
            if re_json['code'] == 'unauthorized':
                # raise ConnectionRefusedError
                return None

    @classmethod
    def get_history_ip(cls):
        """
        获得上传历史. 返回同一 IP 一个小时内上传的图片数据。
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/history'
        params = {'format': 'json', 'ssl': True}
        re = requests.get(url, params=params)
        re_json = json.loads(re.text)
        if re_json['success']:
            return re_json['data']
        else:
            # raise KeyError
            return None


def load_user_config():
    global QYWX
    user_setting_filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config/config.yml')
    if os.path.exists(user_setting_filepath):
        with open(user_setting_filepath, 'r', encoding='utf-8') as file:
            user_config = yaml.safe_load(file)
        QYWX = user_config['user']['qywx']
        if not QYWX:
            raise KeyError('未配置企业微信')


def get_info_from_imdb_id(imdb_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    api_url = "https://movie.douban.com/j/subject_suggest?q="
    req_url = api_url + imdb_id
    try:
        return requests.get(req_url, headers=headers).json()[0]
    except Exception:
        return None


def get_env_value(key):
    if key in os.environ and os.environ[key]:
        return os.environ[key]
    else:
        return None


def HRS(size):
    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    for i in range(len(units) - 1, -1, -1):
        if size >= 2 * (1024 ** i):
            return '%.2f' % (size / (1024 ** i)) + ' ' + units[i]


def fill_msg_from_detail(detail, event_type,  platform):
    title = ''
    msg = ''
    msg += '事件类型：' + event_type
    msg += '\n平台名称：' + platform
    if detail.get('tmdbid'):
        info = get_info_from_imdb_id(detail['imdbid'])
        if info and info.get('title'):
            detail['title'] = re.sub(r' 第\S{1,3}季', '', info['title'], count=1)
    if detail.get('title'):
        title = detail['title']
        msg += '\n影片名称：' + (detail['eps_title'] if detail['eps_title'] else title)
    if detail.get('quality'):
        msg += '\n视频质量：' + detail['quality']
    if detail.get('size'):
        msg += '\n视频大小：' + HRS(int(detail['size']))
    if detail.get('path'):
        msg += '\n文件路径：' + detail['path']
    if detail.get('isupgrade'):
        msg += '\n格式升级：' + ('是' if 'True' == detail['isupgrade'] else '否')
    if detail.get('deletedfiles'):
        msg += '\n删除文件：' + ('是' if 'True' == detail['deletedfiles'] else '否')
    if detail.get('indexer'):
        msg += '\n抓取自：' + detail['indexer']
    return title, msg


class Sonarr:
    def __init__(self):
        self.type = 'Sonarr'
        self.type_dict = {
            "Grab": self.grab,
            "Download": self.download,
            "Rename": self.rename,
            "EpisodeDeleted": self.episode_deleted,
            "SeriesDeleted": self.series_deleted,
            "HealthIssue": self.health_issue,
            "Test": self.test
        }

    def grab(self, post_data):
        imdb_id = post_data['series']['imdbId']
        episode_number = post_data['episodes'][0]['episodeNumber']
        seesion_number = post_data['episodes'][0]['seasonNumber']
        movie_data = movie_db_api.get_tv_info(imdb_id, seesion_number, episode_number)
        movie_img_conf = movie_db_api.get_img_configuration()
        img_url = ''
        if movie_img_conf and movie_data:
            img_url = movie_img_conf['images']['base_url'] + 'w780' + movie_data['backdrop_path']
        detail = {
            'id': post_data['series']['id'],
            'title': movie_data['all_name'] if movie_data and movie_data['all_name'] else post_data['series']['title'],
            'eps_title': movie_data['eps_name'],
            'imdbid': imdb_id,
            'quality': post_data['release']['quality'],
            'size': post_data['release']['size'],
            'episodenumbers': episode_number,
            'seasonnumber': seesion_number,
            'torrent_title': post_data['release']['releaseTitle'],
            'indexer': post_data['release']['indexer'],
        }
        title, msg = fill_msg_from_detail(detail, '开始下载', 'Sonarr')
        wecom_app('开始下载：' + title, msg, img_url)
        logging.info("Grab")

    def download(self, post_data):
        imdb_id = post_data['series']['imdbId']
        episode_number = post_data['episodes'][0]['episodeNumber']
        seesion_number = post_data['episodes'][0]['seasonNumber']
        movie_data = movie_db_api.get_tv_info(imdb_id, seesion_number, episode_number)
        movie_img_conf = movie_db_api.get_img_configuration()
        img_url = ''
        if movie_img_conf and movie_data:
            img_url = movie_img_conf['images']['base_url'] + 'w780' + movie_data['backdrop_path']
        detail = {
            'id': post_data['series']['id'],
            'title': movie_data['all_name'] if movie_data and movie_data['all_name'] else post_data['series']['title'],
            'eps_title': movie_data['eps_name'],
            'imdbid': imdb_id,
            'episodenumbers': episode_number,
            'seasonnumber': seesion_number,
            'quality': post_data['episodeFile']['quality'],
            'size': post_data['episodeFile']['size'],
            'isupgrade': post_data['isUpgrade']
        }
        title, msg = fill_msg_from_detail(detail, '下载完成', 'Sonarr')
        wecom_app('下载完成：' + title, msg, img_url)
        logging.info("Download")

    def rename(self, post_data):
        logging.info("Rename")

    def episode_deleted(self, post_data):
        logging.info("EpisodeDeleted")

    def series_deleted(self, post_data):
        logging.info("SeriesDeleted")

    def health_issue(self, post_data):
        logging.info("HealthIssue")

    def default(self, post_data):
        logging.info("Default")

    def test(self, post_data):
        detail = {
            'id': os.environ.get('sonarr_series_id', None),
            'title': os.environ.get('sonarr_series_title', None),
            'imdbid': os.environ.get('sonarr_series_imdbid', None),
            'episodenumbers': os.environ.get('sonarr_episodefile_episodenumbers', None),
            'seasonnumber': os.environ.get('sonarr_episodefile_seasonnumber', None),
            'quality': os.environ.get('sonarr_episodefile_quality', None),
            'isupgrade': os.environ.get('sonarr_isupgrade', None),
        }
        title, msg = fill_msg_from_detail(detail, '下载完成', 'Sonarr')
        wecom_app('下载完成：' + title, msg, url)
        logging.info("Download")

    def exec(self, post_data):
        fun_name = post_data['eventType']
        radarr_fun = self.type_dict.get(fun_name, self.default)
        radarr_fun(post_data)


class Radarr:

    def __init__(self):
        self.type = 'Radarr'
        self.type_dict = {
            'Grab': self.grab,
            'Download': self.download,
            'Rename': self.rename,
            'HealthIssue': self.health_issue,
            'ApplicationUpdate': self.application_update,
            'Test': self.test
        }

    def grab(self, post_data):
        movie_data = movie_db_api.get_movie_info(post_data['movie']['tmdbId'])
        movie_img_conf = movie_db_api.get_img_configuration()
        img_url = ''
        if movie_img_conf and movie_data:
            img_url = movie_img_conf['images']['base_url'] + 'w780' + movie_data['backdrop_path']
        detail = {
            'id': post_data['movie']['id'],
            'title': movie_data['title'] if movie_data and movie_data['title'] else post_data['movie']['title'],
            'tmdbId': post_data['movie']['tmdbId'],
            'quality': post_data['release']['quality'],
            'size': post_data['release']['size'],
            'indexer': post_data['release']['indexer'],
        }
        title, msg = fill_msg_from_detail(detail, '抓取中', 'Radarr')
        wecom_app('下载完成：' + title, msg, img_url)
        logging.info("Grab")

    def download(self, post_data):
        movie_data = movie_db_api.get_movie_info(post_data['movie']['tmdbId'])
        movie_img_conf = movie_db_api.get_img_configuration()
        img_url = ''
        if movie_img_conf and movie_data:
            img_url = movie_img_conf['images']['base_url'] + 'w780' + movie_data['backdrop_path']
        detail = {
            'id': post_data['movie']['id'],
            'title': movie_data['title'] if movie_data and movie_data['title'] else post_data['movie']['title'],
            'tmdbId': post_data['movie']['tmdbId'],
            'quality': post_data['movieFile']['quality'],
            'size': post_data['movieFile']['size'],
        }
        title, msg = fill_msg_from_detail(detail, '下载完成', 'Radarr')
        wecom_app('下载完成：' + title, msg, img_url)
        logging.info("Download")

    def rename(self, post_data):
        logging.info("Rename")

    def application_update(self, post_data):
        logging.info("ApplicationUpdate")

    def health_issue(self, post_data):
        logging.info("HealthIssue")

    def default(self, post_data):
        logging.info("Default")

    def test(self, post_data):
        movie_data = movie_db_api.get_movie_info(post_data['movie']['tmdbId'])
        movie_img_conf = movie_db_api.get_img_configuration()
        img_url = ''
        if movie_img_conf and movie_data:
            img_url = movie_img_conf['images']['base_url'] + 'w780' + movie_data['backdrop_path']
        detail = {
            'id': post_data['movie']['id'],
            'title': movie_data['title'] if movie_data and movie_data['title'] else post_data['movie']['title'],
            'tmdbId': post_data['movie']['tmdbId'],
            'quality': post_data['release']['quality'],
            'size': post_data['release']['size'],
            'indexer': post_data['release']['indexer'],
        }
        title, msg = fill_msg_from_detail(detail, '测试', 'Radarr')
        wecom_app('Radarr测试推送：' + title, msg, img_url)

    def exec(self, post_data):
        fun_name = post_data['eventType']
        radarr_fun = self.type_dict.get(fun_name, self.default)
        radarr_fun(post_data)


