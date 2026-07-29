Use case: scientific-educational
Asset type: paper illustrated note, vertical 2:3 sketchnote page
Primary request: Create page 2 of a Chinese sketchnote explaining the DeepSeekMoE layer data flow.

【类型】方法总览流程图
【风格】sketchnote, 温暖科研手抄报风
【语言】中文为主，保留 Transformer, Self-Att, MoE, FFN, router, Top-k 等英文术语
【画幅】竖版 2:3，高清，所有文字清晰可读

【页面主题】
方法总览：token 如何穿过 DeepSeekMoE 层

【视觉结构】
- 顶部标题：“方法总览：DeepSeekMoE 层”
- 画面从上到下或左到右分 5 步，用数字圆点引导：
  1. 左上角：“输入 hidden state u_t” 进入 Transformer block。
  2. 中上：“Self-Att 已完成”，箭头流向 MoE 层，强调 DeepSeekMoE 替换的是 FFN 部分。
  3. 中央画 MoE 层大框，内部左右分栏：
     - 左栏为“共享专家 K_s”，2 到 4 个小 FFN 方块，所有 token 都经过，箭头是实线。
     - 右栏为“路由专家 mN-K_s”，一组很多小 FFN 方块，只有部分被高亮，箭头通过 router 后分发。
  4. router 小圆盘旁写“s_i,t = Softmax(u_t · e_i)”和“Top-k 选择”。
  5. 右侧把共享专家输出与路由专家加权输出汇合，再加 residual，输出“h_t”。
- 底部放一个小公式卡片，短写：“h = shared sum + routed weighted sum + u”。
- 右下角写手写页码“2/5”。

【要标注的文字】
- “输入 hidden state u_t”
- “Self-Att 已完成”
- “替换 FFN 为 MoE”
- “共享专家 K_s：每个 token 必经”
- “router 打分”
- “Top-k 路由专家”
- “g_i,t 作为权重”
- “输出 h_t = 专家输出 + residual”

【颜色限制】
- 背景：明亮浅米白 #FFF8EA 或 #FFFDF7。
- 共享专家用橄榄绿淡色，路由专家用深蓝淡色，核心路径用珊瑚红箭头。
- 线条保持手绘黑线，颜色只做强调。

【禁止】
- 不要照抄论文 Figure 2 的布局，要重新组织成更清晰的教学图。
- 不要长段文字，不要照片写实，不要 3D，不要暗旧纸纹。
- 不要让标注遮挡箭头或模块。
