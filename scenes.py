#!/usr/bin/env python3
"""Orpheus TTS Architecture Tutorial - Manim Scenes (7 scenes)."""

from manim import *

# ── Shared config ──────────────────────────────────────────────
BG_COLOR = "#1a1a2e"
ACCENT = "#e94560"
ACCENT2 = "#0f3460"
ACCENT3 = "#16213e"
TEXT_COLOR = "#eaeaea"
GOLD = "#f5c518"
TEAL = "#00b4d8"
GREEN = "#06d6a0"
PURPLE = "#9b5de5"

config.background_color = BG_COLOR


# ================================================================
# Scene 1 – Title & Overview
# ================================================================
class Scene1_Title(Scene):
    def construct(self):
        # Title
        title = Text("Orpheus TTS", font_size=72, color=ACCENT, weight=BOLD)
        subtitle = Text("基于大语言模型的文本转语音系统", font_size=32, color=TEXT_COLOR)
        subtitle.next_to(title, DOWN, buff=0.4)
        VGroup(title, subtitle).move_to(UP * 0.5)

        self.play(Write(title, run_time=1.5))
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait(1)

        # Three pillars
        pillars_data = [
            ("文本处理", "Tokenizer", TEAL),
            ("LLM 主干", "Llama Backbone", GOLD),
            ("SNAC 编解码", "Audio Codec", GREEN),
        ]
        boxes = VGroup()
        for label_cn, label_en, color in pillars_data:
            box = VGroup()
            rect = RoundedRectangle(
                corner_radius=0.15, width=3.2, height=1.6,
                fill_color=color, fill_opacity=0.15,
                stroke_color=color, stroke_width=2,
            )
            t1 = Text(label_cn, font_size=26, color=color, weight=BOLD)
            t2 = Text(label_en, font_size=18, color=TEXT_COLOR)
            t2.next_to(t1, DOWN, buff=0.15)
            box.add(rect, t1, t2)
            boxes.add(box)
        boxes.arrange(RIGHT, buff=0.5).next_to(subtitle, DOWN, buff=0.8)

        for box in boxes:
            self.play(FadeIn(box, shift=UP * 0.3), run_time=0.6)
        self.wait(1)

        # Arrows between pillars
        for i in range(len(boxes) - 1):
            arr = Arrow(
                boxes[i].get_right(), boxes[i + 1].get_left(),
                buff=0.1, color=TEXT_COLOR, stroke_width=2,
            )
            self.play(Create(arr), run_time=0.4)

        # Bottom tagline
        tagline = Text(
            "自然 · 富有表现力 · 多情感风格",
            font_size=24, color=ACCENT,
        ).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(tagline))
        self.wait(3)

        # Hold for audio sync
        self.wait(17)


