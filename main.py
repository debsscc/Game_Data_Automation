# main.py
from flask import Flask, render_template, request
from game_finder import buscar_jogo_steam
import os
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    print("DEBUG: Pagina index acessada")
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    nome_jogo = request.form.get('nome_jogo', '').strip()
    
    print(f"DEBUG: Busca iniciada para: '{nome_jogo}'")
    
    if not nome_jogo:
        print("DEBUG: Nome do jogo vazio")
        return render_template('index.html', erro="Por favor, digite o nome de um jogo")
    
    try:
        print(f"DEBUG: Chamando buscar_jogo_steam('{nome_jogo}')")
        
        resultado = buscar_jogo_steam(nome_jogo)
        
        print(f"DEBUG: Resultado retornado - Tipo: {type(resultado)}")
        print(f"DEBUG: Resultado é None: {resultado is None}")
        
        if resultado:
            print(f"DEBUG: Busca bem-sucedida! Keys no resultado: {list(resultado.keys()) if resultado else 'N/A'}")
            print(f"DEBUG: Preco encontrado: {resultado.get('preco', 'N/A')}")
            print(f"DEBUG: Redirecionando para resultado.html")
            return render_template('resultado.html', nome=nome_jogo, jogo=resultado)
        else:
            print("DEBUG: Busca retornou None - mostrando erro")
            return render_template('index.html', 
                                 erro=f"Não foi possível encontrar informações para '{nome_jogo}'. Tente um jogo mais popular como 'Counter-Strike'.")
    
    except Exception as e:
        print(f"DEBUG: ERRO durante a busca: {str(e)}")
        print(f"DEBUG: Traceback completo:")
        traceback.print_exc()
        return render_template('index.html', 
                             erro=f"Erro ao buscar jogo: {str(e)}")

@app.route('/<path:path>')
def catch_all(path):
    print(f"DEBUG: Rota não encontrada acessada: {path}")
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"DEBUG: Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)