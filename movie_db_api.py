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


# sonarr不直接提供themoviedb的tv id，但可以根据imdbid去获取
def get_tv_info(tv_id, seesion_number, episode_number):
    load_user_config()
    session = requests.session()
    retry_count = 1
    while True:
        try:
            response = session.get(
                'https://api.themoviedb.org/3/find/{}?api_key={}&language=zh-CN&external_source=imdb_id'.format(tv_id, token))
            if response and response.status_code == 200:
                response = response.json()
                # 拿到themoviedb里面的tvid
                show_id = response['tv_results'][0]['id']
                # tv_info = get_tv_info_by_id(show_id)
                tv_info = response['tv_results'][0]
                eps_info = get_tv_ep_info_by_id(show_id, seesion_number, episode_number)
                tv_info['all_name'] = tv_info['name'] + ' S' + str(seesion_number) + 'E' + str(episode_number) + ' - ' + eps_info['name']
                tv_info['eps_name'] = eps_info['name']
                # 获取tv的中文名称
                session.close()
                return tv_info
        except Exception as e:
            print('请求电视剧明细第{}次失败'.format(retry_count))
            print(e)
        if retry_count > max_retry_count:
            print('请求电视剧明细彻底失败，放弃请求。')
            session.close()
            return None
        retry_count = retry_count + 1


def get_tv_info_by_id(show_id):
    session = requests.session()
    retry_count = 1
    while True:
        try:
            response = session.get(
                'https://api.themoviedb.org/3/tv/{}?api_key={}&language=zh-CN'.format(show_id, token))
            if response and response.status_code == 200:
                response = response.json()
                session.close()
                return response
        except Exception as e:
            print('请求电视剧集信息第{}次失败'.format(retry_count))
            print(e)
        if retry_count > max_retry_count:
            print('请求电视剧集信息彻底失败，放弃请求。')
            session.close()
            return None
        retry_count = retry_count + 1


def get_tv_ep_info_by_id(show_id, seesion_number, episode_number):
    session = requests.session()
    retry_count = 1
    while True:
        try:
            response = session.get(
                'https://api.themoviedb.org/3/tv/{}/season/{}/episode/{}?api_key={}&language=zh-CN'.format(show_id, seesion_number, episode_number, token))
            if response and response.status_code == 200:
                response = response.json()
                session.close()
                return response
        except Exception as e:
            print('请求电视剧集单集明细第{}次失败'.format(retry_count))
            print(e)
        if retry_count > max_retry_count:
            print('请求电视剧集单集彻底失败，放弃请求。')
            session.close()
            return None
        retry_count = retry_count + 1




if __name__ == '__main__':
    # get_img_configuration()
    # get_movie_info('4588')
    get_tv_info('tt7808344', 3, 11)