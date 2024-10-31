# text_process

`text_dividing`用于将原始语料切割为单独篇章，同时去除噪音；`deepseek_api`包括了判断话题相关性的`review_relevance`和自动态度标注的`direct_annotation`, `detailed_annotation`；`articles`存储了原始语料。

### text_dividing使用方法

找到主程序入口`if __name__ == "__main__"`中的

```python
    file_path = r'local_file_path'
```

将`local_file_path`替换为本地文件路径。需要注意的是，切割后的篇章会存储在`text_dividing`所在的文件夹内。例如，如果脚本的路径是：

> C:\Users\15332\Desktop\data_processing\data_dividing.py

那么所有的篇章`article_n`都会位于`C:\Users\15332\Desktop\data_processing`文件夹中，因此请在执行脚本前，将其放在单独的文件夹中。同时，每次执行脚本都会复写先前的结果。

### deepseek_api使用方法

找到

```python
client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.deepseek.com"
)
```

将`your_api_key`替换为你的api key；

找到

```python
    directory = r'local_file_path'
```

或

```python
    directory = r'local_folder_path'
```

将`local_file_path`或`local_folder_path`替换为本地文件/文件夹路径。对于后者，生成的文件将存储在`directory`指向的文件夹中。
