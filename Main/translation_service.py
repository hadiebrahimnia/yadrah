from transformers import pipeline

def translate_en_to_fa_simple(text):
    translator = pipeline(
        "translation",
        model="facebook/nllb-200-distilled-600M",
        src_lang="eng_Latn",
        tgt_lang="fas_Arab"
    )
    return translator(text)[0]['translation_text']
