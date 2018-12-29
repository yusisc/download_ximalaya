#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 12/30/2018 1:24 AM
# @Author  : yusisc (yusisc@gmail.com)

import requests
import json
import re
from bs4 import BeautifulSoup
from multiprocessing import Pool
import os
import sys


def download_track(url, file_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    response = requests.get(url, headers=headers)
    with open(file_path, 'wb') as ff:
        ff.write(response.content)
    print(f'this is done: {file_path}')
    return 0



def parse_album(album_url):
    # album_url = 'https://www.ximalaya.com/xiangsheng/2677700/1737666'
    # album_url = 'https://www.ximalaya.com/youshengshu/14875677/'
    # album_url = 'https://www.ximalaya.com/youshengshu/4071220/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    regex = re.compile(r"[-()\"#/@;:<>{}`\\+=~|!?,%&*^]")

    arg_individuals = []

    # for title
    response = requests.get(url=album_url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('h1', {'class':'title NQi'})
    title = title.string
    title = regex.sub('_', title)
    # print(title)

    # for album_id
    album_id_tmp = re.sub('http.*com/[a-zA-z]*/', '', album_url)
    album_id_tmp = album_id_tmp.split('/')
    album_id = album_id_tmp[0]
    # print(album_id)

    # parse each track infomation, and create a thread for each track
    page_num = 0
    # available page_num start from 1.
    while True:
        page_num += 1
        json_url = f'https://www.ximalaya.com/revision/play/album?albumId={album_id}&pageNum={page_num}&sort=0&pageSize=30'
        # print(json_url)

        response = requests.get(url=json_url, headers=headers)
        html = response.text
        # print(html)

        json_obj = json.loads(html)
        # print(dir(json_obj))
        track_list = json_obj['data']['tracksAudioPlay']
        if len(track_list) == 0:
            break
        for track_info in track_list:
            # print(type(track_info))
            # print(track_info, '\n*************************************')
            track_id = track_info['index']
            track_name = track_info['trackName']
            track_media_url = track_info['src']
            print(f'individual info_____ , title: {title:<16}, track_id: {track_id:<4}, track_name: {track_name:<20}, track_media_url: {track_media_url:<10}')
            
            file_path = f'{title}/{track_id:03}_{track_name}.m4a'
            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            arg_individual = (track_media_url, file_path)
            arg_individuals.append(arg_individual)
    return arg_individuals


if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise Exception("""please use commnad like:
        python download_ximalaya.py https://www.ximalaya.com/youshengshu/4720371/ https://www.ximalaya.com/lishi/323215/
        """)

    album_urls = sys.argv[1:]
    pool = Pool(16)
    for album_url in album_urls:
        print(album_url)
        arg_individuals = parse_album(album_url)
        
        for arg_individual in arg_individuals:
            pool.apply_async(download_track, args=arg_individual)
    pool.close()
    pool.join()
    print('done.')
