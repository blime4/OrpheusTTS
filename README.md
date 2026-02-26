# Orpheus TTS 动画教程

这是一个使用 Manim 制作的 Orpheus TTS (Text-to-Speech) 架构动画教程视频项目。

## 项目概述

本项目包含 7 个动画场景，详细解释了 Orpheus TTS 的工作原理：

1. **标题场景** - Orpheus TTS 介绍
2. **TTS 架构概览** - 端到端语音合成流程
3. **LLM 骨干网络** - 基于 Llama 的自回归生成
4. **SNAC 编解码器** - 多尺度残差向量量化
5. **Token 流程** - 输入到输出的完整流程
6. **Orpheus 优势** - 自然韵律、零样本能力、情感控制
7. **端到端流程** - 完整的推理演示

## 文件结构

```
OrpheusTTS/
├── scenes.py              # Manim 动画场景代码
├── generate_audio.py      # 音频生成脚本 (edge-tts)
├── validate_scenes.py     # 场景验证脚本 (检测重叠和越界)
├── audio/                 # 中文配音文件
│   ├── scene1.mp3
│   ├── scene2.mp3
│   ├── scene3.mp3
│   ├── scene4.mp3
│   ├── scene5.mp3
│   ├── scene6.mp3
│   └── scene7.mp3
├── output/                # 输出视频
│   └── OrpheusTTS_Final.mp4
├── requirements.txt       # Python 依赖
└── README.md              # 本文件
```

## 依赖安装

```bash
pip install -r requirements.txt
```

主要依赖：
- **manim** - 动画引擎
- **edge-tts** - 微软 Edge TTS (中文语音合成)
- **ffmpeg** - 视频/音频处理

## 使用方法

### 1. 生成单独的场景视频

```bash
manim -pqh scenes.py Scene1_Title
manim -pqh scenes.py Scene2_TTSOverview
manim -pqh scenes.py Scene3_LLMBackbone
manim -pqh scenes.py Scene4_SNACCodec
manim -pqh scenes.py Scene5_TokenFlow
manim -pqh scenes.py Scene6_OrpheusAdvantages
manim -pqh scenes.py Scene7_EndToEnd
```

### 2. 生成音频文件

```bash
python generate_audio.py
```

### 3. 验证场景布局

```bash
python validate_scenes.py
```

### 4. 合成最终视频

```bash
# 合并每个场景的视频和音频
for i in 1 2 3 4 5 6 7; do
    ffmpeg -i media/videos/scenes/1080p60/Scene${i}_*.mp4 -i audio/scene${i}.mp3 \
        -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=2[v]" \
        -map "[v]" -map 1:a -c:v libx264 -c:a aac -y output/scene${i}_with_audio.mp4
done

# 拼接所有场景
ffmpeg -f concat -safe 0 -i <(for f in output/scene{1..7}_with_audio.mp4; do echo "file '$(pwd)/$f'"; done) \
    -c:v libx264 -c:a aac output/OrpheusTTS_Final.mp4
```

## 输出视频

最终视频：`output/OrpheusTTS_Final.mp4`
- 分辨率：1920x1080 (1080p)
- 帧率：60fps
- 时长：约 4:44
- 包含中文配音

## 技术细节

### 场景验证

`validate_scenes.py` 脚本用于检测：
- 元素重叠 (overlap > 30%)
- 元素越界 (out-of-bounds)
- 位置不正确问题

### 音频生成

使用 `edge-tts` 的 `zh-CN-YunyangNeural` 语音：
- 自然流畅的中文发音
- 语速调整为 -5%

## 许可证

MIT License

## 相关项目

- [Orpheus-TTS](https://github.com/canopyai/Orpheus-TTS) - Orpheus TTS 原始项目
- [Manim](https://github.com/ManimCommunity/manim) - 动画引擎