# ================================================================
# Scene 2 – Tokenization
# ================================================================
class Scene2_Tokenization(Scene):
    def construct(self):
        header = Text("文本分词 Tokenization", font_size=42, color=ACCENT, weight=BOLD)
        header.to_edge(UP, buff=0.5)
        self.play(Write(header))

        # Example sentence
        sentence = Text(
            '"今天天气真不错"', font_size=30, color=TEXT_COLOR
        ).next_to(header, DOWN, buff=0.6)
        self.play(FadeIn(sentence))
        self.wait(1)

        # Arrow down
        arr1 = Arrow(sentence.get_bottom(), sentence.get_bottom() + DOWN * 0.8,
                      buff=0.1, color=TEAL)
        tok_label = Text("Llama Tokenizer", font_size=22, color=TEAL)
        tok_label.next_to(arr1, RIGHT, buff=0.2)
        self.play(Create(arr1), FadeIn(tok_label))
        self.wait(0.5)

        # Token boxes
        tokens = ["今天", "天气", "真", "不错"]
        tok_boxes = VGroup()
        for t in tokens:
            box = VGroup()
            rect = RoundedRectangle(
                corner_radius=0.1, width=1.4, height=0.7,
                fill_color=TEAL, fill_opacity=0.2,
                stroke_color=TEAL, stroke_width=2,
            )
            txt = Text(t, font_size=22, color=TEXT_COLOR)
            box.add(rect, txt)
            tok_boxes.add(box)
        tok_boxes.arrange(RIGHT, buff=0.3)
        tok_boxes.next_to(arr1, DOWN, buff=0.5)

        for tb in tok_boxes:
            self.play(FadeIn(tb, shift=UP * 0.2), run_time=0.4)
        self.wait(0.5)

        # Arrow to IDs
        arr2 = Arrow(tok_boxes.get_bottom(), tok_boxes.get_bottom() + DOWN * 0.8,
                      buff=0.1, color=GOLD)
        self.play(Create(arr2))

        # Token IDs
        ids = ["1234", "5678", "910", "1112"]
        id_boxes = VGroup()
        for tid in ids:
            box = VGroup()
            rect = RoundedRectangle(
                corner_radius=0.1, width=1.4, height=0.7,
                fill_color=GOLD, fill_opacity=0.15,
                stroke_color=GOLD, stroke_width=2,
            )
            txt = Text(tid, font_size=20, color=GOLD)
            box.add(rect, txt)
            id_boxes.add(box)
        id_boxes.arrange(RIGHT, buff=0.3)
        id_boxes.next_to(arr2, DOWN, buff=0.5)

        self.play(FadeIn(id_boxes))
        self.wait(1)

        note = Text(
            "Token IDs → 送入 LLM 主干网络",
            font_size=22, color=TEXT_COLOR,
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(3)

        # Hold for audio
        self.wait(17)


# ================================================================
# Scene 3 – LLM Backbone
# ================================================================
class Scene3_LLMBackbone(Scene):
    def construct(self):
        header = Text("LLM 主干网络", font_size=42, color=ACCENT, weight=BOLD)
        header.to_edge(UP, buff=0.5)
        self.play(Write(header))

        # Transformer block stack
        layers = VGroup()
        layer_labels = [
            "Self-Attention", "Feed-Forward", "Self-Attention",
            "Feed-Forward", "Self-Attention", "Feed-Forward",
        ]
        colors = [PURPLE, TEAL] * 3
        for i, (lbl, col) in enumerate(zip(layer_labels, colors)):
            rect = RoundedRectangle(
                corner_radius=0.1, width=5, height=0.55,
                fill_color=col, fill_opacity=0.2,
                stroke_color=col, stroke_width=2,
            )
            txt = Text(lbl, font_size=18, color=TEXT_COLOR)
            layer = VGroup(rect, txt)
            layers.add(layer)
        layers.arrange(UP, buff=0.12)
        layers.move_to(DOWN * 0.5 + LEFT * 0.5)

        # Input label
        inp = Text("Text Tokens", font_size=20, color=TEAL)
        inp.next_to(layers, DOWN, buff=0.4)
        inp_arr = Arrow(inp.get_top(), layers.get_bottom(), buff=0.1, color=TEAL)

        # Output label
        out = Text("Audio Tokens (SNAC)", font_size=20, color=GOLD)
        out.next_to(layers, UP, buff=0.4)
        out_arr = Arrow(layers.get_top(), out.get_bottom(), buff=0.1, color=GOLD)

        self.play(FadeIn(inp), Create(inp_arr))
        for layer in layers:
            self.play(FadeIn(layer, shift=UP * 0.15), run_time=0.35)
        self.play(Create(out_arr), FadeIn(out))
        self.wait(1)

        # Parenthetical note under header
        note = Text(
            "（基于 Llama 架构，自回归生成音频 Token）",
            font_size=22, color=GREY_B,
        )
        note.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(note, shift=DOWN * 0.2))
        self.wait(3)

        # Hold
        self.wait(21)


