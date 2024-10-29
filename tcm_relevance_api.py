from openai import OpenAI
import os

client = OpenAI(
    api_key="sk-71ffb35e193e46d8acbb2817617e9401",
    base_url="https://api.deepseek.com"
)

def check_documents_relevance(documents, topic):
    results = []
    for doc_path in documents:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        messages = [
            {"role": "user", "content": f"Is the following document related to the topic '{topic}'?\n\nDocument: {content}\n\nAnswer yes or no."}
        ]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )

        answer = response.choices[0].message.content.strip().lower()
        is_related = 'yes' in answer

        results.append((doc_path, is_related))

        print(f"Document '{doc_path}' is related to the topic '{topic}': {is_related}")

    return results

def get_documents_from_directory(directory):
    documents = []
    for filename in os.listdir(directory):
        doc_path = os.path.join(directory, filename)
        if os.path.isfile(doc_path) and doc_path.endswith('.txt'):
            documents.append(doc_path)
    return documents

if __name__ == "__main__":
    directory = r'C:\Users\15332\Desktop\data_processing'
    topic = "the overseas influence or discussions of traditional Chinese medicine (TCM) itself, how people overseas think of it"
    documents = get_documents_from_directory(directory)
    results = check_documents_relevance(documents, topic)