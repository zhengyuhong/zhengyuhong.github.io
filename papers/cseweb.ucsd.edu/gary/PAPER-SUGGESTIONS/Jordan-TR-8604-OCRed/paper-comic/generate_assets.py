from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, sin
from pathlib import Path
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[6]
ASSETS = ROOT / "assets" / "images" / "jordan-serial-order-illustrated"
W, H = 1600, 2400

BG = "#FFF8EA"
INK = "#1F2326"
MUTED = "#5F6467"
FAINT = "#E8DDC8"
PANEL = "#FFFDF7"
BLUE = "#2C5F8A"
CORAL = "#D85C4A"
OLIVE = "#5C6B4F"
YELLOW = "#F3D36B"
MINT = "#DCEBD6"
SKY = "#DDECF7"
PEACH = "#F9DDD5"
LEMON = "#FFF1A8"

FONT_REGULAR = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_MONO = "/Library/Fonts/Arial Unicode.ttf"


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size)


@dataclass
class Canvas:
    img: Image.Image
    draw: ImageDraw.ImageDraw
    rng: random.Random


def new_canvas(seed: int) -> Canvas:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    rng = random.Random(seed)
    add_paper_grain(img, rng)
    return Canvas(img, draw, rng)


def add_paper_grain(img: Image.Image, rng: random.Random) -> None:
    pix = img.load()
    for _ in range(14000):
        x = rng.randrange(W)
        y = rng.randrange(H)
        r, g, b = pix[x, y]
        delta = rng.choice((-3, -2, 2, 3))
        pix[x, y] = (max(0, min(255, r + delta)), max(0, min(255, g + delta)), max(0, min(255, b + delta)))


def jitter(value: float, rng: random.Random, amount: float = 2.0) -> float:
    return value + rng.uniform(-amount, amount)


def rough_line(c: Canvas, xy: tuple[float, float, float, float], color: str = INK, width: int = 4) -> None:
    x1, y1, x2, y2 = xy
    for pass_no in range(2):
        points = []
        steps = 18
        for i in range(steps + 1):
            t = i / steps
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            amount = 1.6 if pass_no == 0 else 2.8
            points.append((jitter(x, c.rng, amount), jitter(y, c.rng, amount)))
        c.draw.line(points, fill=color, width=width, joint="curve")


def rough_polyline(c: Canvas, points: list[tuple[float, float]], color: str = INK, width: int = 4) -> None:
    for a, b in zip(points, points[1:]):
        rough_line(c, (a[0], a[1], b[0], b[1]), color, width)


def rough_rect(
    c: Canvas,
    box: tuple[int, int, int, int],
    fill: str = PANEL,
    outline: str = INK,
    width: int = 4,
    radius: int = 26,
) -> None:
    x1, y1, x2, y2 = box
    c.draw.rounded_rectangle(box, radius=radius, fill=fill)
    for _ in range(2):
        off = c.rng.uniform(-2.0, 2.0)
        c.draw.rounded_rectangle(
            (x1 + off, y1 + off, x2 + off, y2 + off),
            radius=radius,
            outline=outline,
            width=width,
        )


def rough_ellipse(c: Canvas, box: tuple[int, int, int, int], fill: str = PANEL, outline: str = INK, width: int = 4) -> None:
    c.draw.ellipse(box, fill=fill)
    x1, y1, x2, y2 = box
    for _ in range(2):
        off = c.rng.uniform(-2.0, 2.0)
        c.draw.ellipse((x1 + off, y1 + off, x2 + off, y2 + off), outline=outline, width=width)


def arrow(c: Canvas, start: tuple[float, float], end: tuple[float, float], color: str = BLUE, width: int = 6) -> None:
    rough_line(c, (*start, *end), color, width)
    ang = atan2(end[1] - start[1], end[0] - start[0])
    length = 26
    spread = 0.48
    p1 = (end[0] - length * cos(ang - spread), end[1] - length * sin(ang - spread))
    p2 = (end[0] - length * cos(ang + spread), end[1] - length * sin(ang + spread))
    c.draw.polygon([end, p1, p2], fill=color)