# ================================================================
# Scene 4 – SNAC vs SoundStorm/EnCodec/DAC Comparison
# ================================================================
class Scene4_SNACEncoder(Scene):
    def construct(self):
        header = Text("音频编码对比：传统方案 vs SNAC", font_size=38, color=ACCENT, weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # ── Divider line ──
        divider = DashedLine(UP * 2.5, DOWN * 3.0, color=GREY, dash_length=0.15)
        divider.move_to(ORIGIN)
        self.play(Create(divider), run_time=0.5)

        # ── LEFT SIDE: SoundStorm / EnCodec / DAC ──
        left_title = Text("SoundStorm / EnCodec / DAC", font_size=20, color=TEAL, weight=BOLD)
        left_title.move_to(LEFT * 3.5 + UP * 2.0)
        self.play(FadeIn(left_title))

        # Uniform codebook: all layers same number of tokens
        left_layers = VGroup()
        left_layer_labels = ["Codebook 1", "Codebook 2", "Codebook 3", "Codebook 4"]
        num_tokens_uniform = 8  # all layers same count
        for i, lbl in enumerate(left_layer_labels):
            row = VGroup()
            label = Text(lbl, font_size=14, color=TEXT_COLOR)
            label.set_width(min(label.width, 1.4))
            boxes = VGroup()
            for j in range(num_tokens_uniform):
                sq = Square(
                    side_length=0.35, fill_color=TEAL, fill_opacity=0.25,
                    stroke_color=TEAL, stroke_width=1.5,
                )
                boxes.add(sq)
            boxes.arrange(RIGHT, buff=0.04)
            row.add(label, boxes)
            row.arrange(RIGHT, buff=0.3)
            left_layers.add(row)
        left_layers.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        left_layers.next_to(left_title, DOWN, buff=0.4)
        left_layers.shift(LEFT * 0.3)

        for row in left_layers:
            self.play(FadeIn(row), run_time=0.4)
        self.wait(0.5)

        # Annotation: equal rate
        left_note1 = Text("每层速率相同", font_size=16, color=TEAL)
        left_note1.next_to(left_layers, DOWN, buff=0.3)
        left_brace = Brace(left_layers, RIGHT, color=TEAL)
        left_brace_txt = Text("50 tok/s\n× 4层", font_size=13, color=TEAL)
        left_brace_txt.next_to(left_brace, RIGHT, buff=0.1)
        self.play(FadeIn(left_note1), Create(left_brace), FadeIn(left_brace_txt))
        self.wait(0.5)

        # Total tokens
        left_total = Text("总计: 200 tok/s", font_size=16, color=TEAL, weight=BOLD)
        left_total.next_to(left_note1, DOWN, buff=0.2)
        self.play(FadeIn(left_total))
        self.wait(1)

        # ── RIGHT SIDE: SNAC ──
        right_title = Text("SNAC", font_size=24, color=GOLD, weight=BOLD)
        right_title.move_to(RIGHT * 3.5 + UP * 2.0)
        self.play(FadeIn(right_title))

        # Multi-scale codebook: different layers different token counts
        right_layer_data = [
            ("Layer 1", 2, GOLD, "12 tok/s  粗粒度"),
            ("Layer 2", 4, GREEN, "24 tok/s  中粒度"),
            ("Layer 3", 8, PURPLE, "48 tok/s  细粒度"),
        ]
        right_layers = VGroup()
        right_rate_labels = VGroup()
        for lbl, count, col, rate_txt in right_layer_data:
            row = VGroup()
            label = Text(lbl, font_size=14, color=TEXT_COLOR)
            label.set_width(min(label.width, 1.2))
            boxes = VGroup()
            for j in range(count):
                sq = Square(
                    side_length=0.35, fill_color=col, fill_opacity=0.25,
                    stroke_color=col, stroke_width=1.5,
                )
                boxes.add(sq)
            boxes.arrange(RIGHT, buff=0.04)
            row.add(label, boxes)
            row.arrange(RIGHT, buff=0.3)
            right_layers.add(row)
            # Rate annotation
            rate = Text(rate_txt, font_size=12, color=col)
            right_rate_labels.add(rate)

        right_layers.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        right_layers.next_to(right_title, DOWN, buff=0.4)
        right_layers.shift(LEFT * 0.3)

        for i, row in enumerate(right_layers):
            self.play(FadeIn(row), run_time=0.4)
            right_rate_labels[i].next_to(row, RIGHT, buff=0.3)
            self.play(FadeIn(right_rate_labels[i]), run_time=0.3)
        self.wait(0.5)

        # Pyramid shape annotation
        right_note1 = Text("不同层速率不同 → 金字塔结构", font_size=16, color=GOLD)
        right_note1.next_to(right_layers, DOWN, buff=0.3)
        self.play(FadeIn(right_note1))
        self.wait(0.5)

        right_total = Text("总计: 84 tok/s (更高效!)", font_size=16, color=GOLD, weight=BOLD)
        right_total.next_to(right_note1, DOWN, buff=0.2)
        self.play(FadeIn(right_total))
        self.wait(1.5)

        # ── Highlight comparison ──
        # Strikethrough left total (small line, not full Cross)
        strike = Line(
            left_total.get_left() + LEFT * 0.1,
            left_total.get_right() + RIGHT * 0.1,
            stroke_color=ACCENT, stroke_width=4,
        )
        self.play(Create(strike), run_time=0.5)

        highlight_box = SurroundingRectangle(
            right_total, color=GOLD, buff=0.1, corner_radius=0.08, stroke_width=3,
        )
        self.play(Create(highlight_box))
        self.wait(1)

        # Bottom summary
        bottom_note = Text(
            "SNAC: 更少的 token，更高的音质，更适合 LLM 生成",
            font_size=20, color=ACCENT,
        ).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(bottom_note))
        self.wait(3)

        # Hold for audio sync
        self.wait(30)


