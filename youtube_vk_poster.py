# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:48:39 2018

@author: loljkpro
"""

import configparser
Config = configparser.ConfigParser()

import vk_api

import urllib, json

videos_vk = []

def get_all_video_in_channel():
    api_key = Config['YouTube']['ApiKey']
    channel_id = Config['YouTube']['ChannelId']

    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=50'.format(api_key, channel_id)

    video_links = []
    url = first_url
    while True:
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append(base_video_url + i['id']['videoId'])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links

def post_to_vk(message, session):
    # hack for youtube: we cant have correct link if we not upload this as video
    if (message.startswith("https://www.youtube.com")):
        vk_api.VkUpload(session).video(group_id=Config['Vk']['Owner'][1:], link=message)
        return

    vk = session.get_api()
    vk.wall.post(owner_id=Config['Vk']['Owner'], from_group=1, message=message)

def vk_try_get_url(item, session):
    global videos_vk
    try:
        vk = session.get_api()
        id = item['attachments'][0]['video']['id']
        videos_str = Config['Vk']['Owner']+"_"+str(id)
        video = vk.video.get(videos=videos_str)
        url = video['items'][0]['player']
        url = url.replace('?__ref=vk.api', '')
        url = url.replace('https://www.youtube.com/embed/', '')
        url = 'https://www.youtube.com/watch?v=' + url
        videos_vk.append(url)
    except:
        pass

def vk_get_all_videos(session):
    tools = vk_api.VkTools(session)
    wall = tools.get_all('wall.get', 100, {'owner_id': Config['Vk']['Owner']})
    for item in wall['items']:
        vk_try_get_url(item, session)

def main():
    Config.read("conf.ini")
    if (Config.sections() != ['YouTube', 'Vk']):
        print("Wrong Configs")
        return
    videos_youtube = get_all_video_in_channel()

    login = Config['Vk']['Login']
    password = Config['Vk']['Password']
    app_id = Config['Vk']['AppId']
    if Config['Vk']['Socks5IP']:
        import socks
        import socket
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, Config['Vk']['Socks5IP'], int(Config['Vk']['Socks5Port']))
        socket.socket = socks.socksocket

    vk_session = vk_api.VkApi(login, password, app_id=app_id)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    
    #post_to_vk(videos[-1], vk_session)
    vk_get_all_videos(vk_session)
    print(videos_vk, videos_youtube[-1])
    
if __name__ == "__main__":
    main()