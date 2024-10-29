# text_process
##### 使用方法

找到主程序入口`if __name__ == "__main__"`中的

```python
    file_path = r'local_file_path'  # 替换为本地文件路径
```

将`local_file_path`替换为本地文件路径。

##### 目标效果

此程序试图实现三个效果：

1. 切割数据量庞大的原文档，以篇章为单位分别独立存储，方便进一步处理；

2. 消除正文之后、下划线之前的噪音，例如：

   > : Scientists; Collaboration; Cooperation; Diplomatic & consular services; Initiatives; Public health; Islamic countries; Pharmaceutical industry; Research & development--R & D; Chinese medicine; Natural products  
   > : : Pharmaceutical industry; : 92812 :‎ International Affairs 32541 :‎ Pharmaceutical and Medicine Manufacturing  
   > : China; Pakistan; Islamabad Pakistan  
   > : 92812: International Affairs; 32541: Pharmaceutical and Medicine Manufacturing  
   > : Promoting developing traditional medicine in OIC States  
   > : The Financial Daily; Karachi  
   > : 2023  
   > : Apr 28, 2023  
   > : ISLAMABAD  
   > : AsiaNet Pakistan (Pvt) Ltd.  
   > : Karachi  
   > /: Pakistan, Karachi  
   > : Business And Economics--Banking And Finance  
   > : English  
   > : News  
   > ProQuest  ID: 2806801246  
   > URL:   
   > : (c)2023 The Financial Daily  
   > : 2023-11-29  
   > : ABI/INFORM Collection 

3. 将独立存储的篇章处理为一句一行的形式。

##### 实现过程

注意到，噪音通常以如下形式出现：

> Scientists; Collaboration; Cooperation; Diplomatic & consular services

称为标签行，或：

> Source: Russian News Agency

称为来源行；而以固定形式结束，即长短不一的下划线：

```python
____________________
```

因此，基本思路是：

1. 预处理：将位于句首的空格、冒号、数字、句号等非文本符号替换为空字符串，忽略仅包含横线`-------`的行；

2. 识别噪音：使用下列函数找出噪音并消除，切割原文档为独立篇章，并处理为一句一行的形式。

| 函数名            | 效果                                               |
| ----------------- | -------------------------------------------------- |
| `is_label_line`   | 判断是否为标签行                                   |
| `is_source_line`  | 判断是否为来源行                                   |
| `is_noise_start`  | 判断是否为噪音的开始（即标签行或来源行）           |
| `is_noise_end`    | 判断是否为噪音的结束（即下划线行）                 |
| `split_sentences` | 使用`nltk`库，将独立存储的篇章处理为一句一行的形式 |
| `split_articles`  | 主函数，切割原文档为独立篇章                       |
| `save_articles`   | 存储`split_articles`的结果                         |

具体代码与相关解释如下：

```python
# 导入必需的库
import re
import os
import nltk

# 下载 punkt 分词器模型
nltk.download('punkt', quiet=True)

# 预处理函数
def preprocess_line(line):
    # 正则匹配位于句首的空格、句号、数字、冒号的任意组合
    pre_pattern = r'^[\s:0-9.]+'
    # 替换为空字符串
    line = re.sub(pre_pattern, "", line)
    # 忽略仅包含横线的行
    if not re.fullmatch(r'-+', line.strip()):
        # 删除位于句首的冒号、空格、数字，以及位于句末的换行符
        return line.lstrip(':').lstrip().lstrip('0123456789').lstrip().rstrip('\n')
    else:
        return ""	# 防止返回None报错

# 标签行函数
def is_label_line(line, after_noise_end):
    # 噪音后的第一行（即标题行）不参与标签行的匹配
    if after_noise_end:
        return False
    line = line.strip()
    # 包含多个分号的句子不参与匹配
    if any(punct in line for punct in '.!?"'):
        return False
    # 不包含分号的行不参与匹配
    if ';' not in line:
        return False
    return True

# 来源行函数，特征为source:开头
def is_source_line(line):
    return line.lower().startswith('source:')

def is_noise_start(line, after_noise_end):
    return is_label_line(line, after_noise_end) or is_source_line(line)

# 噪音结束函数，特征为任意数量的下划线
def is_noise_end(line):
    return bool(re.match(r'^\s*_+\s*$', line))

# 利用nltk库，一句一行
def split_sentences(text):
    sentences = nltk.tokenize.sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

# 主函数（切割篇章）
def split_articles(file_path):
    articles = []	# 统计篇章数量
    current_article_lines = []	# 临时列表，存储新篇章
    in_noise_section = False
    article_index = 1
    article_started = False  
    after_noise_end = False
	
    # 生成原文档编号后的新路径
    base_name = os.path.basename(file_path)
    modified_file_path = 'modified_' + base_name

    with open(file_path, 'r', encoding='utf-8') as f_in, open(modified_file_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            # 保留原文本行，传入modified_file生成编号后的文档
            original_line = line
            line = preprocess_line(line)
            # 若已知line为噪音，进行处理，否则判断是否为噪音
            if in_noise_section:
                f_out.write(original_line)
                # 若line为噪音结束，重置in_noise_section为False, after_noise_end为True, 并将临时列表current_article_lines中的元素粘贴为新的article
                if is_noise_end(line):
                    in_noise_section = False
                    after_noise_end = True  
                    article = '\n'.join(current_article_lines).strip()
                    # 编号新的article，作为一个元素放入articles以统计篇章数量
                    if article:
                        article = f'Article Number: {article_index}\n{article}'
                        articles.append(article)
                    current_article_lines = []	# 清空临时列表
                    article_index += 1
                    article_started = False	# 重置新篇章标记
            else:
                # 若line为噪音开始，重置in_noise_section为True, after_noise_end为False, 否则line不是噪音，判断是否为新篇章的开头
                if is_noise_start(line, after_noise_end):
                    in_noise_section = True
                    f_out.write(original_line)
                    after_noise_end = False
                else:
                    after_noise_end = False
                    # 临时列表清空后，首次执行if not语句会将article_started切换为True，随后直接执行current_article_lines.append(line)，直到新篇章结束
                    if not article_started:
                        f_out.write(f'Article Number: {article_index}\n')
                        article_started = True
                    # 到达这里的line即为正文行，传入临时列表
                    current_article_lines.append(line)
                    f_out.write(original_line)
                    
        # 处理可能残留的文本
        if current_article_lines:
            article = '\n'.join(current_article_lines).strip()
            if article:
                article = f'Article Number: {article_index}\n{article}'
                articles.append(article)
            if not article_started:
                f_out.write(f'\nArticle Number: {article_index}\n')
    return articles

# 分别独立存储切割后的篇章
def save_articles(articles):
    for idx, article in enumerate(articles, 1):
        lines = article.split('\n')
        article_number_line = lines[0]
        content_lines = lines[1:]
        content = '\n'.join(content_lines)

        sentences = []
        for para in content.split('\n'):
            sentences.extend(split_sentences(para))

        new_article = [article_number_line] + sentences

        with open(f'article_{idx}.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_article))

if __name__ == "__main__":
    file_path = r'local_file_path'  # 替换为本地文件路径
    articles = split_articles(file_path)
    save_articles(articles)
    print(f"获得{len(articles)}篇文章。")
```

