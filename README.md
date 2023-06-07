# minecraft-modpack-quests-transformer
1.提取已汉化的整合包任务文件生成数据集
2.使用数据集微调[transformer预训练模型](https://huggingface.co/Helsinki-NLP/opus-mt-en-zh)以优化在mc术语上的表现。
# 使用说明
  这个项目不是针对所有人的，需要你有一定的机器学习基础，整体上代码逻辑并不复杂且留下了部分注释。
## 数据集
几个推荐的优质数据获取处
- [CFPA-Modpack](https://modpack.cfpa.team/) (比较陈旧，少数使用了ftbquest模组的整合包汉化可以使用)
- [安逸菌汉化](http://www.anyijun.com/zhcn/) 
- [VM汉化组](https://space.bilibili.com/2085089798/article)

除此之外你可以使用CFPA官方的术语库并将其处理为csv格式后直接使用

不过并不建议采用这种方式，因为很多术语是多义词缺少完整的语境直接训练会覆盖掉通用翻译
- [i18n-dict](https://github.com/CFPATools/i18n-dict) 

PS:推荐使用mini版本并进行数据清洗后使用

## 应用
- 微调主要是为了让它避免诸如'暴徒'、'产卵'、'香草'之类的典型术语翻译错误，来让它在涉及mc或者mc模组的长文本翻译上表现更好一些，不用指望它能替代人工翻译
- 如果你想使用你所训练完的模型参照，predict目录下的程序，只需要两行代码就可以调用你所训练好的模型，更多应用你可以参考[HuggingFace-Doc](https://huggingface.co/docs/transformers/index)来获取帮助
## 模型
如果你的硬件配置不够，你可以基于huggingface平台进行托管训练，点击左上角的Train使用AutoTrain即可

**我已使用网络上搜集而来的数据(大约一百万条数据的训练集）完成了一份微调后的模型[XDawned/minecraft-en-zh](https://huggingface.co/XDawned/minecraft-en-zh)并实现了应用[FTBQLocalizationTools](https://github.com/XDawned/FTBQLocalizationTools/tree/model_trans)，它的代码完全开源的或许会对你有所启发**

## PS
此项目是对翻译模型的微调，借由诸多工作者们的方法封装与模型开源，整体技术难点不多。
