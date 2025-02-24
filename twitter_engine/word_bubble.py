"""
Creado el 2/1/2024 a las 3:42 p. m.

@author: jacevedo
"""

#%%

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Sample text
text = "Python is an amazing programming language. It is widely used in data science, machine learning, web development, and more."

# Create a word cloud
wordcloud = WordCloud(width = 1400, height = 1000,
                background_color ='white',
                stopwords = set(),
                min_font_size = 10).generate(text)

# Display the word cloud
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
plt.show()

#%%

import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from matplotlib.font_manager import FontProperties


import pandas as pd

df = pd.read_excel(r"C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\LaSuperTeEscucha\2023_12\palabras_bancos.xlsx")
# Path to the Titillium Web font
font_path = 'C:\\Windows\\Fonts\\TitilliumWeb-SemiBold.ttf'  # Update with the correct file name
titillium_web_font = FontProperties(fname=font_path)

filtro_eif = df.eif == 'popular'
df[filtro_eif][['palabras', 'cantidad']]
# Sample text
text = "Python is an amazing programming language. It is widely used in data science, machine learning, web development, and more."

# Count the frequency of each word
word_counts = Counter(text.split())

# Prepare data for the word cloud
words = list(word_counts.keys())
sizes = list(word_counts.values())
max_size = max(sizes)

# Create a figure
plt.figure(figsize=(10, 6))

# Plot each word
for word, size in zip(words, sizes):
    plt.text(np.random.rand(), np.random.rand(), word,
             fontsize=(size / max_size) * 40,
             fontfamily='Titillium Web',
             color=plt.cm.viridis(np.random.rand()),
             ha='center', va='center')

# Display the word cloud
plt.axis('off')
plt.show()


#%%

import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from matplotlib.font_manager import FontProperties


import pandas as pd

df = pd.read_excel(r"C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\LaSuperTeEscucha\2023_12\palabras_bancos.xlsx")
# Path to the Titillium Web font
font_path = 'C:\\Windows\\Fonts\\TitilliumWeb-SemiBold.ttf'  # Update with the correct file name
titillium_web_font = FontProperties(fname=font_path)

palabras_exclusion = ['banco', 'popular', 'tener', 'hacer', 'reservas',
                      'banreservas', 'bhd', 'scotia', 'scotiabank',
                      'reelection', 'president']
filtro_eif = df.eif == 'popular'
filtro_palabras = df.palabras.isin(palabras_exclusion)
data = df[filtro_eif & ~filtro_palabras]

# Sample text
# Prepare data for the word cloud
words = list(data.palabras)
sizes = list(data.cantidad)
max_size = max(sizes)

# Create a figure
plt.figure(figsize=(10, 6))

# Plot each word
for word, size in zip(words, sizes):
    plt.text(np.random.rand(), np.random.rand(), word,
             # fontsize=(size / 50) * 40,
             # fontsize=(size / 50),
             fontsize=(size*2),

             # fontsize=size**3,
             color=plt.cm.GnBu(size*2/max_size),
             ha='center', va='center')
    # print(size**3)

# Display the word cloud
plt.axis('off')
plt.show()

#%%

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Sample text
text = "Python is an amazing programming language. It is widely used in data science, machine learning, web development, and more."

import pandas as pd

df = pd.read_excel(r"C:\Users\jacevedo\OneDrive - Superintendencia de Bancos de la Republica Dominicana\Documents\LaSuperTeEscucha\2023_12\palabras_bancos.xlsx")
# Path to the Titillium Web font
font_path = 'C:\\Windows\\Fonts\\TitilliumWeb-SemiBold.ttf'  # Update with the correct file name
titillium_web_font = FontProperties(fname=font_path)

palabras_exclusion = ['banco', 'popular', 'tener', 'hacer', 'dar', 'reservas',
                      'banreservas', 'bhd', 'scotia', 'scotiabank',
                      'reelection', 'president']
filtro_eif = df.eif == 'popular'
filtro_palabras = df.palabras.isin(palabras_exclusion)
filtro_palabras = df.palabras.isin(palabras_exclusion)
data = df[filtro_eif & ~filtro_palabras]

# Create a word cloud
wordcloud = WordCloud(width = 1400, height = 1000,
                background_color ='white',
                stopwords = set(palabras_exclusion + ['él', 'yo']),
                min_font_size = 10).generate(f' '.join(list(data.palabras)))

# Display the word cloud
plt.figure(figsize = (13, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
plt.show()
