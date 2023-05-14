import csv
import json
import re
import sys

import snbtlib
from pathlib import Path


#  主要用于从ftbq文件中提取双语训练集，
#  先在tmp文件夹中为你要提取的整合包新建一个文件夹
#  再将FTBQ双语文件重命名为ftbquests-en与ftbquests-zh分别放到这个文件夹中
#  如果整合包任务已经使用了键值直接将en_us.json和zh_cn.json放入即可
#  运行即可生成zh-en.csv


def get_quest(input_path: Path) -> str:
    with open(input_path, 'r', encoding="utf-8") as fin:
        quest = fin.read()
        try:
            quest = snbtlib.loads(quest)  # 转化为json格式并读取
            return quest
        except TypeError:
            print('snbtlib调用出错，可能是python环境版本过低或其它问题！')


def get_lang(input_path: Path):
    with open(input_path, 'r', encoding="utf-8") as fin:
        text = fin.read()
    try:
        lang = json.loads(text)  # 转化为json格式并读取
        return lang
    except TypeError:
        print('json调用出错，请检查文件格式！')


def get_value(prefix: str, text):
    """
    为key赋予value（多行与图片)
    :param text:文本
    :param prefix:键名前缀
    :return 键文dict和处理为键值后的原文
    """
    key_value = {}  # 用于存放新生成的键值及其对应的文本
    if isinstance(text, list):
        for i in range(0, len(text)):
            if bool(re.search(r'\S', text[i])):  # 非空行，为此行生成键值
                if text[i].find('{image:') == -1:  # 非图片
                    local_key = prefix + '.' + str(i)
                    key_value[local_key] = text[i]
                    text[i] = '{' + local_key + '}'
        return text, key_value
    else:
        if text.find('{image:') == -1:  # 非图片
            key_value[prefix] = text
            text = '{' + prefix + '}'
        return text, key_value


