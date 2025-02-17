from transformers import pipeline  

# Load a text classification pipeline (you can fine-tune a model for better results)
classifier = pipeline("text-classification", model="facebook/bart-large-mnli")

def remove_ads(text):  
    sentences = text.split("\n")  # Split text into lines  
    filtered_sentences = [s for s in sentences if classifier(s, candidate_labels=["advertisement", "news"])["labels"][0] == "news"]  
    return "\n".join(filtered_sentences)  

news_text = """  
17. Oktober 2024, 13:56 Uhr  
Ein Sturz von einem Gerüst in Stuttgart endet für einen Arbeiter tödlich.  
Direkt aus dem dpa-Newskanal: Dieser Text wurde automatisch von der Deutschen Presse-Agentur (dpa) übernommen und von der SZ-Redaktion nicht bearbeitet.  
Stuttgart (dpa/lsw) - Ein Arbeiter ist bei Abrissarbeiten an einem Mehrfamilienhaus in Stuttgart ums Leben gekommen.  
Lesen Sie mehr zum Thema In anspruchsvollen Berufsfeldern im Stellenmarkt der SZ.  
Sie möchten die digitalen Produkte der SZ mit uns weiterentwickeln? Bewerben Sie sich jetzt!Jobs bei der SZ Digitale Medien  
"""

clean_text = remove_ads(news_text)  
print(clean_text)  