# ================================================================
# Scene 5 – Pyramid Interleaving (FIXED: no overlap)
# ================================================================
class Scene5_PyramidInterleaving(Scene):
    def construct(self):
        header = Text("金字塔交错 Pyramid Interleaving", font_size=38, color=ACCENT, weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # Three layers visualization
        layer_colors = [GOLD, GREEN, PURPLE]
        layer_names = ["L1 (粗)", "L2 (中)", "L3 (细)"]
        counts = [2, 4, 8]

        layers_group = VGroup()
        for i, (name, count, col) in enumerate(zip(layer_names, counts, layer_colors)):
            row = VGroup()
            label = Text(name, font_size=18, color=col)
            label.set_width(min(label.width, 1.2))
            boxes = VGroup()
            for j in range(count):
                sq = Square(
                    side_length=0.4, fill_color=col, fill_opacity=0.3,
                    stroke_color=col, stroke_width=2,
                )
                idx = Text(str(j), font_size=12, color=TEXT_COLOR)
                boxes.add(VGroup(sq, idx))
            boxes.arrange(RIGHT, buff=0.1)
            row.add(label, boxes)
            row.arrange(RIGHT, buff=0.4)
            layers_group.add(row)
        layers_group.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        layers_group.next_to(header, DOWN, buff=0.5).shift(LEFT * 1.5)

        for row in layers_group:
            self.play(FadeIn(row), run_time=0.5)
        self.wait(1)

        # Interleaving arrow
        arr_label = Text("交错展平", font_size=20, color=ACCENT)
        arr_label.next_to(layers_group, DOWN, buff=0.3)
        arrow_down = Arrow(
            layers_group.get_bottom() + DOWN * 0.1,
            layers_group.get_bottom() + DOWN * 1.0,
            buff=0, color=ACCENT,
        )
        self.play(FadeIn(arr_label), Create(arrow_down))

        # Interleaved sequence: [C0, M0, M1, F0, F1, F2, F3, C1, M2, M3, F4, F5, F6, F7]
        seq_colors = [GOLD, GREEN, GREEN, PURPLE, PURPLE, PURPLE, PURPLE,
                       GOLD, GREEN, GREEN, PURPLE, PURPLE, PURPLE, PURPLE]
        seq_labels = ["C0", "M0", "M1", "F0", "F1", "F2", "F3",
                       "C1", "M2", "M3", "F4", "F5", "F6", "F7"]

        seq_group = VGroup()
        for lbl, col in zip(seq_labels, seq_colors):
            sq = Square(
                side_length=0.38, fill_color=col, fill_opacity=0.3,
                stroke_color=col, stroke_width=2,
            )
            txt = Text(lbl, font_size=10, color=TEXT_COLOR)
            seq_group.add(VGroup(sq, txt))
        seq_group.arrange(RIGHT, buff=0.06)
        seq_group.scale_to_fit_width(10)
        seq_group.move_to(DOWN * 1.2)

        self.play(FadeIn(seq_group), run_time=1.0)
        self.wait(1)

        # Pyramid structure annotation
        brace1 = Brace(seq_group[:7], DOWN, color=TEXT_COLOR)
        brace1_txt = Text("时间步 0", font_size=14, color=TEXT_COLOR)
        brace1_txt.next_to(brace1, DOWN, buff=0.1)
        brace2 = Brace(seq_group[7:], DOWN, color=TEXT_COLOR)
        brace2_txt = Text("时间步 1", font_size=14, color=TEXT_COLOR)
        brace2_txt.next_to(brace2, DOWN, buff=0.1)

        self.play(Create(brace1), FadeIn(brace1_txt), Create(brace2), FadeIn(brace2_txt))
        self.wait(3)

        # Hold
        self.wait(28)


# ================================================================
# Scene 6 – SNAC Decoder (FIXED: no overflow)
# ================================================================
class Scene6_SNACDecoder(Scene):
    def construct(self):
        header = Text("SNAC 解码器", font_size=42, color=ACCENT, weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # Three input token streams
        input_labels = VGroup()
        input_data = [
            ("L1 Tokens", GOLD),
            ("L2 Tokens", GREEN),
            ("L3 Tokens", PURPLE),
        ]
        for lbl, col in input_data:
            rect = RoundedRectangle(
                corner_radius=0.1, width=2.2, height=0.5,
                fill_color=col, fill_opacity=0.2,
                stroke_color=col, stroke_width=2,
            )
            txt = Text(lbl, font_size=16, color=col)
            input_labels.add(VGroup(rect, txt))
        input_labels.arrange(DOWN, buff=0.25)
        input_labels.next_to(header, DOWN, buff=0.5).shift(LEFT * 4)

        for il in input_labels:
            self.play(FadeIn(il), run_time=0.3)

        # Codebook lookup
        cb_label = Text("码本查找", font_size=18, color=TEAL)
        cb_rect = RoundedRectangle(
            corner_radius=0.1, width=2.2, height=1.8,
            fill_color=TEAL, fill_opacity=0.1,
            stroke_color=TEAL, stroke_width=2,
        )
        cb = VGroup(cb_rect, cb_label)
        cb.next_to(input_labels, RIGHT, buff=0.8)

        arrows_to_cb = VGroup()
        for il in input_labels:
            arr = Arrow(il.get_right(), cb.get_left(), buff=0.1, color=TEXT_COLOR, stroke_width=1.5)
            arrows_to_cb.add(arr)
        self.play(*[Create(a) for a in arrows_to_cb], FadeIn(cb), run_time=0.6)
        self.wait(0.5)

        # Upsample blocks
        up_blocks = VGroup()
        up_labels = ["上采样 ×2", "上采样 ×2", "上采样 ×2"]
        widths = [2.0, 2.6, 3.2]
        for w, lbl in zip(widths, up_labels):
            rect = RoundedRectangle(
                corner_radius=0.1, width=w, height=0.5,
                fill_color=GREEN, fill_opacity=0.15,
                stroke_color=GREEN, stroke_width=2,
            )
            txt = Text(lbl, font_size=16, color=TEXT_COLOR)
            up_blocks.add(VGroup(rect, txt))
        up_blocks.arrange(DOWN, buff=0.25)
        up_blocks.next_to(cb, RIGHT, buff=0.8)

        arr_cb = Arrow(cb.get_right(), up_blocks.get_left(), buff=0.1, color=TEAL)
        self.play(Create(arr_cb))
        for ub in up_blocks:
            self.play(FadeIn(ub, shift=DOWN * 0.15), run_time=0.35)
        self.wait(0.5)

        # Output waveform
        wave = FunctionGraph(
            lambda x: 0.25 * np.sin(4 * x) * np.cos(8 * x),
            x_range=[-2, 2], color=ACCENT, stroke_width=2,
        ).scale(0.5)
        wave.next_to(up_blocks, RIGHT, buff=0.8)
        wave_label = Text("24kHz 音频", font_size=16, color=ACCENT)
        wave_label.next_to(wave, DOWN, buff=0.15)

        arr_out = Arrow(up_blocks.get_right(), wave.get_left(), buff=0.1, color=ACCENT)
        self.play(Create(arr_out), Create(wave), FadeIn(wave_label))
        self.wait(1)

        # Bottom note
        note = Text(
            "从粗到细逐步重建 → 自然清晰的语音",
            font_size=20, color=ACCENT,
        ).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(3)

        # Hold
        self.wait(22)


# ================================================================
# Scene 7 – End-to-End Pipeline & Summary (FIXED: no overlap)
# ================================================================
class Scene7_EndToEnd(Scene):
    def construct(self):
        header = Text("端到端流程", font_size=42, color=ACCENT, weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header))

        # Pipeline stages
        stages_data = [
            ("输入文本", TEAL),
            ("Tokenizer", TEAL),
            ("LLM\n(Llama)", GOLD),
            ("反交错", PURPLE),
            ("SNAC\n解码器", GREEN),
            ("音频输出", ACCENT),
        ]
        stages = VGroup()
        for label, col in stages_data:
            rect = RoundedRectangle(
                corner_radius=0.12, width=1.8, height=1.0,
                fill_color=col, fill_opacity=0.15,
                stroke_color=col, stroke_width=2,
            )
            txt = Text(label, font_size=14, color=col, line_spacing=1.0)
            stages.add(VGroup(rect, txt))
        stages.arrange(RIGHT, buff=0.35)
        stages.scale_to_fit_width(12)
        stages.next_to(header, DOWN, buff=0.6)

        # Animate stages one by one
        for i, stage in enumerate(stages):
            self.play(FadeIn(stage, shift=RIGHT * 0.2), run_time=0.4)
            if i < len(stages) - 1:
                arr = Arrow(
                    stage.get_right(), stages[i + 1].get_left(),
                    buff=0.05, color=TEXT_COLOR, stroke_width=2,
                )
                self.play(Create(arr), run_time=0.25)
        self.wait(1)

        # Streaming badge
        stream_badge = VGroup()
        sr = RoundedRectangle(
            corner_radius=0.1, width=3.5, height=0.5,
            fill_color=GREEN, fill_opacity=0.15,
            stroke_color=GREEN, stroke_width=2,
        )
        st = Text("✓ 支持流式生成，实时输出", font_size=18, color=GREEN)
        stream_badge.add(sr, st)
        stream_badge.next_to(stages, DOWN, buff=0.5)
        self.play(FadeIn(stream_badge))
        self.wait(1)

        # Summary box
        summary_items = [
            "高质量：多尺度 SNAC 编码",
            "低延迟：流式自回归生成",
            "灵活：基于 LLM 架构，易于扩展",
        ]
        summary = VGroup()
        for item in summary_items:
            txt = Text(f"• {item}", font_size=18, color=TEXT_COLOR)
            summary.add(txt)
        summary.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        summary_box = SurroundingRectangle(
            summary, color=ACCENT, buff=0.3, corner_radius=0.15,
        )
        summary_group = VGroup(summary_box, summary)
        summary_group.next_to(stream_badge, DOWN, buff=0.4)

        self.play(Create(summary_box), run_time=0.5)
        for item in summary:
            self.play(FadeIn(item), run_time=0.4)
        self.wait(1)

        # Thank you
        thanks = Text("感谢观看!", font_size=36, color=ACCENT, weight=BOLD)
        thanks.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(thanks, scale=1.2))
        self.wait(3)

        # Hold
        self.wait(24)
