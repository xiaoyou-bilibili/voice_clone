import json
import os
import random
import shutil

path = "/home/xiaoyou/code/ai/dataset/voice/aidatatang_200zh/corpus"


# 处理数据集
def read_data():
    with open("test.txt", "w") as f:
        for people in os.listdir("{}/test".format(path)):
            num = people[1:]
            for file in os.listdir("{}/test/{}".format(path, people)):
                if file.endswith("txt"):
                    name = file[:-4]
                    shutil.copy("{}/test/{}/{}.wav".format(path, people, name), "voice/{}.wav".format(name))
                    f.write("./voice/{}.wav|{}\n".format(name, num))
                    print(name)


def read_file():
    people = {}
    with open("test_sort.txt", "w") as f2:
        with open("train_sort.txt", "w") as f3:
            with open("test.txt") as f4:
                with open("train.txt") as f5:
                    trains = f4.read().split("\n")
                    tests = f5.read().split("\n")
                    for name in trains:
                        if len(name.split("|")) == 2:
                            num = name.split("|")[1]
                            people[num] = len(people)
                    for name in tests:
                        if len(name.split("|")) == 2:
                            num = name.split("|")[1]
                            people[num] = len(people)
                    print(people)
                    for name in trains:
                        if len(name.split("|")) == 2:
                            names = name.split("|")
                            f3.write("{}|{}\n".format(names[0], people[names[1]] - 1))
                    for name in tests:
                        if len(name.split("|")) == 2:
                            names = name.split("|")
                            f2.write("{}|{}\n".format(names[0], people[names[1]] - 1))


src = "/home/xiaoyou/code/ai/dataset/yuanshen2"

from shutil import copyfile


# 转换原神数据集
def read_genshin():
    with open("{}/result_merged.json".format(src)) as f:
        data = json.loads(f.read())
        for people in data:
            info = data[people]
            if info['language'] == 'CHS':
                if 'npcName' in info:
                    # 先创建文件
                    name = info['npcName']
                    file = str(info['fileName'])
                    file = file.replace("\\", "/")
                    if not os.path.exists("{}/{}".format(src, file)):
                        file = file.replace(".wem", ".wav")
                        if not os.path.exists("{}/{}".format(src, file)):
                            print("文件不存在", "{}/{}".format(src, file))
                            continue

                    txt = info['text']
                    path = "{}/voice/{}".format(src, name)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    # 拷贝角色声音文件
                    copyfile("{}/{}".format(src, file), "{}/{}".format(path, file.split("/")[-1]))
                    with open("{}/{}.txt".format(path, file.split("/")[-1]), "w") as f:
                        f.write(txt)
                    print(info)


# 随机拷贝150条角色数据
def convert_role():
    src = "/home/xiaoyou/code/ai/dataset/yuanshen2/voice"
    peoples = ["派蒙", "可莉", "香菱", "七七", "丽莎", "胡桃", "琴", "凝光", "芭芭拉", "安柏",
               "云堇", "刻晴", "砂糖", "甘雨", "雷电将军", "凯亚", "行秋", "温迪", "迪卢克", "钟离"]

    index = 1
    for people in peoples:
        path = "voice/{}".format(index)
        if not os.path.exists(path):
            os.mkdir(path)
        files = os.listdir("{}/{}".format(src, people))
        total = 0
        for file in files:
            if file.endswith(".wav"):
                total += 1
                if total == 501:
                    break
                copyfile("{}/{}/{}".format(src, people, file), "{}/{}.wav".format(path, total))
                print(file)
        index += 1


# 转换一下声音
def get_train():
    data = []
    for path in os.listdir("data"):
        for voice in os.listdir("data/{}".format(path)):
            data.append("./data/{}/{}|{}".format(path, voice, int(path) - 1))
    random.shuffle(data)
    sp = int(len(data) * 0.8)
    with open("train.txt", "w") as f:
        f.write("\n".join(data[:sp]))
    with open("val.txt", "w") as f:
        f.write("\n".join(data[sp:]))
    print(data)


if __name__ == '__main__':
    # get_train()
    peoples = ["派蒙", "可莉", "香菱", "七七", "丽莎", "胡桃", "琴", "凝光", "芭芭拉", "安柏",
               "云堇", "刻晴", "砂糖", "甘雨", "雷电将军", "凯亚", "行秋", "温迪", "迪卢克", "钟离"]
    for index in range(0,21):
        print('<input type="radio" name="role" value="{}" title="{}" />'.format(index, peoples[index]))