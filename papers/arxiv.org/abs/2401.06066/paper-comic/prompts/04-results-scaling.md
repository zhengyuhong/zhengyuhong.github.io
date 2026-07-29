Use case: scientific-educational
Asset type: paper illustrated note, vertical 2:3 sketchnote page
Primary request: Create page 5 of a Chinese sketchnote summarizing key DeepSeekMoE experimental results, with careful numbers and no invented chart scores.

【类型】关键结果图 / 证据总结
【风格】sketchnote, 温暖科研手抄报风，专业、清晰、克制
【语言】中文为主，保留 DeepSeekMoE, GShard, Dense, LLaMA2, activated params, FLOPs 等英文术语
【画幅】竖版 2:3，高清，所有文字清晰可读

【页面主题】
关键结果：更少激活计算，接近 dense 效果

【视觉结构】
- 顶部标题：“关键结果：更少计算，接近 dense 效果”
- 画面主体分成三条横向证据带，每条有小图标、对比模块和一句结论。不要画具体 benchmark 分数，不要发明排名数字。
- 证据带 1：“2B 验证”
  - 画四个模型卡片：GShard 2B、GShard 2.9B、DeepSeekMoE 2B、Dense 2B 上界。
  - 用箭头表达：“DeepSeekMoE 2B ≈ GShard 2.9B；接近 Dense 2B 上界”。
  - 标注：“同等 2B 规模验证架构有效”。
- 证据带 2：“16B 扩展”
  - 画 DeepSeekMoE 16B 与 DeepSeek 7B / LLaMA2 7B 的对比。
  - 精确标签：DeepSeekMoE 16B: “16.4B total, 2.8B activated”。
  - 旁边算力仪表：DeepSeekMoE 16B “74.4T FLOPs / 4K tokens”，Dense 7B “约 183T FLOPs / 4K tokens”。
  - 高亮：“约 40% compute, 性能 comparable”。
- 证据带 3：“145B 初步”
  - 画 DeepSeekMoE 145B、GShard 137B、DeepSeek 67B 三张模型卡片。
  - 精确标签：DeepSeekMoE 145B “144.6B total, 22.2B activated”。
  - 高亮：“约 28.5% compute vs DeepSeek 67B”。
  - 结论：“优于 GShard，接近 DeepSeek 67B”。
- 底部放“为什么有效？”三点小总结：
  - “小专家：更专”
  - “共享专家：少重复”
  - “Top-k 组合：更灵活”
- 右下角写手写页码“5/5”。

【要标注的文字】
- “2B: 接近 dense 上界”
- “16B: 16.4B total, 2.8B activated”
- “74.4T vs 约 183T FLOPs / 4K tokens”
- “约 40% compute, comparable”
- “145B: 144.6B total, 22.2B activated”
- “约 28.5% compute vs DeepSeek 67B”
- “优于 GShard，接近 DeepSeek 67B”
- “小专家 + 共享专家 + 灵活路由”

【颜色限制】
- 背景：明亮浅米白 #FFF8EA 或 #FFFDF7。
- 关键数字用柔和黄色马克笔高亮。
- DeepSeekMoE 用深蓝，dense baseline 用灰色，GShard 用珊瑚红。
- 不要渐变和大面积重色块。

【禁止】
- 不要画完整实验表格。
- 不要发明 benchmark 分数或排行榜数字。
- 不要夸张成绝对胜利，要表达“comparable / 接近 / 优于 GShard”的准确语气。
- 不要旧纸、暗角、3D、照片感。
