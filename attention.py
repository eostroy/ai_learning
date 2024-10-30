from transformers import BartTokenizerFast
from transformers import AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from captum.attr import LayerIntegratedGradients

model_name = 'facebook/bart-large-mnli'
tokenizer = BartTokenizerFast.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

comments = [
    "I love using Chinese herbal medicine for my digestion.",
    "I think acupuncture is very effective for pain relief.",
    "Western medicine is the best for treating diseases.",
    "I've been drinking TCM tea and feel much better.",
    "I don't trust traditional remedies.",
    "I hate America."
]


tcm_label = "relevant to traditional Chinese medicine"
not_tcm_label = "irrelevant to traditional Chinese medicine"

# 定义相关性函数
def is_tcm_related(sentence):
    premise = sentence
    hypothesis = "This text is about Traditional Chinese Medicine."
    inputs = tokenizer.encode_plus(premise, hypothesis, return_tensors='pt', truncation=True)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        entailment_score = probs[:, 2].item()
        print(f"Sentence: {sentence}")
        print(f"The entailment score: {entailment_score}")
    return entailment_score > 0.1

tcm_sentences = [s for s in comments if is_tcm_related(s)]

dimensions = ['affect', 'judgment', 'appreciation']

def classify_dimension(sentence):
    premise = sentence
    scores = {}
    for dim in dimensions:
        hypothesis = f"This text expresses {dim}."
        inputs = tokenizer.encode_plus(premise, hypothesis, return_tensors='pt', truncation=True)
        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']

        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            entailment_score = probs[:, 2].item()
        scores[dim] = entailment_score
    max_dim = max(scores, key=scores.get)
    return max_dim, scores

for sentence in tcm_sentences:
    dimension, scores = classify_dimension(sentence)
    print(f"Sentence: {sentence}")
    print(f"Label: {dimension}")
    print(f"Score: {scores}")

def get_token_importance(sentence, hypothesis):
    # 获取输入，并获取 offset_mapping
    inputs = tokenizer.encode_plus(
        sentence,
        hypothesis,
        return_tensors='pt',
        truncation=True,
        return_offsets_mapping=True
    )
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    offsets = inputs['offset_mapping'][0]

    # 找到前提和假设的分界点
    sep_token_id = tokenizer.eos_token_id
    sep_indices = (input_ids[0] == sep_token_id).nonzero(as_tuple=True)[0]
    if len(sep_indices) >= 1:
        premise_end = sep_indices[0].item() + 1
    else:
        premise_end = input_ids.size(1)

    # 定义前向钩子函数来捕获嵌入并保留梯度
    embedding_list = []

    def forward_hook(module, input, output):
        output.retain_grad()
        embedding_list.append(output)

    # 注册前向钩子
    embeddings_layer = model.model.encoder.embed_tokens
    handle = embeddings_layer.register_forward_hook(forward_hook)

    # 目标类别（假设为 2，即 entailment）
    target_class = 2

    # 前向传播
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    logits = outputs.logits
    loss = F.softmax(logits, dim=1)[0, target_class]

    # 清零梯度
    model.zero_grad()

    # 反向传播
    loss.backward()

    # 移除钩子
    handle.remove()

    # 获取嵌入和梯度
    embeddings = embedding_list[0].detach()  # (batch_size, seq_len, embed_dim)
    grads = embedding_list[0].grad  # (batch_size, seq_len, embed_dim)

    # 计算归因值：逐元素相乘并求和
    attributions = (embeddings * grads).sum(dim=-1).squeeze(0)

    # 归一化
    attributions = attributions / torch.norm(attributions)

    # 获取对应的 tokens
    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze(0))

    # 只关注前提部分的 tokens 和归因值
    premise_tokens = tokens[:premise_end]
    premise_attributions = attributions[:premise_end]

    # 过滤特殊 tokens，并处理子词
    words = []
    word_attributions = []
    current_word = ''
    current_attr = 0.0

    for token, attr in zip(premise_tokens, premise_attributions):
        # 检查是否为特殊 token
        if token in tokenizer.all_special_tokens:
            continue

        # 去除 BPE 前缀，如 'Ġ'
        clean_token = token.replace('Ġ', '').replace('▁', '')

        # 如果 token 以 '##' 开头，表示是子词的一部分
        if not token.startswith('Ġ') and not token.startswith('▁') and current_word != '':
            # 累加子词
            current_word += clean_token
            current_attr += attr.item()
        else:
            # 保存之前的词和归因值
            if current_word != '':
                words.append(current_word)
                word_attributions.append(current_attr)
            # 开始新的词
            current_word = clean_token
            current_attr = attr.item()

    # 添加最后一个词
    if current_word != '':
        words.append(current_word)
        word_attributions.append(current_attr)

    # 创建词语贡献度字典
    token_importances = {word: attrib for word, attrib in zip(words, word_attributions)}
    return token_importances

# 计算贡献率
for sentence in tcm_sentences:
    dimension, scores = classify_dimension(sentence)
    hypothesis = f"This text expresses {dimension}."
    token_importances = get_token_importance(sentence, hypothesis)
    max_token = max(token_importances, key=token_importances.get)
    print(f"Sentence: {sentence}")
    print(f"Label: {dimension}")
    print(f"The most significant word: {max_token}")
    print(f"Contribution: {token_importances}")