import re
import os
import nltk

nltk.download('punkt', quiet=True)

def preprocess_line(line):
    pre_pattern = r'^[\s:0-9.]+'
    line = re.sub(pre_pattern, "", line)
    if not re.fullmatch(r'-+', line.strip()):
        return line.lstrip(':').lstrip().lstrip('0123456789').lstrip().rstrip('\n')
    else:
        return ""

def is_label_line(line, after_noise_end):
    if after_noise_end:
        return False
    line = line.strip()
    if any(punct in line for punct in '.!?"'):
        return False
    if ';' not in line:
        return False
    return True

def is_source_line(line):
    return line.lower().startswith('source:')

def is_noise_start(line, after_noise_end):
    return is_label_line(line, after_noise_end) or is_source_line(line)

def is_noise_end(line):
    return bool(re.match(r'^\s*_+\s*$', line))

def split_sentences(text):
    sentences = nltk.tokenize.sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

def split_articles(file_path):
    articles = []
    current_article_lines = []
    in_noise_section = False
    article_index = 1
    article_started = False  
    after_noise_end = False

    base_name = os.path.basename(file_path)
    modified_file_path = 'modified_' + base_name

    with open(file_path, 'r', encoding='utf-8') as f_in, open(modified_file_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            original_line = line
            line = preprocess_line(line)
            if in_noise_section:
                f_out.write(original_line)
                if is_noise_end(line):
                    in_noise_section = False
                    after_noise_end = True  
                    article = '\n'.join(current_article_lines).strip()
                    if article:
                        article = f'Article Number: {article_index}\n{article}'
                        articles.append(article)
                    current_article_lines = []
                    article_index += 1
                    article_started = False
            else:
                if is_noise_start(line, after_noise_end):
                    in_noise_section = True
                    f_out.write(original_line)
                    after_noise_end = False
                else:
                    after_noise_end = False
                    if not article_started:
                        f_out.write(f'Article Number: {article_index}\n')
                        article_started = True
                    current_article_lines.append(line)
                    f_out.write(original_line)

        if current_article_lines:
            article = '\n'.join(current_article_lines).strip()
            if article:
                article = f'Article Number: {article_index}\n{article}'
                articles.append(article)
            if not article_started:
                f_out.write(f'\nArticle Number: {article_index}\n')
    return articles

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