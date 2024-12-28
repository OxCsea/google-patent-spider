import pandas as pd
import re
import logging

# 基于摘要进行技术提取
def get_abstract_tech(id, abstract):
    # 定义第一个正则表达式，用于提取“一种”和（“方式”|“技术”|“方法” 或标点符号）之间的文本
    pattern_1 = r"一种(.*?)((方式|技术|方法|[，。；]))"

    # 定义第二个正则表达式，用于提取“基于”后面的内容
    pattern_2 = r"(基于|用于)(.*?)([，。；])"
    pattern_3 = r"(提供|提供了|提出|提出了|涉及|涉及了|公开|公开了)(.*?)((方式|技术|方法|[，。；]))"
    
    # 第一个正则表达式提取第一个匹配的文本
    match_1 = re.search(pattern_1, abstract)
    not_find = 0
    keyword = ""
    if match_1:
        keyword = match_1.group(1).strip()  # 获取“一种”和标点符号之间的文本
        # print(f"提取的主题：{keyword}")
        
        # 对tmp进一步应用第二个正则表达式，提取出“基于”后面的内容
        match_2 = re.search(pattern_2, keyword)
        if match_2:
            base_content = match_2.group(2).strip()  # 获取“基于”后面的文本 
            # 检查“基于”后面是否有“的”，如果有，则提取“的”后面的内容
            if '的' in base_content:
                # 提取“的”后面的内容
                base_content = base_content.split('的', 1)[-1].strip()
                keyword = base_content
    
    elif(re.search(pattern_3, abstract)):
        match_3 = re.search(pattern_3, abstract)
        if match_3:
            keyword = match_3.group(2).strip()  # 获取“一种”和标点符号之间的文本

            # 对tmp进一步应用第二个正则表达式，提取出“基于”后面的内容
            match_2 = re.search(pattern_2, keyword)
            if match_2:
                base_content = match_2.group(2).strip()  # 获取“基于”后面的文本 
                # 检查“基于”后面是否有“的”，如果有，则提取“的”后面的内容
                if '的' in base_content:
                    # 提取“的”后面的内容
                    base_content = base_content.split('的', 1)[-1].strip()
                    keyword = base_content
    else:
        match_2 = re.search(pattern_2, abstract)
        if match_2:
            base_content = match_2.group(2).strip()  # 获取“基于”后面的文本 
            # 检查“基于”后面是否有“的”，如果有，则提取“的”后面的内容
            if '的' in base_content:
                # 提取“的”后面的内容
                base_content = base_content.split('的', 1)[-1].strip()
                keyword = base_content
        else:
            not_find = 1
            print(f"{id} 没有提取出keyword")
            
    return keyword, not_find


def get_techList(tech_df):
    # 创建一个空列表，用于存储所有行的关键词
    keylist = []

    not_find_sum = 0

    # 遍历 DataFrame 的每一行
    for _, row in tech_df.iterrows():
        # 获取当前行的 id 和 abstract
        id = row['id']
        abstract = row['abstract']
        
        # 调用 get_abstract_tech 函数，得到关键词
        keyword, not_find_cnt = get_abstract_tech(id, abstract)
        not_find_sum = not_find_sum + not_find_cnt
        # 将关键词添加到 keylist 列表中
        keylist.append(keyword)

    # 将 keylist 列表作为新的列 "keyTech" 添加到 DataFrame
    # tech_df['keyTech'] = keylist
    return keylist, not_find_sum


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("keyTech.log", mode='a')
    ]
)

logger = logging.getLogger("keyTechLogger")

clus_path = "../data/patent_topic_n_cluster_simple.csv"
cluster_df = pd.read_csv(clus_path)

keylist, not_find_sum = get_techList(cluster_df)
logger.info("%s : 没有提取出来", not_find_sum)
cluster_df['keyTech'] = keylist
cluster_df.to_csv("../data/patent_topic_keyTech.csv", index=False, header=True, encoding="utf-8")
cluster_df.to_excel("../data/patent_topic_keyTech.xlsx", index=False, header=True)
logger.info("完成全部技术提取")