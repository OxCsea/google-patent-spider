import pandas as pd
import requests
from bs4 import BeautifulSoup

# 加载数据
data = pd.read_csv("../data/patent_info.csv", encoding="utf-8")

# 定义被引数据
cited_output = "../data/patent_cited.csv"
columns = ['orgNum', 'cpubNum', 'ctitle', 'citeURL', 'cpriorityDate', 'cpublicationDate', 'cassigneeOriginal']
citedDF = pd.DataFrame(columns=columns)  # 使用表头创建一个空的 DataFrame
citedDF.to_csv(cited_output, mode='w', index=False, header=True, encoding="utf-8")

# 定义专利内容
patent_output = "../data/patent_content.csv"
columns = ['id', 'title', 'assignee', 'author', 'priorityDate', 'filingDate', 'publicationDate', 'grantDate', 'url', 'abstract', 'label', 'desp', 'citedNum']
patentDF = pd.DataFrame(columns=columns)  # 使用表头创建一个空的 DataFrame
patentDF.to_csv(patent_output, mode='w', index=False, header=True, encoding="utf-8")

proxies = {
    'http':'http://127.0.0.1:7890',
    'https':'http://127.0.0.1:7890'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Connection':'close'
}

# 遍历每一行数据
# 'id', 'title', 'assignee', 'author', 'priorityDate', 'filingDate', 'publicationDate', 'grantDate', 'url'

wrong_id = []
patent_num = 0

for index, row in data.iterrows():
    try:
        # 获取每行的字段值
        id = row['id']
        title = row['title']
        assignee = row['assignee']
        author = row['author']
        priorityDate = row['priorityDate']
        filingDate = row['filingDate']
        publicationDate = row['publicationDate']
        grantDate = row['grantDate']
        url = row['url']

        response = requests.get(url, headers=headers, proxies=proxies, timeout=10, verify=False)
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "html.parser")
        abstract = ""
        label = ""
        desp = ""
        citedNum = 0
        # 1.爬取 Abstract
        abstract_section = soup.find('section', itemprop='abstract')
        if abstract_section:
            abstract_div = abstract_section.find('div', class_='abstract')
            if abstract_div:
                abstract = abstract_div.get_text(strip=True)  # 获取纯文本内容

        # 2.抓取 Description 和 code
        # 定位 Classifications 的 section
        classifications_section = soup.find('h2', text='Classifications')
        if classifications_section:
            classifications_section = classifications_section.find_next('ul')
            if classifications_section:
                # 获取第一个 <ul> 中第一个 <li> 的最后一个 <li>
                first_ul = classifications_section.find('ul', attrs={'itemprop': 'classifications'})
                if first_ul:
                    last_li = first_ul.find_all('li')[-1]
                    if last_li:
                        # 提取最后一个 <li> 中的 <span itemprop="Description">
                        description = last_li.find('span', attrs={'itemprop': 'Description'})
                        # <span itemprop="Code">H02J7/0018
                        code = last_li.find('span', attrs={'itemprop': 'Code'})
                        if description:
                            desp = description.get_text(strip=True)
                            label = code.get_text(strip=True)
                    

        # 3.被引指数
        # 提取 Cited Number (e.g., 14)
        citing_header = soup.find('h2', string=lambda text: text and "Families Citing this family" in text)
        if citing_header:
            citedNum = int(citing_header.text.split('(')[-1].split(')')[0])
            # print(f"Cited Number: {citedNum}")
        
        patentData = []
        patentData.append({
            "id": id,
            "title": title,
            "assignee": assignee,
            "author" : author,
            "priorityDate" : priorityDate,
            "filingDate" : filingDate,
            "publicationDate" : publicationDate,
            "grantDate" : grantDate,
            "url" : url,
            "abstract": abstract,
            "label": label,
            "desp": desp,
            "citedNum": citedNum
        })
        # 将数据存入 DataFrame
        patentDF = pd.DataFrame(patentData)
        patentDF.to_csv(patent_output, mode='a', index=False, header=False, encoding="utf-8")
        print(id+" ==> 内容爬取完毕")
        
        # 4.被引数据
        rows = soup.find_all('tr', itemprop="forwardReferencesFamily")  # 找到表格中符合条件的每一行
        citeData = []
        for row in rows:
            # 提取每行的数据
            citeURL = row.find('a')['href'] if row.find('a') else None
            cpubNum = row.find('span', itemprop="publicationNumber").text if row.find('span', itemprop="publicationNumber") else None
            cpriorityDate = row.find('td', itemprop="priorityDate").text if row.find('td', itemprop="priorityDate") else None
            cpublicationDate = row.find('td', itemprop="publicationDate").text if row.find('td', itemprop="publicationDate") else None
            cassigneeOriginal = row.find('span', itemprop="assigneeOriginal").text if row.find('span', itemprop="assigneeOriginal") else None
            ctitle = row.find('td', itemprop="title").text.strip() if row.find('td', itemprop="title") else None

            # 拼接完整的 citeURL
            full_citeURL = f"https://patents.google.com{citeURL}" if citeURL else None

            # 将数据添加到列表
            citeData.append({
                "orgNum":id,
                "cpubNum": cpubNum,
                "ctitle": ctitle,
                "citeURL": full_citeURL,
                "cpriorityDate": cpriorityDate,
                "cpublicationDate": cpublicationDate,
                "cassigneeOriginal": cassigneeOriginal
            })
        # 将数据存入 DataFrame
        citedDF = pd.DataFrame(citeData)
        citedDF.to_csv(cited_output, mode='a', index=False, header=False, encoding="utf-8")
        print(id+"  ==> 被引爬取完毕")
        patent_num = patent_num + 1
    except Exception as e:
        print(f"{id} ==> 请求过程中发生错误：{e}")
        wrong_id.append({"id":id})
        continue

wrong_df = pd.DataFrame(wrong_id)
wrong_df.to_csv("./data/wrong_patent.csv", mode='w', index=True, header=True, encoding="utf-8")
print(f"一共成功爬取 {patent_num} 专利数据")

