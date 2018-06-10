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

import time
day_today = int(time.time())//60//60//24
video_posted_today = 0 # count of videos was posted this day

from multiprocessing import Pool

def get_all_video_in_channel(channel_id):
    api_key = Config['YouTube']['ApiKey']

    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=50'.format(api_key, channel_id)

    video_links = []
    url = first_url
    while True:
        inp = urllib.request.urlopen(url)
        inp2 = inp.read().decode('utf-8')
        resp = json.loads(inp2)

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
        vk_api.VkUpload(session).video(group_id=Config['Vk']['Owner'][1:], link=message, is_private=False, wallpost=False)
        return

    vk = session.get_api()
    vk.wall.post(owner_id=Config['Vk']['Owner'], from_group=1, message=message)

def vk_try_get_url(item):
    global video_posted_today
    if 'attachments' not in item or 'video' not in item['attachments'][0]:
        return

    id = item['attachments'][0]['video']['id']
    videos_str = Config['Vk']['Owner']+"_"+str(id)
    video_day = item['date']//60//60//24
    if (video_day == day_today):
        video_posted_today += 1
    return videos_str

def vk_video_to_youtube(video):
    s = str(urllib.request.urlopen('https://vk.com/video'+video).read())
    i1 = s.find("ajax.preload")
    i1 = s.find("www.youtube.com", i1)
    i2 = s.find("?enablejsapi", i1)
    return 'https://www.youtube.com/watch?v='+s[i1+len("www.youtube.com\/embed\/\/"):i2]

def vk_get_all_videos(session):
    global videos_vk
    tools = vk_api.VkTools(session)
    wall = tools.get_all('wall.get', 100, {'owner_id': Config['Vk']['Owner']})
    videos = map(vk_try_get_url, wall['items'])
    videos = list(
            filter(None, 
                 list(videos))
              )
    pool = Pool()
    videos_vk = pool.map(vk_video_to_youtube, videos)
    pool.close()
    pool.join()
   #print(videos_vk)


def main():
    Config.read("conf.ini")
    if (Config.sections() != ['YouTube', 'Vk']):
        print("Wrong Configs")
        return

    videos_youtube = []
    for channel_id in Config['YouTube']['ChannelId'].split('\n')[::-1]:
        print ("Getting videos for", channel_id)
        videos_youtube += get_all_video_in_channel(channel_id)

    login = Config['Vk']['Login']
    password = Config['Vk']['Password']
    app_id = Config['Vk']['AppId']
    ignore = Config['YouTube']['Ignore'].split('\n')
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
    
    print ("Retriving all videos from vk")
    vk_get_all_videos(vk_session)

    print ("Today we posted", video_posted_today, "videos")
    if (video_posted_today >= int(Config['Vk']['VideosPerDay'])):
        print("Posting limit done")
        return

    # disjunction
    videos_to_post = [item for item in videos_youtube if (item not in videos_vk+ignore)]

    videos_count = int(Config['Vk']['VideosCount'])
   
    # this algo to take first 5 videos from list
    for video in videos_to_post[-1:-(videos_count+1):-1]:
        print("Posting:", video)
        post_to_vk(video, vk_session)

if __name__ == "__main__":
    main()