def trans2lang(quest_path):
    key_value = {}  # 用于存放新生成的键值及其对应的文本
    for input_path in quest_path.rglob("*.snbt"):
        print(input_path)
        quest = get_quest(input_path)
        prefix = '' + list(input_path.parts)[-1].replace('.snbt', '')  # 以snbt文件名为key的前缀便于回溯
        # chapter_groups[title]
        if quest.get('chapter_groups'):
            chapter_groups = quest['chapter_groups']
            for i in range(0, len(chapter_groups)):
                local_key = 'ftbquests.chapter_groups.' + prefix + '.' + str(i) + '.title'
                text, new_key_value = get_value(local_key, chapter_groups[i]['title'])
                key_value.update(new_key_value)
                quest['chapter_groups'][i]['title'] = text
            continue

        # loot_table[title]
        if quest.get('loot_size'):  # 仅以键值判断是否是loot_table内容
            title = quest['title']
            local_key = 'ftbquests.loot_table.' + prefix + '.title'
            text, new_key_value = get_value(local_key, quest['title'])
            key_value.update(new_key_value)
            quest['title'] = text
            continue

        # chapter[title,subtitle]
        if quest.get('title'):
            title = quest['title']
            local_key = 'ftbquests.chapter.' + prefix + '.title'
            text, new_key_value = get_value(local_key, quest['title'])
            key_value.update(new_key_value)
            quest['title'] = text
        if quest.get('subtitle'):
            subtitle = quest['subtitle']
            if len(subtitle) > 0:
                local_key = 'ftbquests.chapter.' + prefix + '.subtitle'
                text, new_key_value = get_value(local_key, quest['subtitle'])
                key_value.update(new_key_value)
                quest['subtitle'] = text

        # chapter.images[i][hover]
        if quest.get('images'):
            images = quest['images']
            for i in range(0, len(images)):
                if images[i].get('hover'):
                    hover = images[i]['hover']
                    if len(hover) > 0:
                        local_key = 'ftbquests.chapter.' + prefix + '.images.' + str(i) + '.hover'
                        text, new_key_value = get_value(local_key, hover)
                        key_value.update(new_key_value)
                        quest['images'][i]['hover'] = text

        # chapter.quests[i][title,subtitle,description]
        # chapter.quests[i].tasks[j].[title,description]
        # chapter.quests[i].rewards[j].title
        if quest.get('quests'):
            quests = quest['quests']
            for i in range(0, len(quests)):
                # title
                if quests[i].get('title'):
                    title = quests[i]['title']
                    if len(title) > 0:
                        local_key = 'ftbquests.chapter.' + prefix + '.quests.' + str(i) + '.title'
                        text, new_key_value = get_value(local_key, title)
                        key_value.update(new_key_value)
                        quest['quests'][i]['title'] = text
                # subtitle
                if quests[i].get('subtitle'):
                    subtitle = quests[i]['subtitle']
                    if len(subtitle) > 0:
                        local_key = 'ftbquests.chapter.' + prefix + '.quests.' + str(i) + '.subtitle'
                        text, new_key_value = get_value(local_key, subtitle)
                        key_value.update(new_key_value)
                        quest['quests'][i]['subtitle'] = text
                # description
                if quests[i].get('description'):
                    description = quests[i]['description']
                    if len(description) > 0:
                        local_key = 'ftbquests.chapter.' + prefix + '.quests.' + str(i) + '.description'
                        text, new_key_value = get_value(local_key, description)
                        key_value.update(new_key_value)
                        quest['quests'][i]['description'] = text

                # tasks[j].title
                if quests[i].get('tasks'):
                    tasks = quests[i]['tasks']
                    if len(tasks) > 0:
                        for j in range(0, len(tasks)):
                            if tasks[j].get('title'):
                                title = tasks[j]['title']
                                local_key = 'ftbquests.chapter.' + prefix + '.quests.' + str(i) + '.tasks.' + str(
                                    j) + '.title'
                                text, new_key_value = get_value(local_key, title)
                                key_value.update(new_key_value)
                                quest['quests'][i]['tasks'][j]['title'] = text

                # tasks[j].description
                if quests[i].get('tasks'):
                    tasks = quests[i]['tasks']
                    if len(tasks) > 0:
                        for j in range(0, len(tasks)):
                            if tasks[j].get('description'):
                                description = tasks[j]['description']
                                local_key = 'ftbquests.chapter.' + prefix + '.quests.' + str(i) + '.tasks.' + str(
                                    j) + '.description'
                                text, new_key_value = get_value(local_key, description)
                                key_value.update(new_key_value)
                                quest['quests'][i]['tasks'][j]['description'] = text

                # rewards[j].title
                if quests[i].get('rewards'):
                    rewards = quests[i]['rewards']
                    if len(rewards) > 0:
                        for j in range(0, len(rewards)):
                            if rewards[j].get('title'):
                                title = rewards[j]['title']
                                local_key = 'ftbquests.chapter.' + prefix + '.quests.' + str(i) + '.rewards.' + str(
                                    j) + '.title'
                                text, new_key_value = get_value(local_key, title)
                                key_value.update(new_key_value)
                                quest['quests'][i]['rewards'][j]['title'] = text

    return key_value


def list_dir(path):
    path = Path(path)
    return [e for e in path.iterdir() if e.is_dir()]


def gen_csv(zh_dict, en_dict, output_path):
    # 将两个字典中key相同的项合并，并保存到新的字典中
    merged_dict = {}
    for key in zh_dict:
        if not re.search('[\u4e00-\u9fa5]', zh_dict[key]):
            # 不包含中文的保留部分不加入数据集中
            continue
        if key in en_dict:
            merged_dict[key] = {'zh': zh_dict[key], 'en': en_dict[key]}

    # 将合并后的字典转换成csv文件
    with open(output_path.joinpath('zh_en.csv'), mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['key', '中文', '英文'])
        for key in merged_dict:
            writer.writerow([key, merged_dict[key]['zh'], merged_dict[key]['en']])


for pack in list_dir('./tmp'):
    lang_zh = {}
    lang_en = {}
    for quest in list_dir(pack):
        tag = quest.parts[2]
        if tag.find('-en') != -1:
            lang_en = trans2lang(quest)
        elif tag.find('-zh') != -1:
            lang_zh = trans2lang(quest)
        elif tag.find('lang') != -1:
            for lang_path in quest.rglob("*.json"):
                print(lang_path)
                tag_lang = lang_path.parts[3]
                if tag_lang == 'en_us.json':
                    lang_en = get_lang(lang_path)
                elif tag_lang == 'zh_cn.json':
                    lang_zh = get_lang(lang_path)
        else:
            print('目录名出错或缺少任务文件')
            sys.exit(0)
    gen_csv(lang_zh, lang_en, pack)
