from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Configurar Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

ROWS_PER_PAGE = 100
PAGE_NUMBER = 1
QUERY = '("Startup" OR "Entrepreneurship" OR "New Venture" OR "Business Innovation" OR "Tech Startup" OR "Emerging Business") AND ("Chatbot" OR "Conversational Agent" OR "Virtual Assistant" OR "Dialogue System" OR "Generative AI" OR "Artificial Intelligence" OR "LLM" OR "Machine Learning") AND ("Trends" OR "Future Directions" OR "Emerging Technologies" OR "Innovations" OR "Market Analysis" OR "Adoption Patterns" OR "Industry Evolution")'

url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={QUERY}&highlight=true&matchPubs=true&returnFacets=ALL&returnType=SEARCH&rowsPerPage={ROWS_PER_PAGE}&pageNumber={PAGE_NUMBER}"	

driver.get(url)

# Esperar a que carguen los resultados
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "xpl-results-item"))
)

# Desplazarse para cargar todos los elementos
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Extraer datos
results = driver.find_elements(By.CSS_SELECTOR, "xpl-results-item")
data = []

for result in results:
    try:
        # Título
        title = result.find_element(By.CSS_SELECTOR, "h3 a").text
        
        # Autores
        authors = [author.text for author in result.find_elements(
            By.CSS_SELECTOR, "xpl-authors-name-list a span")]
        authors_str = ", ".join(authors)
        
        # PDF
        pdf = result.find_element(
            By.CSS_SELECTOR, "xpl-view-pdf a").get_attribute("href")
        if pdf.startswith("/"):
            pdf = f"https://ieeexplore.ieee.org{pdf}"
            
        # Navegar a la página del PDF para obtener DOI y abstract completo
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(pdf)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.abstract-desktop-div"))
        )
        
        # Extraer DOI
        try:
            doi = driver.find_element(
                By.CSS_SELECTOR, "div.stats-document-abstract-doi a").text
        except:
            doi = "N/A"
            
        # Extraer abstract completo
        try:
            abstract = driver.find_element(
                By.CSS_SELECTOR, "div.abstract-text div.u-mb-1 div[xplmathjax]").text
        except:
            abstract = "N/A"
            
        # Cerrar pestaña y volver a resultados
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        data.append({
            "title": title,
            "authors": authors_str,
            "doi": doi,
            "pdf": pdf,
            "abstract": abstract
        })
        
    except Exception as e:
        print(f"Error procesando artículo: {str(e)}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        continue

driver.quit()

# Guardar en CSV
with open('ieeexplore.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['title', 'authors', 'doi', 'pdf', 'abstract']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for item in data:
        # Limpiar saltos de línea en abstract
        cleaned_abstract = item['abstract'].replace('\n', ' ')
        writer.writerow({
            'title': item['title'],
            'authors': item['authors'],
            'doi': item['doi'],
            'pdf': item['pdf'],
            'abstract': cleaned_abstract
        })

print("Datos guardados en data_ieee.csv")