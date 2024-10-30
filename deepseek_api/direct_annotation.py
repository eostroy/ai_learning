# 执行此程序，将获得直接的结论
import os
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.deepseek.com"
)

def check_documents_relevance(documents, topic):
    results = []
    for doc_path in documents:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        messages = [
            {
                "role": "user",
                "content": f"Is the following document related to the topic '{topic}'? Answer yes or no.\n\nDocument:\n{content}"
            }
        ]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )

        answer = response.choices[0].message.content.strip().lower()
        is_related = 'yes' in answer

        print(f"Document '{doc_path}' is related to the topic '{topic}': {is_related}")

        if is_related:
            analyze_sentences(doc_path, content)

        results.append((doc_path, is_related))

    return results

def analyze_sentences(doc_path, content):
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk.tokenize import sent_tokenize

    sentences = sent_tokenize(content)

    annotated_sentences = []

    for sentence in sentences:
        messages = [
            {
                "role": "user",
                "content": (
                    "According to Martin's Appraisal Theory, classify the following sentence into one of the three dimensions: "
                    "'affect', 'judgment', or 'appreciation'. "
                    "For 'affect', specify whether it belongs to 'un/happiness', 'dis/satisfaction', 'in/security', and/or 'dis/inclination'."
                    "For 'judgment', specify whether it belongs to normality, capacity, tenacity, propriety, veracity, and/or unclear."
                    "For 'appreciation', specify whether it belongs to reaction, composition, and/or social-valuation."
                    "Then, identify the words and phrases that contribute most to the classification. "
                    "It is allowed to provide more than one dimension, word and/or phrase."
                    "It is also allowed to provide no dimension if none of the dimensions can be related to the sentence."
                    "Provide the dimension(s) and the most significant words and/or praises only.\n\n"
                    f"Sentence:\n{sentence}"
                )
            }
        ]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )

        analysis = response.choices[0].message.content.strip()
        annotated_sentences.append((sentence, analysis))

    annotated_file_path = f"{doc_path}_annotated.txt"
    with open(annotated_file_path, 'w', encoding='utf-8') as f:
        for sentence, analysis in annotated_sentences:
            f.write(f"Sentence: {sentence}\nAnalysis: {analysis}\n\n")

    print(f"Annotated sentences saved to '{annotated_file_path}'.")

def get_documents_from_directory(directory):
    documents = []
    for filename in os.listdir(directory):
        doc_path = os.path.join(directory, filename)
        if os.path.isfile(doc_path) and doc_path.endswith('.txt'):
            documents.append(doc_path)
    return documents

if __name__ == "__main__":
    directory = r'local_folder_path'
    topic = "the overseas acceptance of traditional Chinese medicine (TCM); how non-Chinese people think of traditional Chinese medicine"
    documents = get_documents_from_directory(directory)
    results = check_documents_relevance(documents, topic)
