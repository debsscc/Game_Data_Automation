from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
import re
import os

logging.getLogger('selenium').setLevel(logging.WARNING)

def get_chromedriver_path():
    if os.path.exists('/usr/bin/chromedriver'):
        return '/usr/bin/chromedriver'
    
    # No Windows local
    env_path = os.environ.get('CHROMEDRIVER_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    # webdriver-manager (local development)
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeDriverManager().install()
    except Exception:
        return 'chromedriver'

CHROMEDRIVER_PATH = get_chromedriver_path()

SHORT_WAIT = 6  
MID_WAIT = 10

def _get_text_safe(driver, by, selector, wait=MID_WAIT):
    try:
        el = WebDriverWait(driver, wait).until(EC.presence_of_element_located((by, selector)))
        return el.text.strip()
    except Exception:
        try:
            els = driver.find_elements(by, selector)
            if els:
                return els[0].text.strip()
        except Exception:
            pass
    return "N/A"

def _get_attr_safe(driver, by, selector, attr="src", wait=SHORT_WAIT):
    try:
        el = WebDriverWait(driver, wait).until(EC.presence_of_element_located((by, selector)))
        return el.get_attribute(attr) or "N/A"
    except Exception:
        try:
            els = driver.find_elements(by, selector)
            if els:
                return els[0].get_attribute(attr) or "N/A"
        except Exception:
            pass
    return "N/A"

def _get_extra_market_data(driver, info_jogo):
    """Coleta dados extras para análise de mercado"""
    market_data = {}
    
    # 1. Dados de Performance Comercial
    try:
        similares = driver.find_elements(By.CSS_SELECTOR, ".recommended_page_content .similar_grid a, .similar_games_table a")
        market_data['concorrentes_diretos'] = [s.text.strip() for s in similares[:5] if s.text.strip()]
    except Exception:
        market_data['concorrentes_diretos'] = []
    
    # Posição em rankings
    market_data['top_seller'] = "Sim" if driver.find_elements(By.CSS_SELECTOR, ".top-seller, .bestseller") else "Não"
    
    # Tempo na loja
    try:
        data_lancamento = info_jogo.get('data', '')
        market_data['tempo_na_loja'] = data_lancamento if data_lancamento != "N/A" and data_lancamento else "N/A"
    except Exception:
        market_data['tempo_na_loja'] = "N/A"

    # 2. Análise de Conteúdo e Escopo
    try:
        dlcs = driver.find_elements(By.CSS_SELECTOR, ".game_area_dlc_row, .dlc_row")
        market_data['quantidade_dlcs'] = len(dlcs)
    except Exception:
        market_data['quantidade_dlcs'] = 0
    
    # Multiplayer/Co-op
    desc = info_jogo.get('descricao', '').lower()
    tags = info_jogo.get('tags', '').lower()
    all_text = desc + " " + tags
    
    market_data['tem_multijogador'] = any(word in all_text for word in ['multiplayer', 'online', 'pvp', 'co-op', 'coop', 'competitive'])
    market_data['tem_coop'] = any(word in all_text for word in ['co-op', 'cooperative', 'coop'])
    
    # Workshop/Mods
    market_data['tem_mods_suportados'] = any(word in all_text for word in ['workshop', 'mod', 'modding', 'user-generated'])
    
    # 3. Dados Técnicos
    try:
        tamanho = _get_text_safe(driver, By.CSS_SELECTOR, ".game_area_sys_req_full, .game_area_sys_req li", wait=SHORT_WAIT)
        market_data['tamanho_download'] = tamanho if "GB" in tamanho or "MB" in tamanho else "N/A"
    except Exception:
        market_data['tamanho_download'] = "N/A"
    
    # VR Suportado
    market_data['vr_suportado'] = any(word in all_text for word in ['vr', 'virtual reality', 'htc vive', 'oculus rift'])
    
    # 4. Suporte Pós-Venda
    try:
        atualizacoes = driver.find_elements(By.CSS_SELECTOR, ".eventDate, .update_date")
        market_data['atualizacoes_recentes'] = len(atualizacoes) > 0
    except Exception:
        market_data['atualizacoes_recentes'] = False
    
    # Cloud Saves
    market_data['tem_cloud_saves'] = len(driver.find_elements(By.CSS_SELECTOR, "[data-tooltip-text*='cloud'], [src*='cloud_saves']")) > 0
    
    # Controller
    market_data['suporte_controller'] = any(word in all_text for word in ['controller', 'gamepad', 'xbox', 'playstation'])
    
    # 5. Engajamento
    try:
        achievements = driver.find_elements(By.CSS_SELECTOR, ".achievement, [class*='achievement']")
        market_data['quantidade_achievements'] = len(achievements) if achievements else 0
    except Exception:
        market_data['quantidade_achievements'] = 0
    
    # Cartas Steam
    market_data['tem_cartas_steam'] = any(word in all_text for word in ['trading cards', 'steam cards'])
    
    # 6. Preço e Classificação
    try:
        preco = info_jogo.get('preco', 'N/A')
        if preco != "N/A" and "Free" not in preco:
            valor = re.findall(r'[\d,]+\.?\d*', preco)
            market_data['faixa_preco'] = f"R$ {valor[0]}" if valor else preco
        else:
            market_data['faixa_preco'] = "Gratuito" if "Free" in str(preco) else "N/A"
    except Exception:
        market_data['faixa_preco'] = "N/A"
    
    # Classificação etária
    try:
        classificacao_etaria = _get_text_safe(driver, By.CSS_SELECTOR, ".game_rating_icon, .esrb_rating", wait=SHORT_WAIT)
        market_data['classificacao_etaria'] = classificacao_etaria
    except Exception:
        market_data['classificacao_etaria'] = "N/A"
    
    return market_data

def _setup_driver_options():
    options = Options()
        
    # Configurações para ambiente de produção
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")
    
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-backgrounding-occluded-windows")
    
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
    }
    options.add_experimental_option("prefs", prefs)
    
    return options

