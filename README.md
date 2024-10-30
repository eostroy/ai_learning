# text_process
### text_dividing使用方法

找到主程序入口`if __name__ == "__main__"`中的

```python
    file_path = r'local_file_path'
```

将`local_file_path`替换为本地文件路径。

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

将`local_file_path`或`local_folder_path`替换为本地文件/文件夹路径。
