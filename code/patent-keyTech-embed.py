import pandas as pd
import torch
import numpy as np
import os
from transformers import BertTokenizer, BertModel
import csv 

# 对专利中抽取出的keyTech进行embedding

# 设置工作目录为当前脚本所在路径
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 确认当前工作目录
print(f"Current working directory: {os.getcwd()}")

patent_path = "../data/patent_topic_keyTech.csv"
patent_df = pd.read_csv(patent_path, encoding="utf-8")

# 加载模型和tokenizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("model loading....")
# os.environ["HF_ENDPOINT"]="https://hf-mirror.com"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"

model_name = "hfl/chinese-bert-wwm-ext"  # 模型名称
model = BertModel.from_pretrained(model_name)
tokenizer = BertTokenizer.from_pretrained(model_name)
print("model has been loaded....")

def get_embeddings(texts, tokenizer, model, device, max_length=256):
    # 使用tokenizer将文本编码
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=max_length, return_tensors="pt").to(device)
    
    # 获取模型的输出（hidden states）
    with torch.no_grad():
        outputs = model(**inputs)
        
    # 获取最后一层的 hidden state
    embeddings = outputs.last_hidden_state.mean(dim=1)  # 获取句子级别的embedding，可以取平均值
    return embeddings

def save_embeddings_to_csv(input_df, output_csv_path, tokenizer, model, device):
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 写入 CSV 表头
        writer.writerow(list(input_df.columns) + ['keyEmb'])

        # 遍历每一行
        for _, row in input_df.iterrows():
            content = row['keyTech']
            # 获取当前行的嵌入
            embedding = get_embeddings([content], tokenizer, model, device).cpu().numpy().tolist()[0]
            # 写入当前行数据和嵌入向量
            writer.writerow(list(row) + [embedding])
            print(row['id']+" ===> finish")

# 保存嵌入到 CSV 文件
save_embeddings_to_csv(
    patent_df,
    '../data/patent_keyTech_embed.csv',
    tokenizer,
    model,
    device
)