def buscar_jogo_steam(nome_jogo):
    print(f"[scraper] Buscando '{nome_jogo}' na Steam...")

    options = _setup_driver_options()
    driver = None
    
    try:
        print("DEBUG [GAME_FINDER]: Tentando iniciar ChromeDriver...")
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        print("DEBUG [GAME_FINDER]: ChromeDriver iniciado com sucesso")

    except Exception as e:
            print(f"DEBUG [GAME_FINDER]: Erro ao iniciar ChromeDriver: {e}")
            try:
                print("DEBUG [GAME_FINDER]: Tentando fallback sem Service...")
                driver = webdriver.Chrome(options=options)
                print("DEBUG [GAME_FINDER]: ChromeDriver iniciado sem Service")
            except Exception as e2:
                print(f"DEBUG [GAME_FINDER]: Falha total ao iniciar ChromeDriver: {e2}")
                return None

    if not driver:
        print("DEBUG [GAME_FINDER]: Driver não inicializado")
        return None

    driver.set_page_load_timeout(15)
    driver.set_script_timeout(15)
    info_jogo = {}

    try:
        print("[scraper] Acessando Steam...")
        driver.get("https://store.steampowered.com/")
        print("DEBUG [GAME_FINDER]: Steam carregado")

        
        try:
            search_box = WebDriverWait(driver, SHORT_WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#store_nav_search_term"))
            )
        except TimeoutException:
            # Fallback para outros seletores
            search_selectors = [
                "input[name='term']",
                "input[type='search']",
                ".searchbox"
            ]
            for selector in search_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    search_box = elements[0]
                    break
            else:
                search_box = None

        if not search_box:
            print("[scraper] Campo de busca não encontrado")
            return None

        print(f"[scraper] Pesquisando por '{nome_jogo}'...")
        search_box.clear()
        search_box.send_keys(nome_jogo)
        search_box.send_keys(Keys.RETURN)

        try:
            primeiro_resultado = WebDriverWait(driver, MID_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".search_result_row"))
            )
            driver.execute_script("arguments[0].click();", primeiro_resultado)
        except TimeoutException:
            results = driver.find_elements(By.CSS_SELECTOR, ".search_result_row, .search_result_row a")
            if results:
                try:
                    driver.execute_script("arguments[0].click();", results[0])
                except Exception:
                    pass
            else:
                print("[scraper] Nenhum resultado encontrado")
                return None

        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass

        print("[scraper] Coletando informações básicas...")
        
        # Preço
        preco = _get_text_safe(driver, By.CSS_SELECTOR, ".discount_final_price, .game_purchase_price", wait=SHORT_WAIT)
        info_jogo['preco'] = preco
        if preco != "N/A" and ("Free" in preco or "Gratuito" in preco):
            info_jogo['status'] = "Gratuito"
        else:
            try:
                el = driver.find_elements(By.CSS_SELECTOR, ".discount_final_price")
                info_jogo['status'] = "Em promoção" if el else "Preço normal"
            except Exception:
                info_jogo['status'] = "Preço normal" if preco != "N/A" else "N/A"

        # Classificação
        info_jogo['classificacao'] = _get_text_safe(driver, By.CSS_SELECTOR, ".game_review_summary", wait=SHORT_WAIT)
        
        # Avaliações
        try:
            aval_text = _get_text_safe(driver, By.CSS_SELECTOR, ".responsive_reviewdesc", wait=SHORT_WAIT)
            if "(" in aval_text and ")" in aval_text:
                info_jogo['avaliacoes'] = aval_text.split("(")[-1].split(")")[0]
            else:
                info_jogo['avaliacoes'] = aval_text if aval_text != "N/A" else "N/A"
        except Exception:
            info_jogo['avaliacoes'] = "N/A"

        # Informações básicas
        info_jogo['data'] = _get_text_safe(driver, By.CSS_SELECTOR, ".date", wait=SHORT_WAIT)

        # Desenvolvedor e Publicadora
        try:
            devs = driver.find_elements(By.CSS_SELECTOR, ".dev_row a")
            info_jogo['desenvolvedor'] = devs[0].text.strip() if len(devs) > 0 else "N/A"
            info_jogo['publicadora'] = devs[1].text.strip() if len(devs) > 1 else info_jogo.get('desenvolvedor', "N/A")
        except Exception:
            info_jogo['desenvolvedor'] = "N/A"
            info_jogo['publicadora'] = "N/A"

        # Descrição
        info_jogo['descricao'] = _get_text_safe(driver, By.CSS_SELECTOR, ".game_description_snippet", wait=SHORT_WAIT)

        # Tags
        try:
            tags_els = driver.find_elements(By.CSS_SELECTOR, ".popular_tags a")
            tags = [t.text.strip() for t in tags_els if t.text.strip()]
            info_jogo['tags'] = ", ".join(tags) if tags else "N/A"
        except Exception:
            info_jogo['tags'] = "N/A"

        # Gênero
        try:
            detalhes_block = _get_text_safe(driver, By.CSS_SELECTOR, "div.details_block", wait=SHORT_WAIT)
            genero = "N/A"
            if detalhes_block != "N/A":
                for linha in detalhes_block.split("\n"):
                    if "Genre:" in linha or "Genres:" in linha:
                        genero = linha.replace("Genre:", "").replace("Genres:", "").strip()
                        break
            info_jogo['genero'] = genero
        except Exception:
            info_jogo['genero'] = "N/A"

        # Idiomas
        try:
            idiomas_els = driver.find_elements(By.CSS_SELECTOR, "#languageTable tr td:nth-child(1)")
            idiomas = [i.text.strip() for i in idiomas_els if i.text.strip()]
            info_jogo['idiomas'] = ", ".join(idiomas) if idiomas else "N/A"
        except Exception:
            info_jogo['idiomas'] = "N/A"

        # Imagem
        info_jogo['imagem'] = _get_attr_safe(driver, By.CSS_SELECTOR, "img.game_header_image_full", attr="src", wait=SHORT_WAIT)

        # Dados de mercado
        print("[scraper] Coletando dados de mercado...")
        market_data = _get_extra_market_data(driver, info_jogo)
        info_jogo.update(market_data)

        print("[scraper] Busca concluída com sucesso!")
        return info_jogo

    except Exception as e:
        print(f"[scraper][erro] Erro durante a busca: {e}")
        return None

    finally:
        if driver:
            try:
                driver.quit()
                print("DEBUG [GAME_FINDER]: Driver fechado")

            except Exception:
                pass