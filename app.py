from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests

# Don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # Do not change this

# Insert the scraping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2023-01-01,2023-7-31')
soup = BeautifulSoup(url_get.content, "html.parser")

# Find your right key here
table = soup.find('div', attrs={'class': 'lister-list'})
row = table.find_all('div', attrs={'class': 'lister-item mode-advanced'})

row_length = len(row)

temp = []  # Init
items = soup.find_all('div', class_='lister-item-content')
for item in items:

    # Pengambilan title film
    title = item.find('h3', class_='lister-item-header').a.text

    # Pengambilan data kolom IMDB Rating & Pengolahan
    imdb_rating_a = item.find('div', class_='ratings-bar')
    imdb_rating = imdb_rating_a.strong.text if imdb_rating_a and imdb_rating_a.strong else 'N/A'

    # Pengambilan data kolom Metascore & Pengolahan
    metascore_a = item.find('div', class_='inline-block ratings-metascore')
    metascore = metascore_a.text.strip() if metascore_a else '0'
    metascore = metascore.replace("\n", "")
    metascore = metascore.replace("Metascore", "")

    # Pengambilan data kolom Vote & Pengolahan
    votes_a = item.find('span', attrs={'name': 'nv'})
    votes = votes_a['data-value'] if votes_a and 'data-value' in votes_a.attrs else 'N/A'

    temp.append((title, imdb_rating, metascore, votes))

temp = temp[::-1]

# Change into a DataFrame
df = pd.DataFrame(temp, columns=('Title', 'IMDB Rating', 'Metascore', 'Votes'))

# Insert data wrangling here
dftop = df.tail(7)

dftop['IMDB Rating'] = dftop['IMDB Rating'].astype('float64')
dftop[['Votes', 'Metascore']] = dftop[['Votes', 'Metascore']].astype('int64')
titleindex = dftop.set_index('Title')

# End of data wrangling

@app.route("/")
def index():
    card_data = f'{titleindex["IMDB Rating"].mean().round(2)}'  # Be careful with the " and '

    # Generate plot for By IMDB Rating
    ax_imdb = titleindex['IMDB Rating'].plot(kind='barh')

    # Rendering plot for By IMDB Rating
    figfile_imdb = BytesIO()
    plt.figure(ax_imdb.get_figure())
    plt.savefig(figfile_imdb, format='png', transparent=True)
    figfile_imdb.seek(0)
    figdata_png_imdb = base64.b64encode(figfile_imdb.getvalue())
    plot_result_imdb = str(figdata_png_imdb)[2:-1]

    # Generate plot for By Votes
    ax_votes = titleindex['Votes'].plot(kind='barh')

    # Rendering plot for By Votes
    figfile_votes = BytesIO()
    plt.figure(ax_votes.get_figure())
    plt.savefig(figfile_votes, format='png', transparent=True)
    figfile_votes.seek(0)
    figdata_png_votes = base64.b64encode(figfile_votes.getvalue())
    plot_result_votes = str(figdata_png_votes)[2:-1]

    # Generate plot for By Metascore
    ax_metascore = titleindex['Metascore'].plot(kind='barh')

    # Rendering plot for By Metascore
    figfile_metascore = BytesIO()
    plt.figure(ax_metascore.get_figure())
    plt.savefig(figfile_metascore, format='png', transparent=True)
    figfile_metascore.seek(0)
    figdata_png_metascore = base64.b64encode(figfile_metascore.getvalue())
    plot_result_metascore = str(figdata_png_metascore)[2:-1]


    return render_template('index.html',
                           card_data=card_data,
                           plot_result=plot_result_imdb,  # Pass the IMDB Rating chart result
                           plot_result1=plot_result_votes,  # Pass the Votes chart result
                           plot_result2=plot_result_metascore  # Pass the Votes chart result
                           )

if __name__ == "__main__":
    app.run(debug=True)
