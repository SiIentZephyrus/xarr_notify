import os

import requests
import yaml


token = ''
max_retry_count = 5
retry_wait_time = 10


def load_user_config():
    global token
    user_setting_filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config/config.yml')
    if os.path.exists(user_setting_filepath):
        with open(user_setting_filepath, 'r', encoding='utf-8') as file:
            user_config = yaml.safe_load(file)
        token = user_config['themoviedb']['token']


# 获取电影明细
def get_movie_info(movie_id):
    load_user_config()
    session = requests.session()
    retry_count = 1
    while True:
        try:
            response = session.get('https://api.themoviedb.org/3/movie/{}?api_key={}&language=zh-CN'.format(movie_id, token))
            if response and response.status_code == 200:
                response = response.json()
                session.close()
                return response
        except Exception as e:
            print('请求电影明细第{}次失败'.format(retry_count))
            print(e)
        if retry_count > max_retry_count:
            print('请求电影明细彻底失败，放弃请求。')
            session.close()
            return None
        retry_count = retry_count + 1


# 获取图片前缀
def get_img_configuration():
    load_user_config()
    session = requests.session()
    retry_count = 1
    while True:
        try:
            response = session.get(
                'https://api.themoviedb.org/3/configuration?api_key={}'.format(token))
            if response and response.status_code == 200:
                response = response.json()
                session.close()
                return response
        except Exception as e:
            print('请求图片配置第{}次失败'.format(retry_count))
            print(e)
        if retry_count > max_retry_count:
            print('请求图片配置彻底失败，放弃请求。')
            session.close()
            return None
        retry_count = retry_count + 1



if __name__ == '__main__':
    # get_img_configuration()
    get_movie_info('4588')