from transformers import MarianTokenizer, MarianMTModel

# 查看所训练模型的术语翻译效果

# 要翻译的文字
line = 'Runic Altar'

# 将下方地址参数修改为你训练出来的模型地址
tokenizer = MarianTokenizer.from_pretrained("../fine-tune/results/checkpoint-1000")
model = MarianMTModel.from_pretrained("../fine-tune/results/checkpoint-1000")


input_ids = tokenizer.encode(line, return_tensors="pt")
translated = model.generate(input_ids, max_length=128)
output = tokenizer.decode(translated[0], skip_special_tokens=True)
print(output)