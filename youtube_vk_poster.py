# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:48:39 2018

@author: loljkpro
"""

import configparser
Config = configparser.ConfigParser()
import vk_api

import urllib, json

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
    vk = session.get_api()
    vk.wall.post(owner_id=Config['Vk']['Owner'], from_group=1, attachments=message)


def main():
    Config.read("conf.ini")
    if (Config.sections() != ['YouTube', 'Vk']):
        print("Wrong Configs")
        return
    videos = get_all_video_in_channel()

    login = Config['Vk']['Login']
    password = Config['Vk']['Password']
    app_id = Config['Vk']['AppId']
    vk_session = vk_api.VkApi(login, password, app_id=app_id)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    post_to_vk(videos[-1], vk_session)

if __name__ == "__main__":
    main()