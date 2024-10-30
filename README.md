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
