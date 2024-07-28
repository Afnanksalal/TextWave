from transformers import pipeline

# Translation pipelines 
device = "cpu"  
translation_pipelines = {
    "ES": pipeline("translation", model="Helsinki-NLP/opus-mt-en-es", device=device),
    "FR": pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr", device=device),
    "ZH": pipeline("translation", model="Helsinki-NLP/opus-mt-en-zh", device=device),
    "JP": pipeline("translation", model="Helsinki-NLP/opus-tatoeba-en-ja", device=device),
}