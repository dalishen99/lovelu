# -*- coding: utf-8 -*-
"""
用 Microsoft Edge 的免费神经网络 TTS 给每条"我爱你"生成 MP3
不需要 API Key。声音是 Microsoft 自家训练的 Neural Voices，接近真人朗读
"""
import asyncio
import os
import edge_tts

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(OUT_DIR, exist_ok=True)

# 每一站对应的：文件名（不含扩展名）/ 文本 / Edge TTS 的 voice 名
# Edge 的 neural voice 在 https://learn.microsoft.com/azure/ai-services/speech-service/language-support 里
PHRASES = [
    ("zh-CN",  "我爱你",                                 "zh-CN-XiaoxiaoNeural"),
    ("zh-HK",  "我愛你",                                 "zh-HK-HiuMaanNeural"),       # 粤语
    ("zh-TW",  "我愛妳",                                 "zh-TW-HsiaoChenNeural"),
    ("ko-KR",  "사랑해",                                  "ko-KR-SunHiNeural"),
    ("ja-JP",  "愛してる",                                "ja-JP-NanamiNeural"),
    ("fil-PH", "Mahal kita",                            "fil-PH-BlessicaNeural"),
    ("id-ID",  "Aku cinta kamu",                        "id-ID-GadisNeural"),
    ("vi-VN",  "Anh yêu em",                            "vi-VN-HoaiMyNeural"),
    ("th-TH",  "ฉันรักเธอ",                               "th-TH-PremwadeeNeural"),
    ("hi-IN",  "मैं तुमसे प्यार करता हूँ",              "hi-IN-SwaraNeural"),
    ("fa-IR",  "دوستت دارم",                             "fa-IR-DilaraNeural"),
    ("he-IL",  "אני אוהב אותך",                          "he-IL-HilaNeural"),
    ("ar-SA",  "أحبك",                                    "ar-SA-ZariyahNeural"),
    ("tr-TR",  "Seni seviyorum",                         "tr-TR-EmelNeural"),
    ("el-GR",  "Σ' αγαπώ",                               "el-GR-AthinaNeural"),
    ("ar-EG",  "بحبك",                                    "ar-EG-SalmaNeural"),
    ("sw-KE",  "Nakupenda",                              "sw-KE-ZuriNeural"),
    ("ru-RU",  "Я тебя люблю",                           "ru-RU-SvetlanaNeural"),
    ("pl-PL",  "Kocham Cię",                             "pl-PL-ZofiaNeural"),
    ("de-DE",  "Ich liebe dich",                         "de-DE-KatjaNeural"),
    ("nl-NL",  "Ik hou van jou",                         "nl-NL-ColetteNeural"),
    ("fr-FR",  "Je t'aime",                              "fr-FR-DeniseNeural"),
    ("it-IT",  "Ti amo",                                 "it-IT-ElsaNeural"),
    ("es-ES",  "Te amo",                                 "es-ES-ElviraNeural"),
    ("pt-PT",  "Amo-te",                                 "pt-PT-RaquelNeural"),
    ("en-GB",  "I love you",                             "en-GB-SoniaNeural"),
    ("is-IS",  "Ég elska þig",                           "is-IS-GudrunNeural"),
    ("en-US",  "I love you",                             "en-US-AriaNeural"),
    ("pt-BR",  "Eu te amo",                              "pt-BR-FranciscaNeural"),
    ("en-AU",  "I love you",                             "en-AU-NatashaNeural"),
    # 火奴鲁鲁夏威夷语 Edge 没有夏威夷语 voice，用美式英语女声念，依然很好听
    ("haw",    "Aloha au iā ʻoe",                       "en-US-JennyNeural"),
]

async def gen(slug, text, voice):
    out = os.path.join(OUT_DIR, f"{slug}.mp3")
    communicate = edge_tts.Communicate(text, voice, rate="-5%", pitch="+2Hz")
    await communicate.save(out)
    size = os.path.getsize(out)
    print(f"  [OK]   {slug:8} {voice:35} -> {size} bytes")

async def main():
    print(f"out dir: {OUT_DIR}")
    print(f"total {len(PHRASES)} phrases to generate\n")
    failed = []
    for slug, text, voice in PHRASES:
        try:
            await gen(slug, text, voice)
        except Exception as e:
            print(f"  [FAIL] {slug:8} {voice:35} {e}")
            failed.append((slug, voice, str(e)))
    print(f"\nDone. ok {len(PHRASES) - len(failed)} / {len(PHRASES)}")
    if failed:
        print("FAILED:")
        for slug, voice, err in failed:
            print(f"  - {slug} ({voice}): {err}")

if __name__ == "__main__":
    asyncio.run(main())
