# minecraft-modpack-quests-transformer
提取已汉化整合包任务文件生成数据集，并基于其对transformer预训练模型进行专门强化。  公有云

## 数据集
因涉及公私问题不予公开,但分享几个获取数据集的方式
- [i18n-dict](https://github.com/CFPATools/i18n-dict) 推荐使用mini版本并进行数据清洗后使用
- [CFPA-Modpack](https://modpack.cfpa.team/) 比较陈旧，少数使用了ftbquest模组的整合包汉化可以使用
- [安逸菌汉化](http://www.anyijun.com/zhcn/) 
## 模型
初期阶段，受限于硬件性能，暂时使用huggingface平台训练并托管[minecraft-modpack-quests-transformer](https://huggingface.co/XDawned/minecraft-modpack-quests-transformer)
- 基于预训练模型[opus-mt-en-zh](https://huggingface.co/Helsinki-NLP/opus-mt-en-zh)强化而来
- 建议本地部署调用
