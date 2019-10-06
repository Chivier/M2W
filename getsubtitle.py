# -*- coding: UTF-8 -*-

import difflib
import os
import re
import time

import ocrapi
from config import Config


def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


def is_image(f):
    return re.match(r'.+jpg', f)


def get_ocr(image_name):
    image = get_file_content(Config.get_value('image_dir') + image_name)
    res = ocrapi.jd_general_ocr(image)
    code = int(res['code'])
    if code != 10000:
        if code in [10043, 10044]:  # 达到OPS上限
            return res['msg'], -1
        return res['msg'], res['code']  # 系统级错误
    else:
        code = int(res['result']['code'])

        if code == 0:
            return res['result']['resultData'], 0  # OK
        elif code == 13004:
            return res['result']['message'], -2  # 无内容被识别
        elif code == 13005:
            return res['result']['message'], -3  # 其他错误
        else:
            return res['result']['message'], res['result']['code']  # 业务级错误


def main():
    start = time.time()
    probability = Config.get_value('probability')
    remove_duplicate = Config.get_value('remove_duplicate')
    frames = sorted(
        filter(is_image, os.listdir(Config.get_value('image_dir'))))
    ocr_content = ""
    length = len(frames)
    count = 1
    position_data = []

    for image_name in frames:
        ocr_content += image_name + '\n'
        ocr_result, status = get_ocr(image_name)

        while status == -1:  # QPS限制，重试
            print(('%s failed for QPS limit, retry...... process: %d%%' %
                   (image_name, (count * 100) // length)).ljust(60, ' '), end='\r')
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            ocr_result, status = get_ocr(image_name)

        if status == -2:  # 无内容被识别
            ocr_content += 'passed (nothing recognized)\n\n'
            print(('%s passed (nothing recognized), process: %d%%' %
                   (image_name, (count * 100) // length)).ljust(60, ' '), end='\r')
            count += 1
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            continue
        elif status == -3:  # 其他错误
            ocr_content += 'passed (other error)\n\n'
            print(('%s passed (other error), process: %d%%' %
                   (image_name, (count * 100) // length)).ljust(60, ' '), end='\r')
            count += 1
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            continue
        elif status != 0:
            print(('%s FAILED! Error code: %s' %
                   (image_name, status)).ljust(60, ' '))
            print('Check config / image info, and review document')
            return False

        for word in ocr_result:
            if float(word['probability']) < probability:
                ocr_content += 'passed (lower than probability limit)\n'
                continue

            top = int(word['location']['y'])
            height = int(word['location']['height'])
            w = word['text']
            has = False

            for group in position_data:
                # Belong to this group
                if abs(group['top'] - top) < (group['height'] / 2):

                    # Avoid duplicate: check if current word is similar to last word
                    last_word = group['words'][len(group['words']) - 1]

                    if difflib.SequenceMatcher(None, last_word, w).quick_ratio() > 0.8:
                        break

                    # Append words
                    group['words'].append(w)

                    # Cal new value
                    group['totalTop'] += top
                    group['totalHeight'] += height
                    group['totalNum'] += 1
                    group['top'] = group['totalTop'] / group['totalNum']
                    group['height'] = group['totalHeight'] / group['totalNum']
                    has = True
                    break

            if not has:
                position_data.append({
                    'top': top,  # Group standard, using average value of tops
                    'totalTop': top,
                    'height': height,
                    'totalHeight': height,
                    'totalNum': 1,  # How many pics has been add to this group
                    'words': [w]
                })

            ocr_content += 'Words: ' + w + '\nTop: ' + str(word['location']['y']) + '\nHeight: ' + \
                str(word['location']['height']) + '\n'

        count += 1
        ocr_content += '\n'
        print(('%s finished, process: %d%%' %
               (image_name, (count * 100) // length)).ljust(60, ' '), end='\r')
        time.sleep(0.1)  # 线程暂停避免触发QPS限制

    group_info = ""

    for group in position_data:
        # 强制去重
        if remove_duplicate:
            sorted_list = list(set(group["words"]))
            sorted_list.sort(key=group["words"].index)
            group["words"] = sorted_list
            group["totalNum"] = len(sorted_list)

        group_info += str(group) + '\n\n'

    max_group = []

    for group in position_data:
        if group["top"] > Config.get_value("subtitle_top") and group['totalNum'] > len(max_group):
            max_group = group['words']

    subtitle = ','.join(max_group) + '\n\n'
    output = open(Config.get_value('output_dir') +
                  Config.get_value("video_name") + '.txt', mode='w')  # 写入文件
    output.write('----------字幕识别结果----------\n\n%s' % subtitle)
    output.write('----------OCR分析结果----------\n\n%s' % ocr_content)
    output.write('----------字幕分组结果----------\n\n%s' % group_info)
    end = time.time()
    output.write('----------程序运行时间----------\n\nRunning time: %.2fs' %
                 (end - start) + '\n')
    output.close()
    return True
