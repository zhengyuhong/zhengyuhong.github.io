Use case: scientific-educational
Asset type: paper illustrated note, vertical 2:3 sketchnote page
Primary request: Create page 3 of a Chinese sketchnote explaining fine-grained expert segmentation in DeepSeekMoE.

【类型】核心机制细节图 / before-after 对比
【风格】sketchnote, 温暖科研手抄报风
【语言】中文为主，保留 GShard, DeepSeekMoE, Top-2, Top-8, FFN 等术语
【画幅】竖版 2:3，高清，所有文字清晰可读

【页面主题】
机制一：细粒度专家切分

【视觉结构】
- 顶部标题：“机制一：把大专家切成小专家”
- 左半边画传统 GShard：
  - 16 个较大的专家方块，标注“N = 16 大专家”
  - router 只连向 2 个专家，标注“Top-2”
  - 大专家内部画混杂的小知识符号：数学、代码、中文、常识混在一个框里，标注“知识混杂”
  - 下方写“组合数 C(16,2)=120”
- 右半边画 DeepSeekMoE：
  - 每个大专家被切成 4 个更小专家，形成 64 个小方块，标注“m=4 → mN=64 小专家”
  - router 连向 8 个小专家，标注“Top-8”
  - 小专家分别只含一种简化知识符号，标注“更细的专长”
  - 下方写“组合数 C(64,8)=4.4B”
- 中间用粗箭头写：“参数量≈不变，计算量≈不变，组合更灵活”
- 右下角写手写页码“3/5”。

【要标注的文字】
- “GShard: 16 选 2”
- “DeepSeekMoE: 64 选 8”
- “每个专家变小：FFN hidden / m”
- “激活专家变多：K → mK”
- “组合空间暴涨”
- “更精确地拼出 token 所需知识”
- “参数量≈不变”
- “计算量≈不变”

【颜色限制】
- 背景：明亮浅米白 #FFF8EA 或 #FFFDF7。
- 左侧传统方案用浅灰和少量珊瑚红表示问题。
- 右侧 DeepSeekMoE 用深蓝和柔和黄色高亮小专家组合。
- 不超过 3 个主要颜色，保持清爽。

【禁止】
- 不要把所有 64 个小专家画得拥挤到不可读，可以用 8x8 小格阵列表示。
- 不要长段解释；用短标签和箭头。
- 不要旧纸、暗角、3D、照片感。
