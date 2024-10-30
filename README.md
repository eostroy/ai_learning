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

