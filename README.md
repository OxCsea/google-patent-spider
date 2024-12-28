# Google-Patent-Spider

## 1. Introduction

基于Python爬取指定领域专利信息。

- 专利数据。爬取字段：专利号，标题，摘要，作者，机构，申请时间，公开时间，授权时间，专利分类号，分类号对应描述，被引量，专利原文下载链接。id,title,assignee,author,priorityDate,filingDate,publicationDate,grantDate,url,abstract,label,desp,citedNum

- 专利引用情况。爬取字段：被引专利号，被引专利标题，被引专利机构，被引专利作者，被引专利公开日期，被引专利摘要，引用专利号，引用专利标题，引用专利摘要，引用专利机构，引用专利原文链接，引用专利申请时间，引用专利公开时间，引用专利授权时间，引用专利分类号

  orgNum,cpubNum,ctitle,citeURL,cpriorityDate,cpublicationDate,cassigneeOriginal

- 专利内容向量。对专利标题+摘要进行词向量转化。

  id,title,assignee,abstract,label,desp,citedNum,cpc,filingDate,publicationDate,content,embedding

- 专利技术提取。基于专利内容进行技术提取。

  id,title,assignee,abstract,label,desp,citedNum,cpc,keyTech

## 2. Environment 

Python=3.10.x

## 3. Structure

- code

  - patent-spider.py
    - 爬取专利内容信息和被引信息。
  - patent-content-embed.py
    - 计算title+abstract=content的embedding
  - patent-keyTech-extract.py
    -  基于专利摘要提取技术keyTech
  - patent-keyTech-embed.py
    - 计算keyTech的embedding

- data

  - patent-info.csv

    > 从google patent输入检索词检索都导出的专利信息文件，用于后续内容爬取。

## 4. Usage

1. 从google patent输入检索词检索都导出的专利信息文件存入patent-info.csv
2. 运行patent-spider.py爬取对应专利信息
3. 根据需要对专利内容和关键技术进行提取和向量化转换。

## 5. Contact

Created by [OxCsea](https://github.com/OxCsea) - feel free to reach out!

> https://t.me/magic_Cxsea