def curved_arrow(
    c: Canvas,
    start: tuple[float, float],
    control: tuple[float, float],
    end: tuple[float, float],
    color: str = BLUE,
    width: int = 6,
) -> None:
    points = []
    for i in range(34):
        t = i / 33
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        points.append((x, y))
    rough_polyline(c, points, color, width)
    arrow(c, points[-3], end, color, width)


def text_size(c: Canvas, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = c.draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def split_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    buf = ""
    for ch in text:
        if ch.isspace():
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        elif ord(ch) < 128:
            buf += ch
        else:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
    if buf:
        tokens.append(buf)
    return tokens


def wrap(c: Canvas, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for token in split_tokens(text):
        candidate = current + token
        if token == "\n":
            lines.append(current)
            current = ""
            continue
        if text_size(c, candidate, fnt)[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current.rstrip())
            current = token.lstrip()
    if current:
        lines.append(current.rstrip())
    return lines


def put(
    c: Canvas,
    xy: tuple[int, int],
    text: str,
    size: int = 34,
    color: str = INK,
    bold: bool = False,
    max_width: int | None = None,
    line_gap: int = 12,
    mono: bool = False,
    anchor: str = "la",
) -> int:
    fnt = font(size, bold=bold, mono=mono)
    if max_width is None:
        c.draw.text(xy, text, fill=color, font=fnt, anchor=anchor)
        return text_size(c, text, fnt)[1]
    y = xy[1]
    total = 0
    for line in wrap(c, text, fnt, max_width):
        c.draw.text((xy[0], y), line, fill=color, font=fnt)
        line_h = text_size(c, line or " ", fnt)[1] + line_gap
        y += line_h
        total += line_h
    return total


def title(c: Canvas, main: str, subtitle: str, page: str) -> None:
    put(c, (82, 78), main, 68, INK, True)
    put(c, (86, 162), subtitle, 32, MUTED, max_width=1280, line_gap=10)
    put(c, (1420, 2264), page, 34, MUTED)
    rough_line(c, (82, 220, 1510, 220), FAINT, 3)


def note(c: Canvas, box: tuple[int, int, int, int], heading: str, lines: list[str], fill: str, outline: str) -> None:
    rough_rect(c, box, fill, outline, width=4, radius=28)
    x1, y1, x2, _ = box
    put(c, (x1 + 30, y1 + 30), heading, 36, outline, True, max_width=x2 - x1 - 60)
    y = y1 + 88
    for line in lines:
        put(c, (x1 + 32, y), line, 27, INK, max_width=x2 - x1 - 64, line_gap=9)
        y += 58


def pill(c: Canvas, box: tuple[int, int, int, int], label: str, fill: str = LEMON, outline: str = CORAL, size: int = 28) -> None:
    rough_rect(c, box, fill, outline, width=3, radius=(box[3] - box[1]) // 2)
    w, h = text_size(c, label, font(size, True))
    put(c, (box[0] + (box[2] - box[0] - w) // 2, box[1] + (box[3] - box[1] - h) // 2 - 2), label, size, INK, True)


def draw_units(c: Canvas, x: int, y: int, rows: int, cols: int, active: set[tuple[int, int]], color: str = BLUE) -> None:
    for r in range(rows):
        for col in range(cols):
            xx = x + col * 44
            yy = y + r * 44
            fill = color if (r, col) in active else "#FFFDF7"
            outline = color if (r, col) in active else FAINT
            rough_ellipse(c, (xx, yy, xx + 26, yy + 26), fill, outline, 2)


def mini_table(c: Canvas, x: int, y: int, rows: list[list[str]], cell_w: int, cell_h: int, colors: dict[str, str]) -> None:
    for r, row in enumerate(rows):
        for col, val in enumerate(row):
            fill = colors.get(val, PANEL)
            outline = BLUE if val == ".9" else CORAL if val == "0" else FAINT
            rough_rect(c, (x + col * cell_w, y + r * cell_h, x + (col + 1) * cell_w, y + (r + 1) * cell_h), fill, outline, 2, 8)
            w, h = text_size(c, val, font(24, True, mono=True))
            put(c, (x + col * cell_w + (cell_w - w) // 2, y + r * cell_h + (cell_h - h) // 2 - 2), val, 24, INK, True, mono=True)


def page_cover() -> Image.Image:
    c = new_canvas(1)
    title(c, "Serial Order：PDP 如何生成有序动作", "Michael I. Jordan, 1986 · 用动态状态、约束学习和分布式表示解释“串行中的并行”", "00 / 06")
    pill(c, (86, 270, 520, 330), "论文图解 · 中文 sketchnote")
    pill(c, (630, 270, 1010, 330), "关键词：state / plan / constraints")

    note(c, (92, 410, 520, 760), "旧问题", ["链式 A→B 难处理 ABAC", "buffer 指针难解释协同发音", "重复动作会混淆上下文"], PEACH, CORAL)
    note(c, (1080, 410, 1510, 760), "新视角", ["行为是一条 state trajectory", "plan 选序列，state 记时间", "约束越少，并行越自然"], SKY, BLUE)
    arrow(c, (530, 590), (1070, 590), OLIVE, 7)

    rough_rect(c, (345, 885, 1255, 1580), "#FFFDF7", INK, 5, 42)
    put(c, (460, 940), "不是“按清单逐项执行”", 44, MUTED, True)
    put(c, (445, 1010), "而是让动态系统学会走一条轨迹", 46, INK, True)
    rough_ellipse(c, (630, 1200, 970, 1540), LEMON, YELLOW, 5)
    put(c, (708, 1300), "state", 52, BLUE, True)
    put(c, (690, 1368), "s_n", 70, BLUE, True, mono=True)
    for i, label in enumerate(["plan p", "output x_n", "next state"]):
        angle = i * 2.05 - 1.0
        cx = 800 + int(410 * cos(angle))
        cy = 1370 + int(270 * sin(angle))
        rough_rect(c, (cx - 150, cy - 54, cx + 150, cy + 54), SKY if i == 0 else MINT if i == 1 else PEACH, BLUE if i == 0 else OLIVE if i == 1 else CORAL, 4, 25)
        put(c, (cx - 92, cy - 20), label, 31, INK, True)
        curved_arrow(c, (800, 1370), ((800 + cx) // 2, (1370 + cy) // 2 - 120), (cx - 148 if cx > 800 else cx + 148, cy), BLUE if i == 0 else OLIVE if i == 1 else CORAL, 5)

    note(c, (100, 1665, 1510, 2130), "一句话读法", [
        "这篇论文把 serial order、speech coarticulation 和 dual-task interference 放进同一个机制。",
        "核心不是“多画几个动作”，而是把时间藏进 state vector，把允许并行的部分留给 don't-care constraints。",
        "严格串行只是约束最强的极限情况。"
    ], "#FFFDF7", OLIVE)
    return c.img


def page_architecture() -> Image.Image:
    c = new_canvas(2)
    title(c, "方法总览：Plan + State → Output → State", "网络把 plan 和 state 当作输入；输出动作后，再反馈更新下一时刻 state", "01 / 06")

    note(c, (88, 320, 460, 600), "Plan units", ["固定整段意图", "区分 ABC 与 CBA", "不是时间指针"], SKY, BLUE)
    note(c, (88, 1130, 460, 1410), "State units", ["连续变化的时间上下文", "记录过去 output 的 trace", "相似时刻 → 相似状态"], MINT, OLIVE)
    note(c, (1125, 700, 1510, 1020), "Output units", ["当前动作特征", "可以部分并行激活", "输出又回写 state"], PEACH, CORAL)
    note(c, (610, 705, 995, 1015), "Hidden units", ["共享权重里的 associative memory", "学习 state/plan 到 output 的映射"], LEMON, YELLOW)

    draw_units(c, 195, 642, 4, 4, {(0, 1), (1, 0), (2, 3)}, BLUE)
    put(c, (158, 850), "p：选择哪条序列", 28, BLUE, True)
    draw_units(c, 195, 1452, 4, 4, {(0, 0), (1, 2), (2, 2), (3, 1)}, OLIVE)
    put(c, (150, 1660), "s_n：当前时间上下文", 28, OLIVE, True, mono=True)
    draw_units(c, 702, 1085, 4, 4, {(0, 1), (1, 1), (2, 2), (2, 3)}, YELLOW)
    draw_units(c, 1232, 1065, 4, 4, {(0, 0), (0, 3), (1, 1), (2, 2)}, CORAL)

    arrow(c, (390, 790), (650, 1100), BLUE, 6)
    arrow(c, (390, 1540), (680, 1190), OLIVE, 6)
    arrow(c, (885, 1175), (1198, 1175), CORAL, 6)
    curved_arrow(c, (1320, 1300), (1180, 1720), (370, 1600), OLIVE, 6)
    put(c, (815, 1625), "output feedback", 30, OLIVE, True)

    rough_rect(c, (220, 1830, 1380, 2095), "#FFFDF7", INK, 4, 35)
    put(c, (270, 1885), "两条方程就是整篇论文的骨架", 42, INK, True)
    put(c, (360, 1970), "x_n = f(s_n, p)", 46, CORAL, True, mono=True)
    put(c, (845, 1970), "s_{n+1} = g(s_n, p)", 46, OLIVE, True, mono=True)
    put(c, (270, 2052), "f 学输出；g 让 state 沿着轨迹前进。顺序信息不写在 output-to-output 链条里。", 28, MUTED, max_width=1080)
    return c.img


def page_temporal_state() -> Image.Image:
    c = new_canvas(3)
    title(c, "核心机制 1：State 是过去输出的指数痕迹", "用一个连续 state vector 记住时间上下文，避免把顺序写成脆弱的动作链", "02 / 06")

    put(c, (105, 310), "例子：ABAC 中两个 A 看起来相同，但 state 不同", 40, INK, True)
    xs = [170, 410, 650, 890]
    labels = ["A", "B", "A", "C"]
    for i, (x, lab) in enumerate(zip(xs, labels)):
        fill = LEMON if lab == "A" else SKY if lab == "B" else PEACH
        outline = YELLOW if lab == "A" else BLUE if lab == "B" else CORAL
        rough_rect(c, (x, 420, x + 150, 550), fill, outline, 5, 22)
        put(c, (x + 55, 455), lab, 56, INK, True)
        if i < 3:
            arrow(c, (x + 160, 485), (xs[i + 1] - 15, 485), INK, 5)
    put(c, (1085, 430), "链式模型在第二个 A 后容易迷路", 30, CORAL, True, max_width=350)

    rough_rect(c, (100, 680, 1500, 1015), "#FFFDF7", BLUE, 4, 35)
    put(c, (150, 735), "state 不是最近 n 个动作的硬窗口，而是一个逐渐衰减的记忆", 36, BLUE, True)
    put(c, (190, 820), "s_n = x_{n-1} + mu x_{n-2} + mu^2 x_{n-3} + ...", 38, INK, True, mono=True)
    put(c, (190, 910), "近的输出权重大，远的输出权重小；足够远的过去仍然留下微弱痕迹。", 30, MUTED, max_width=1180)

    y0 = 1180
    put(c, (105, 1090), "指数 trace 怎么长出来", 40, INK, True)
    for i, lab in enumerate(labels):
        x = 160 + i * 300
        rough_rect(c, (x, y0, x + 190, y0 + 110), LEMON if lab == "A" else SKY if lab == "B" else PEACH, INK, 3, 16)
        put(c, (x + 75, y0 + 30), lab, 44, INK, True)
        for k in range(i + 1):
            alpha_h = int(120 * (0.62 ** (i - k)))
            c.draw.rounded_rectangle((x + 24 + k * 34, y0 + 145, x + 50 + k * 34, y0 + 145 + alpha_h), radius=8, fill=[LEMON, SKY, LEMON, PEACH][k], outline=INK, width=2)
        put(c, (x + 15, y0 + 306), f"s{i+1}", 30, OLIVE, True, mono=True)
        if i < 3:
            arrow(c, (x + 200, y0 + 55), (x + 285, y0 + 55), OLIVE, 5)

    rough_rect(c, (150, 1650, 1450, 2110), MINT, OLIVE, 5, 36)
    put(c, (200, 1708), "为什么这解决 repeated actions？", 43, OLIVE, True)
    put(c, (210, 1795), "第一次 A 后的 state = “刚做过 A”", 31, INK)
    put(c, (210, 1855), "第二次 A 后的 state = “刚做过 A，但更早还有 A、B”", 31, INK)
    put(c, (210, 1915), "所以同一个 output A 可以出现在不同 state 上；下一步可以分别去 B 或 C。", 31, INK, max_width=1120)
    rough_line(c, (1010, 1780, 1270, 1900), BLUE, 5)
    rough_line(c, (1010, 1900, 1270, 1780), CORAL, 5)
    rough_ellipse(c, (960, 1728, 1048, 1816), LEMON, YELLOW, 4)
    rough_ellipse(c, (960, 1860, 1048, 1948), LEMON, YELLOW, 4)
    put(c, (976, 1748), "A1", 30, INK, True)
    put(c, (976, 1880), "A2", 30, INK, True)
    put(c, (1300, 1766), "→ B", 32, BLUE, True)
    put(c, (1300, 1888), "→ C", 32, CORAL, True)
    return c.img


def page_constraints() -> Image.Image:
    c = new_canvas(4)
    title(c, "核心机制 2：约束向量决定哪里必须串行", "学习时只对指定值回传误差；don't-care 维度让网络自己填，形成可控并行", "03 / 06")

    put(c, (90, 310), "一个训练序列可以写成“值约束 + *”", 40, INK, True)
    rows = [
        ["t", "1", "2", "3", "4"],
        ["u1", ".9", "*", "*", "*"],
        ["u2", "*", ".9", "*", "*"],
        ["u3", "*", "*", ".9", "*"],
        ["u4", "*", "*", "*", ".9"],
    ]
    mini_table(c, 130, 405, rows, 150, 82, {".9": LEMON, "*": "#FFFDF7", "0": PEACH})
    put(c, (930, 435), ".9：这个时刻必须激活", 31, BLUE, True)
    put(c, (930, 510), "*：don't-care，不规定值", 31, MUTED, True)
    put(c, (930, 585), "误差只从非 * 的格子回传", 31, CORAL, True)
    for i in range(4):
        arrow(c, (205 + (i + 1) * 150, 775 + i * 82), (1130, 865 + i * 35), CORAL, 4)

    rough_rect(c, (105, 940, 1495, 1345), SKY, BLUE, 5, 35)
    put(c, (160, 1000), "学习后的“填空”不是随机噪声，而是 generalization", 42, BLUE, True)
    put(c, (175, 1088), "网络学到 state/plan → output 的连续映射；未指定的维度会被相邻时刻、bias 和权重自然补上。", 31, INK, max_width=1220)
    put(c, (175, 1190), "如果只要求当前动作为 .9，未来动作也可能部分激活：这是 coarticulation 的来源。", 31, INK, max_width=1220)
    rough_line(c, (845, 1268, 1335, 1268), YELLOW, 18)
    put(c, (855, 1238), "约束留下的自由度 = 允许并行的空间", 33, INK, True)

    note(c, (105, 1480, 715, 2040), "更多约束", ["相邻时间步要求 0", "bias 被压住", "动作更严格分开", "并行更少"], PEACH, CORAL)
    note(c, (885, 1480, 1495, 2040), "更少约束", ["许多维度是 *", "网络自己填入部分激活", "未来动作提前浮现", "并行更多"], MINT, OLIVE)
    arrow(c, (720, 1760), (875, 1760), BLUE, 8)
    put(c, (760, 1685), "放松", 36, BLUE, True)
    put(c, (665, 2125), "Jordan 的关键转向：serial order 不是硬编码链条，而是约束学习后的动态轨迹。", 31, MUTED, max_width=780)
    return c.img


def page_coarticulation() -> Image.Image:
    c = new_canvas(5)
    title(c, "核心机制 3：协同发音是“被允许的提前激活”", "相邻 phoneme 的特征在 don't-care 维度里扩散，但语言约束会挡住不该发生的扩散", "04 / 06")

    put(c, (95, 315), "例 1：sinistre structure 中的 lip rounding", 40, INK, True)
    phonemes = ["s", "t", "r", "s", "t", "r", "y"]
    x0, y0 = 135, 440
    for i, ph in enumerate(phonemes):
        x = x0 + i * 190
        rough_rect(c, (x, y0, x + 130, y0 + 92), SKY if ph != "y" else LEMON, BLUE if ph != "y" else YELLOW, 4, 18)
        put(c, (x + 48, y0 + 22), ph, 42, INK, True)
        if i < len(phonemes) - 1:
            rough_line(c, (x + 140, y0 + 47, x + 178, y0 + 47), FAINT, 4)
    put(c, (105, 600), "圆唇目标在 /y/ 上，但如果前面辅音不用嘴唇，rounding 可以很早开始。", 30, MUTED, max_width=1320)
    curve = []
    for i in range(220):
        t = i / 219
        x = 160 + t * 1240
        y = 850 - 220 / (1 + 35 * (2.71828 ** (-9 * (t - 0.55))))
        curve.append((x, y))
    rough_polyline(c, curve, CORAL, 7)
    put(c, (168, 880), "lip rounding activation", 30, CORAL, True)
    put(c, (1120, 655), "目标 /y/", 33, INK, True)
    arrow(c, (1190, 685), (1330, 735), YELLOW, 5)
    rough_line(c, (155, 850, 1400, 850), FAINT, 4)

    put(c, (95, 1080), "例 2：freon 中的 nasal feature", 40, INK, True)
    phonemes2 = ["f", "r", "e", "o", "n"]
    for i, ph in enumerate(phonemes2):
        x = 190 + i * 240
        rough_rect(c, (x, 1190, x + 150, 1288), MINT if ph != "n" else LEMON, OLIVE if ph != "n" else YELLOW, 4, 18)
        put(c, (x + 58, 1215), ph, 42, INK, True)
    rough_line(c, (210, 1540, 1360, 1540), FAINT, 4)
    points = []
    for i in range(160):
        t = i / 159
        x = 210 + t * 1080
        y = 1540 - 190 / (1 + 18 * (2.71828 ** (-8 * (t - 0.64))))
        points.append((x, y))
    rough_polyline(c, points, BLUE, 7)
    put(c, (218, 1575), "nasal activation 提前升高", 30, BLUE, True)
    arrow(c, (1145, 1325), (1260, 1400), YELLOW, 5)
    put(c, (1090, 1288), "目标 /n/", 33, INK, True)

    rough_rect(c, (125, 1765, 1485, 2118), "#FFFDF7", INK, 5, 36)
    put(c, (175, 1825), "同一个机制解释“流畅”和“限制”", 43, INK, True)
    put(c, (185, 1910), "允许：free articulator 可以提前准备未来动作 → 语音更平滑。", 31, OLIVE, True, max_width=1160)
    put(c, (185, 1982), "阻止：如果语言把 nasal vowel 当成不同音位，约束会禁止 velum 提前打开。", 31, CORAL, True, max_width=1160)
    put(c, (185, 2054), "所以 coarticulation 不是额外模块，而是 constraint learning 的自然副产品。", 31, BLUE, True, max_width=1160)
    return c.img


def page_dual_task() -> Image.Image:
    c = new_canvas(6)
    title(c, "关键结果：时间扩散有用，任务空间扩散会干扰", "coarticulation 和 dual-task crosstalk 是同一种 generalization 在两个方向上的结果", "05 / 06")

    note(c, (95, 325, 735, 785), "时间维度：有用的扩散", ["同一序列内相邻 state 相似", "未来动作部分激活", "形成流畅 coarticulation"], MINT, OLIVE)
    note(c, (865, 325, 1505, 785), "空间维度：危险的扩散", ["两个任务共享 hidden channel", "v1 与 v2 越相似，越容易串音", "训练要压掉 crosstalk"], PEACH, CORAL)
    arrow(c, (740, 555), (860, 555), BLUE, 7)
    put(c, (620, 610), "同一种连续映射", 29, BLUE, True)

    put(c, (125, 930), "Shared hidden channel 里的 crosstalk", 40, INK, True)
    rough_ellipse(c, (275, 1060, 625, 1410), SKY, BLUE, 5)
    rough_ellipse(c, (500, 1060, 850, 1410), PEACH, CORAL, 5)
    put(c, (390, 1195), "v1", 50, BLUE, True, mono=True)
    put(c, (680, 1195), "v2", 50, CORAL, True, mono=True)
    put(c, (535, 1305), "overlap", 31, INK, True)
    note(c, (985, 1050, 1470, 1408), "相似度越高", ["inner product(v1,v2) ↑", "dual-task error ↑", "学习后误差下降"], LEMON, YELLOW)

    rough_rect(c, (135, 1575, 1465, 2075), "#FFFDF7", INK, 5, 34)
    put(c, (190, 1632), "论文 Figure 15/16 的核心形状", 41, INK, True)
    gx0, gy0, gw, gh = 270, 1795, 850, 210
    rough_line(c, (gx0, gy0 + gh, gx0 + gw, gy0 + gh), INK, 4)
    rough_line(c, (gx0, gy0, gx0, gy0 + gh), INK, 4)
    put(c, (gx0 - 95, gy0 + 15), "crosstalk", 26, MUTED, True)
    put(c, (gx0 + 600, gy0 + gh + 42), "learning trials", 26, MUTED, True)
    high = [(gx0, gy0 + 45), (gx0 + 130, gy0 + 78), (gx0 + 270, gy0 + 120), (gx0 + 510, gy0 + 171), (gx0 + 780, gy0 + 205)]
    low = [(gx0, gy0 + 105), (gx0 + 130, gy0 + 128), (gx0 + 270, gy0 + 160), (gx0 + 510, gy0 + 190), (gx0 + 780, gy0 + 208)]
    rough_polyline(c, high, CORAL, 7)
    rough_polyline(c, low, BLUE, 7)
    put(c, (1138, 1795), "高相似任务", 27, CORAL, True)
    put(c, (1138, 1875), "低相似任务", 27, BLUE, True)
    put(c, (190, 2118), "读后结论：学习不是消灭所有并行，而是保留时间上有用的并行、压制任务间有害的并行。", 31, MUTED, max_width=1180)
    return c.img


PAGES = [
    ("00-cover.png", page_cover),
    ("01-method-overview.png", page_architecture),
    ("02-temporal-state.png", page_temporal_state),
    ("03-constraints-dont-care.png", page_constraints),
    ("04-coarticulation.png", page_coarticulation),
    ("05-dual-task-crosstalk.png", page_dual_task),
]


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for filename, renderer in PAGES:
        out = ASSETS / filename
        img = renderer()
        img.save(out, optimize=True)
        print(out)


if __name__ == "__main__":
    main()
