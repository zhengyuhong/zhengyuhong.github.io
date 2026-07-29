Use case: scientific-educational
Asset type: paper illustrated note, vertical 2:3 sketchnote page
Primary request: Create page 4 of a Chinese sketchnote explaining shared expert isolation in DeepSeekMoE.

【类型】核心机制细节图 / 冗余消除示意
【风格】sketchnote, 温暖科研手抄报风
【语言】中文为主，保留 shared experts, routed experts, router, FFN 等英文术语
【画幅】竖版 2:3，高清，所有文字清晰可读

【页面主题】
机制二：共享专家隔离

【视觉结构】
- 顶部标题：“机制二：把通用知识单独放出来”
- 左侧画“传统 MoE 的问题”：
  - 多个 routed expert，每个专家里都重复出现“语法 / 常识 / 基础模式”等小标签。
  - 用珊瑚红圈出重复部分，标注“知识冗余”。
- 右侧画“DeepSeekMoE 的做法”：
  - 上方或中间放 2 到 4 个橄榄绿 shared experts，标注“共享专家 K_s: always on”。
  - 所有 token 的箭头都先经过 shared experts，显示公共知识被吸收。
  - 下方是一组深蓝 routed experts，router 只选择其中若干个，标注“只学差异知识”。
- 中央用一条清晰转换箭头：“公共知识 → shared；差异知识 → routed”。
- 底部小公式卡片：“h = sum(shared FFN) + sum(g_i · routed FFN_i) + u”
- 右下角写手写页码“4/5”。

【要标注的文字】
- “传统 MoE：多个专家重复学通用知识”
- “共享专家 K_s：每个 token 必经”
- “路由专家：保留专门知识”
- “减少 redundancy”
- “提升参数效率”
- “mK - K_s 个 routed experts 被激活”

【颜色限制】
- 背景：明亮浅米白 #FFF8EA 或 #FFFDF7。
- 重复/冗余用珊瑚红圈注；shared experts 用橄榄绿；routed experts 用深蓝。
- 保持手绘黑线为主，颜色轻量。

【禁止】
- 不要画成剧情漫画，不要人物对话框。
- 不要让公式占据主体，公式只是底部卡片。
- 不要旧纸、暗角、3D、照片感。
