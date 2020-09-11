# -*- coding: UTF-8 -*-

import os
import sys
import time

import getframe
import getsubtitle
from config import Config


def clear():
    if sys.platform.find("win") > -1:
        os.system("cls")
    else:
        print()


def main():
    Config.set_path()

    if not (os.path.exists(Config.get_value('video_dir'))):
        os.mkdir(Config.get_value('video_dir'))

    if not (os.path.exists(Config.get_value('video_frames'))):
        os.mkdir(Config.get_value('video_frames'))

    if not (os.path.exists(Config.get_value('output_dir'))):
        os.mkdir(Config.get_value('output_dir'))

    video_name = ""
    video_suffix = ""

    while True:
        clear()
        print("----------Select Video----------")
        video_list = os.listdir(Config.get_value('video_dir'))

        if len(video_list) < 1:
            print("Nothing found\n\n")
            print("Process finished")
            input()
            return

        for video in video_list:
            print("%d.%s" % (video_list.index(video) + 1, video))

        try:
            index = int(input("\nInput index: "))
        except ValueError:
            continue

        if 0 < index <= len(video_list):
            video_name = video_list[index -
                                    1][: video_list[index - 1].rfind(".")]
            video_suffix = video_list[index -
                                      1][video_list[index - 1].rfind("."):]
            break

    Config.set_path(video_name, video_suffix)

    start = time.time()
    print("\n----------Video Division----------")
    print("Start video division")

    if not getframe.main():
        print("Video division FAILED!")
        print("Process finished")
        input()
        return

    print("Video division finished")
    print("Time: %.2fs\n" % (time.time() - start))

    start2 = time.time()
    print("----------Subtitle Analysis----------")
    print("Start subtitle analysis")

    if not getsubtitle.main():
        print("\nSubtitle analysis FAILED!")
    else:
        print("\nSubtitle analysis finished")

    print("Time: %.2fs\n" % (time.time() - start2))

    print("Process finished")
    print("Time: %.2fs" % (time.time() - start))
    input()
    return


if __name__ == "__main__":
    main()
