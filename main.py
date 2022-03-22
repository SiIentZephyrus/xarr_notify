import json
import platform

import tornado.ioloop
import tornado.web
import xarr_notify


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print('接收到get请求')

    def post(self):
        print('接收到post请求')


class NoticeHandler(tornado.web.RequestHandler):
    def get(self):
        print('接收到get请求')

    def post(self):
        print('接收到post请求')
        type = self.get_query_argument('type', '')
        if type == 'radarr':
            post_data = self.request.body_arguments
            post_data = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
            if not post_data:
                post_data = self.request.body.decode('utf-8')
                post_data = json.loads(post_data)
            print(post_data)
            xarr_notify.load_user_config()
            xarr_notify.Radarr().exec(post_data)
        elif type == 'sonarr':
            post_data = self.request.body_arguments
            post_data = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
            if not post_data:
                post_data = self.request.body.decode('utf-8')
                post_data = json.loads(post_data)
            print(post_data)
            xarr_notify.load_user_config()
            xarr_notify.Sonarr().exec(post_data)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler), ('/notice', NoticeHandler)
    ])

if __name__ == "__main__":
    if platform.system() == "Windows":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app = make_app()
    app.listen(8898)
    tornado.ioloop.IOLoop.current().start()