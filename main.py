# app.py
from flask import Flask, render_template, request
from game_finder import buscar_jogo_steam
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    nome_jogo = request.form.get('nome_jogo', '').strip()
    
    if not nome_jogo:
        return render_template('index.html', erro="Por favor, digite o nome de um jogo")
    
    try:
        resultado = buscar_jogo_steam(nome_jogo)
        
        if resultado:
            return render_template('resultado.html', nome=nome_jogo, jogo=resultado)
        else:
            return render_template('index.html', 
                                 erro=f"Não foi possível encontrar informações para '{nome_jogo}'")
    
    except Exception as e:
        return render_template('index.html', 
                             erro=f"Erro ao buscar jogo: {str(e)}")

@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)