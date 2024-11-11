import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Caminho para o ChromeDriver (ajustado para um caminho no Linux)
caminho_chromedriver = '/usr/local/bin/chromedriver'

options = webdriver.ChromeOptions()
# Executa o navegador em segundo plano (headless)
options.add_argument('--headless')
options.add_argument('--no-sandbox')  # Necessário em ambientes de container
options.add_argument('--disable-dev-shm-usage')  # Previne problemas de memória compartilhada
options.add_argument('--remote-debugging-port=9222')  # Permite a depuração remota
options.add_argument('--disable-software-rasterizer')  # Para desativar problemas gráficos

# Adicionando a opção de inicialização sem abrir janela
options.add_argument('--disable-gpu')  # Necessário para rodar em servidores com poucos recursos gráficos
options.add_argument('--start-maximized')  # Inicia com a janela maximizada, útil em ambientes de container


# Inicializando o driver com o caminho exato
service = Service(executable_path=caminho_chromedriver)
driver = webdriver.Chrome(service=service, options=options)

# URL da página de promoções da Steam
url = 'https://steamdb.info/sales/'

# Abrindo a página
driver.get(url)

# Aumentando o tempo de espera para 60 segundos
wait = WebDriverWait(driver, 60)

# Espera explícita para garantir que a tabela de promoções seja carregada
try:
    # Tentando esperar até que o conteúdo da página seja carregado (elementos de jogos)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "app")))
    print("Página carregada com sucesso!")
except Exception as e:
    print(f"Erro ao aguardar carregamento dos elementos: {e}")
    driver.quit()

# Simular rolagem da página para garantir que mais elementos sejam carregados
for i in range(3):  # Rolando 3 vezes para carregar mais dados
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(3)  # Espera para garantir que a página tenha tempo de carregar

# Extraindo os dados dos jogos
jogos_dados = []
jogos = driver.find_elements(By.CLASS_NAME, "app")

for jogo in jogos:
    try:
        # Nome do jogo
        nome_jogo = jogo.find_element(By.CLASS_NAME, "b").text

        # Preço do jogo (tratamento adicional)
        preco_elemento = jogo.find_element(
            By.CSS_SELECTOR, 'td[data-sort][class="dt-type-numeric"]')
        preco_jogo = preco_elemento.text.strip() if preco_elemento else 'Preço não encontrado'

        # Link para o jogo
        link_jogo = jogo.find_element(By.CLASS_NAME, "b").get_attribute("href")

        # Adicionando os dados à lista
        jogos_dados.append(
            {"Nome do Jogo": nome_jogo, "Preço": preco_jogo, "Link": link_jogo})

    except Exception as e:
        print(f"Erro ao capturar informações de um jogo: {e}")

# Verificando se os dados foram extraídos
if jogos_dados:
    # Convertendo os dados para um DataFrame do Pandas
    df_jogos = pd.DataFrame(jogos_dados)

    # Salvando em um arquivo Excel
    try:
        # Caminho para salvar o arquivo (ajuste conforme necessário)
        caminho_arquivo = '/home/usuario/Documents/jogos_promocoes_steam.xlsx'
        df_jogos.to_excel(caminho_arquivo, index=False)
        print(f"Planilha criada com sucesso! Salvo em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar a planilha: {e}")
else:
    print("Nenhum dado de jogos foi encontrado.")

# Fechando o driver corretamente
driver.quit()


