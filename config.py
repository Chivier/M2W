# -*- coding: UTF-8 -*-

import sys


class Config:
    Maps = {
        # 以下请填写自己的 APP 信息
        "APP_KEY": '3a5bf2c6070eec5f925a6eb859c9dc0d',  # 修改为你的 APP_KEY
        "SECRET_KEY": 'ce7b40cb781550f3b2462b056d480ef1',  # 修改为你的 SECRET_KEY

        # 以下请根据需要调整数值
        "split_duration": 1,  # 切片间隔,每 split_duration 秒输出一帧
        "jpg_quality": 40,  # 图片输出质量, 0~100
        "probability": 0.66,  # OCR可信度下限, 0~1
        "subtitle_top_rate": 0.66,  # 字幕范围倍率
        "remove_duplicate": False,  # 强制去重

        # 目录信息,在下方定义
        "video_dir": "",
        "video_path": "",
        "video_frames": "",
        "image_dir": "",
        "output_dir": "",

        # 视频信息,自动生成
        "video_name": "",
        "video_suffix": "",
        "video_width": 0,
        "video_height": 0,
        "subtitle_top": 0,  # 字幕范围 = 字幕范围倍率 * 视频高度,此高度以下的文字被认为是字幕
    }

    @staticmethod
    def set_path(video_name="", video_suffix=""):
        current_path = sys.path[0]

        Config.Maps["video_dir"] = '%s/video/' % current_path  # 视频源文件目录
        # 指定视频文件路径
        Config.Maps["video_path"] = '%s/video/%s%s' % (
            current_path, video_name, video_suffix)
        # 视频切片文件目录
        Config.Maps["video_frames"] = '%s/video_frames/' % current_path
        # 指定视频切片文件目录
        Config.Maps["image_dir"] = '%s/video_frames/%s/' % (
            current_path, video_name)
        Config.Maps["output_dir"] = '%s/output/' % current_path  # 字幕输出目录

        Config.Maps["video_name"] = video_name
        Config.Maps["video_suffix"] = video_suffix

    @staticmethod
    def set_video_props(video_width, video_height):
        Config.Maps["video_width"] = video_width
        Config.Maps["video_height"] = video_height
        Config.Maps["subtitle_top"] = Config.Maps["subtitle_top_rate"] * video_height

    @staticmethod
    def get_value(key):
        return Config.Maps[key]
