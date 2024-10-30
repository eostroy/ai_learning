# 使用bart-large-mnli并结合attention机制进行zero-shot classification，但效果不佳，仅供参考

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

    sep_token_id = tokenizer.eos_token_id
    sep_indices = (input_ids[0] == sep_token_id).nonzero(as_tuple=True)[0]
    if len(sep_indices) >= 1:
        premise_end = sep_indices[0].item() + 1
    else:
        premise_end = input_ids.size(1)

    embedding_list = []

    def forward_hook(module, input, output):
        output.retain_grad()
        embedding_list.append(output)

    embeddings_layer = model.model.encoder.embed_tokens
    handle = embeddings_layer.register_forward_hook(forward_hook)

    target_class = 2

    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    logits = outputs.logits
    loss = F.softmax(logits, dim=1)[0, target_class]

    model.zero_grad()

    loss.backward()

    handle.remove()

    embeddings = embedding_list[0].detach()  # (batch_size, seq_len, embed_dim)
    grads = embedding_list[0].grad  # (batch_size, seq_len, embed_dim)

    attributions = (embeddings * grads).sum(dim=-1).squeeze(0)

    attributions = attributions / torch.norm(attributions)

    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze(0))

    premise_tokens = tokens[:premise_end]
    premise_attributions = attributions[:premise_end]

    words = []
    word_attributions = []
    current_word = ''
    current_attr = 0.0

    for token, attr in zip(premise_tokens, premise_attributions):
        if token in tokenizer.all_special_tokens:
            continue

        clean_token = token.replace('Ġ', '').replace('▁', '')

        if not token.startswith('Ġ') and not token.startswith('▁') and current_word != '':
            current_word += clean_token
            current_attr += attr.item()
        else:
            if current_word != '':
                words.append(current_word)
                word_attributions.append(current_attr)
            current_word = clean_token
            current_attr = attr.item()

    if current_word != '':
        words.append(current_word)
        word_attributions.append(current_attr)

    token_importances = {word: attrib for word, attrib in zip(words, word_attributions)}
    return token_importances

for sentence in tcm_sentences:
    dimension, scores = classify_dimension(sentence)
    hypothesis = f"This text expresses {dimension}."
    token_importances = get_token_importance(sentence, hypothesis)
    max_token = max(token_importances, key=token_importances.get)
    print(f"Sentence: {sentence}")
    print(f"Label: {dimension}")
    print(f"The most significant word: {max_token}")
    print(f"Contribution: {token_importances}")
