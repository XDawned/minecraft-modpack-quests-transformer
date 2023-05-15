import datasets
import evaluate
import pandas as pd
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer

# 微调预训练模型,并将最佳模型保存至results下
# 首次使用会先下载预训练翻译模型至C:\Users\你的用户名\.cache\huggingface\hub下
# 强烈建议使用GPU进行训练，需自行配置torch与cuda依赖环境
# 使用CPU不仅训练速度慢而且可能会出现意想不到的错误
# 出现cuda out of memory报错代表显存溢出
# 可以尝试降低bath-size或切换更好的设备
# 或者将数据集拆分分多次训练，虽然这样可能降低训练效果



modelName = "Helsinki-NLP/opus-mt-en-zh"
tokenizer = AutoTokenizer.from_pretrained(modelName)
model = AutoModelForSeq2SeqLM.from_pretrained(modelName)

# 检测cuda是否安装，未安装则使用cpu训练
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model = model.to(device)

df = pd.read_csv('my_data.csv', usecols=['source', 'target'])  # 修改此处my_data.csv为你要训练的数据集

# 清除无效数据
df = df.dropna(subset=['source'])
df = df.dropna(subset=['target'])

dataset = datasets.DatasetDict({
    "train": datasets.Dataset.from_pandas(df)
})

# 随机打乱，取1/5为测试集
dataset = dataset["train"].train_test_split(test_size=0.2)


def preprocess_function(examples):
    inputs = [example for example in examples["source"]]
    targets = [example for example in examples["target"]]
    model_inputs = tokenizer(inputs, text_target=targets, max_length=128, truncation=True)
    return model_inputs


tokenized_datasets = dataset.map(preprocess_function, batched=True)
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=modelName)

metric = evaluate.load("sacrebleu")


def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]

    return preds, labels


def compute_metrics(eval_preds):
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

    result = metric.compute(predictions=decoded_preds, references=decoded_labels)
    result = {"bleu": result["score"]}

    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    result["gen_len"] = np.mean(prediction_lens)
    result = {k: round(v, 4) for k, v in result.items()}
    return result


training_args = Seq2SeqTrainingArguments(
    output_dir="./results",  # 模型存放地
    evaluation_strategy="epoch",
    learning_rate=2e-5,

    # 如果显存较大这两处参数可以调高，提高训练速度，建议向上依次*2
    # 显存较小则调低，依次/2
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,

    weight_decay=0.01,
    save_total_limit=3,

    # 训练的轮数，多轮更容易找到bleu分数较高的模型
    num_train_epochs=10,

    predict_with_generate=True,
    fp16=True if device == 'cuda' else False,   # 只有gpu环境才可以使用混合精度
    push_to_hub= False,
)
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test'],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)
trainer.train()
