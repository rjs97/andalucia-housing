from flask import Flask, render_template
import geopandas as gpd

app = Flask(__name__)

@app.route("/")
def home_english():
    return render_template('home_en.html')

@app.route("/es")
def home_spanish():
    return render_template('home_es.html')

@app.route("/airbnb-malaga/<lang>")
def airbnb_malaga(lang):
    return render_template(f'airbnb_malaga_{lang}.html')

@app.route("/airbnb-sevilla/<lang>")
def airbnb_sevilla(lang):
    return render_template(f'airbnb_sevilla_{lang}.html')

@app.route("/vivienda-malaga/<lang>")
def vivienda_malaga(lang):
    return render_template(f'vivienda_malaga_{lang}.html')

@app.route("/vivienda-sevilla/<lang>")
def vivienda_sevilla(lang):
    return render_template(f'vivienda_sevilla_{lang}.html')