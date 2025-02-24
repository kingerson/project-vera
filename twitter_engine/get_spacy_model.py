"""
Creado el 6/9/2024 a las 12:08 PM

@author: jacevedo
"""

import requests
import spacy
from spacy.cli import download
def download_model(model_name):
    url = f"https://github.com/explosion/spacy-models/releases/download/{model_name}/{model_name}.tar.gz"
    print(url)
    # Disable SSL verification
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        with open(f"{model_name}.tar.gz", "wb") as f:
            f.write(response.content)
            print(f"{model_name} downloaded successfully.")
    else:
        print(f"Failed to download {model_name}. Status code: {response.status_code}") # Replace 'es_dep_news_trf' with the actual model name download_model("es_dep_news_trf")

model = 'es_dep_news_trf'
download_model(model)