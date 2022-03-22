import json
import platform

import tornado.ioloop
import tornado.web
import xarr_notify
import logging
import tornado.log


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info('接收到get请求')

    def post(self):
        logging.info('接收到post请求')


class NoticeHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info('接收到get请求')

    def post(self):
        logging.info('接收到post请求')
        type = self.get_query_argument('type', '')
        if type == 'radarr':
            post_data = self.request.body_arguments
            post_data = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
            if not post_data:
                post_data = self.request.body.decode('utf-8')
                post_data = json.loads(post_data)
            logging.info(post_data)
            xarr_notify.load_user_config()
            xarr_notify.Radarr().exec(post_data)
        elif type == 'sonarr':
            post_data = self.request.body_arguments
            post_data = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
            if not post_data:
                post_data = self.request.body.decode('utf-8')
                post_data = json.loads(post_data)
            logging.info(post_data)
            xarr_notify.load_user_config()
            xarr_notify.Sonarr().exec(post_data)


def make_app():
    logging.info("服务器准备启动")
    return tornado.web.Application([
        (r"/", MainHandler), ('/notice', NoticeHandler)
    ])


# 日志格式
logging.getLogger().setLevel(logging.INFO)
formatter = logging.Formatter(fmt="%(levelname).4s %(asctime)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)


# 日志消息格式
def log_request(handler):
    if 400 <= handler.get_status() <= 499:
        log_method = tornado.log.access_log.warning
    elif 500 < handler.get_status() <= 599:
        log_method = tornado.log.access_log.error
    else:
        log_method = tornado.log.access_log.info

    request_time = 1000.0 * handler.request.request_time()
    log_method("%d %s %.2fms %s", handler.get_status(), handler._request_summary(), request_time, handler.request.headers.get("User-Agent", ""))


if __name__ == "__main__":
    if platform.system() == "Windows":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app = make_app()
    # 自定义tornado日志消息格式
    app.settings["log_function"] = log_request  # app 是 torando.web.Application() 的实例
    app.listen(8898)
    tornado.ioloop.IOLoop.current().start()
    logging.info("服务器启动成功！")