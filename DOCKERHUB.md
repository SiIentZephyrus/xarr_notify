## 使用说明

### 功能

支持`radarr`和`sonarr`通知发送，使用`themoviedb`的api获取图片，进行发送，不需要使用图床。

### 使用

```shell
docker run -id --name xarr_notify -v /data/xarr-notify/config:/app/xarr_notify/config \
-p 8898:8898 silentzephyrus/xarr_notify:latest
```

实际使用的webhook链接为：http://192.168.123.10:8898/notice?type=sonarr，type可选项`sonarr`、`radarr`

### 配置

需要在映射的config下创建配置文件，文件名为config.yml，参考配置文件属性是

```yaml
# 参考配置文件
user:
  # 企业微信应用的配置，仅需前4项，若第五项配置了仅在缓存图片未找到的情况下使用;配置参考http://note.youdao.com/s/HMiudGkb
  qywx:
    corpid: '' # 企业微信id
    agentid: '' # 企业微信应用id
    secret: '' # 企业微信应用secret
    touser: '@all' # 发送给用户
themoviedb:
  token: # themoviedb的api令牌，用来推送的时候提供图片
  max_retry_count: 5 # api请求的最大重试次数
  retry_wait_time: 10 # api请求的重试等待时间 秒
```

