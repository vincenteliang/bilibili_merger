# -*- coding: UTF-8 -*-
import os
import subprocess
import json
import re
from pathlib import Path


class BiliBili(object):
    def __init__(self, AUDIO, VIDEO, video_path, save_position, title):
        self.AUDIO = AUDIO
        self.VIDEO = VIDEO
        self.save_position = save_position
        self.video_dir = Path(video_path)
        self.title = title

    # ffmpeg将音频视频合在一起
    def comband_av(self):
        path = self.video_dir
        cmd = f'ffmpeg -i {path}\{self.AUDIO} -i {path}\{self.VIDEO} -c:v copy -c:a aac -strict ' \
              f'experimental "{self.save_position}\{self.title}.mp4"'  # 使用双引号将导出文件名括起以解决空格问题
        subprocess.call(cmd, shell=True)


# 从 entry.json 提取视频信息，若没有则递归查找
def find_json(video_path):
    for i in os.listdir(video_path):  # 遍历所有子文件夹
        if i == "merged":  # 跳过存储已处理视频的文件夹
            continue
        inner_path = Path(video_path, i)
        json_path = Path(video_path, i, "entry.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf8')as fp:
                json_data = json.load(fp)
                inner_path = Path(inner_path / json_data['type_tag'])
                title = validate_title(get_title(json_data, title_type))
                title_path = str(Path(inner_path, title + '.mp4'))
                save_path = str(Path(save_position, title + '.mp4'))
                if os.path.exists(save_path):
                    print('跳过: ' + title_path)
                    continue
                print('\n正在导出: ' + title_path)
                load = BiliBili(audio_name, video_name,
                                inner_path, save_position, title)
                load.comband_av()
        else:
            find_json(inner_path)


# 生成标题的方法, 传入 entry.json 和标题类型：
# 1: 【XX】视频标题，适用于单个视频
# 2: 【01】视频集数，适用于合集且小标题有特殊字符导致合成失败
# 3: 【1.XX】视频小标题，适用于小标题有序号且无特殊字符
# 4: 【1 XX】视频集数+小标题，适用于小标题无序号且无特殊字符
def get_title(json_data, type):
    title = page = part = ""
    if 'title' in json_data.keys():
        title = json_data['title']
    if 'page_data' in json_data.keys():  # 文件夹为一串数字
        page_data = json_data['page_data']
    elif 'ep' in json_data.keys():  # 文件夹以S开头
        page_data = json_data['ep']
    if 'page' in page_data.keys():
        page = str(page_data['page'])
    if 'index' in page_data.keys():  # 文件夹以S开头
        page = str(page_data['index'])
    if 'part' in page_data.keys():
        part = page_data['part']
    if 'index_title' in page_data.keys():  # 文件夹以S开头
        part = page_data['index_title']
    if type == 1:  # 标题
        return title
    elif type == 2:  # 1
        return page
    elif type == 3:  # 子标题
        return part
    elif type == 4:  # 1. 子标题
        return page + '. ' + part
    elif type == 5:  # 标题 子标题
        return title + ' ' + part
    elif type == 6:  # 标题 1. 子标题
        return title + ' ' + page + '. ' + part


# 过滤标题中的非法字符
def validate_title(title):
    rstr = r'[\\/:*?"<>|\r\n]'
    title = re.sub(rstr, '_', title)  # 用_替换非法字符
    title = re.sub('–', '-', title)  # 用-替换破折号
    return title


title_type = 6


if __name__ == '__main__':
    save_position = "D:\BiliBili\merged"  # 合成后的视频存放路径
    video_path = "D:\BiliBili"  # 原始文件文件夹的路径
    audio_name = "audio.m4s"        # 音频文件的名称
    video_name = "video.m4s"        # 音频文件的名称
    find_json(video_path)
