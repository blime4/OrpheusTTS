#!/usr/bin/env python3
"""Generate Chinese narration audio for each Orpheus TTS tutorial scene using edge-tts."""

import asyncio
import edge_tts
import os

VOICE = "zh-CN-YunyangNeural"
OUTPUT_DIR = "audio"

# Scene durations (seconds) for reference:
# Scene1: 28.1s, Scene2: 31.6s, Scene3: 31.1s, Scene4: 53.2s
# Scene5: 39.5s, Scene6: 33.6s, Scene7: 38.4s

SCRIPTS = {
    "scene1": (
        "欢迎来到 Orpheus TTS 架构详解。"
        "Orpheus 是一个基于大语言模型的文本转语音系统，"
        "它能够生成自然、富有表现力的语音。"
        "整个系统由三大核心模块组成。"
        "第一，文本处理模块，负责将输入文本转化为 Token。"
        "第二，LLM 主干网络，基于 Llama 架构，自回归地生成音频 Token。"
        "第三，SNAC 编解码器，负责音频信号的压缩与重建。"
        "这三个模块协同工作，实现了自然、多情感风格的语音合成。"
    ),
    "scene2": (
        "首先来看文本分词的过程。"
        "当我们输入一段中文文本，比如，今天天气真不错，"
        "系统会使用 Llama Tokenizer 对文本进行分词处理。"
        "分词器将文本拆分为多个子词单元，"
        "例如，今天、天气、真、不错。"
        "每个子词会被映射为一个唯一的数字 ID，也就是 Token ID。"
        "这些 Token ID 就是 LLM 主干网络的输入。"
        "值得注意的是，Orpheus 复用了 Llama 的分词器，"
        "这使得文本编码与语言模型无缝衔接。"
    ),
    "scene3": (
        "接下来是 LLM 主干网络。"
        "Orpheus 采用了 Llama 架构作为核心骨干。"
        "网络由多层 Transformer 模块堆叠而成，"
        "每层包含自注意力机制和前馈网络。"
        "文本 Token 从底部输入，经过逐层处理后，"
        "在顶部输出音频 Token，也就是 SNAC 编码。"
        "整个过程是自回归的，模型逐个生成音频 Token，"
        "这使得系统天然支持流式输出。"
    ),
    "scene4": (
        "现在我们来对比传统音频编码方案和 SNAC 的区别。"
        "左边是传统方案，比如 SoundStorm、EnCodec 和 DAC。"
        "它们使用统一速率的码本结构，每一层的 Token 数量相同。"
        "以四层码本为例，每层都是 50 个 Token 每秒，"
        "总计需要 200 个 Token 每秒，数据量非常大。"
        "右边是 SNAC 的多尺度码本结构。"
        "第一层是粗粒度，只需要 12 个 Token 每秒，捕捉语音的整体轮廓。"
        "第二层是中粒度，24 个 Token 每秒，补充更多细节。"
        "第三层是细粒度，48 个 Token 每秒，还原精细的声学特征。"
        "总计只需要 84 个 Token 每秒，比传统方案减少了一半以上。"
        "更少的 Token 意味着 LLM 生成更快、更高效，"
        "同时音质却没有损失。这就是 SNAC 的核心优势。"
    ),
    "scene5": (
        "那么，不同层的 Token 如何送入 LLM 呢？"
        "答案是金字塔交错，也叫 Pyramid Interleaving。"
        "我们可以看到三层 Token，粗粒度 L1 有 2 个，"
        "中粒度 L2 有 4 个，细粒度 L3 有 8 个。"
        "交错展平后，它们按照特定顺序排列成一维序列。"
        "每个时间步内，先放一个粗粒度 Token，"
        "再放两个中粒度 Token，最后放四个细粒度 Token。"
        "这种金字塔结构让 LLM 能够从粗到细逐步生成，"
        "既保证了生成质量，又适配了自回归的生成方式。"
    ),
    "scene6": (
        "最后来看 SNAC 解码器如何将 Token 还原为音频。"
        "三层 Token 首先通过码本查找，转换为对应的向量表示。"
        "然后经过多级上采样模块，逐步提升时间分辨率。"
        "每一级上采样将分辨率提高两倍。"
        "从粗粒度到细粒度，信息逐层融合叠加，"
        "最终输出 24kHz 采样率的高质量语音波形。"
        "这种从粗到细的重建方式，确保了语音的自然和清晰。"
    ),
    "scene7": (
        "现在让我们回顾整个端到端流程。"
        "输入文本首先经过 Tokenizer 分词，"
        "然后送入基于 Llama 的 LLM 主干网络。"
        "LLM 自回归地生成交错的音频 Token 序列。"
        "接着，反交错模块将一维序列还原为多层 Token。"
        "最后，SNAC 解码器将 Token 重建为音频波形。"
        "整个系统支持流式生成，可以实时输出语音。"
        "总结一下 Orpheus 的三大优势。"
        "高质量，多尺度 SNAC 编码保证了音质。"
        "低延迟，流式自回归生成实现了实时输出。"
        "灵活性，基于 LLM 架构，易于扩展和微调。"
        "感谢观看！"
    ),
}


async def generate_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, text in SCRIPTS.items():
        output_path = os.path.join(OUTPUT_DIR, f"{name}.mp3")
        print(f"Generating {output_path} ...")
        communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
        await communicate.save(output_path)
        print(f"  Done: {output_path}")


if __name__ == "__main__":
    asyncio.run(generate_all())
