from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import csv
import time

# Configurar opciones de Chrome
options = webdriver.ChromeOptions()
options.add_argument(r"user-data-dir=C:\Users\Diogo\AppData\Local\Google\Chrome\User Data")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

stealth(driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

driver.get("https://www.sciencedirect.com/")

try:
    search_query = '("Startup" OR "Entrepreneurship") AND ("Chatbot" OR "Generative AI") AND "Trends" NOT ("Healthcare" OR "Finance")'
    full_url = f"https://www.sciencedirect.com/search?qs={search_query}&show=25"
    driver.get(full_url)
    time.sleep(5)

    articles = driver.find_elements(By.CSS_SELECTOR, "ol.search-result-wrapper li.ResultItem")
    results = []
    
    for article in articles:
        try:
            title_element = article.find_element(By.CSS_SELECTOR, "h2 a")
            title = title_element.text
            doi = article.get_attribute("data-doi")
            year = article.find_element(By.CSS_SELECTOR, ".srctitle-date-fields span:nth-child(2)").text
            journal = article.find_element(By.CSS_SELECTOR, ".subtype-srctitle-link").text
            authors = [a.text for a in article.find_elements(By.CSS_SELECTOR, "ol.Authors li span.author")]
            
            # Extraer PDF
            try:
                pdf_link = article.find_element(By.CSS_SELECTOR, "a.download-link").get_attribute("href")
            except:
                pdf_link = "No disponible"

            # Extraer Abstract
            abstract = "No disponible"
            try:
                abstract_button = article.find_element(By.CSS_SELECTOR, 'button[aria-label="Abstract"]')
                driver.execute_script("arguments[0].click();", abstract_button)
                time.sleep(0.5)  # Esperar carga del abstract
                abstract_element = article.find_element(By.CSS_SELECTOR, "div.ArticlePreview div.abstract-section p")
                abstract = abstract_element.text
            except Exception as e:
                print(f"Error obteniendo abstract: {e}")

            results.append({
                "Título": title,
                "DOI": doi,
                "Año": year,
                "Revista": journal,
                "Autores": authors,
                "PDF": pdf_link,
                "Abstract": abstract
            })
        except Exception as e:
            print(f"Error extrayendo artículo: {e}")

    # Guardar en CSV con nuevo campo Abstract
    csv_file = "articulos.csv"
    headers = ["Título", "DOI", "Año", "Revista", "Autores", "PDF", "Abstract"]
    
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for res in results:
            writer.writerow([
                res["Título"],
                res["DOI"],
                res["Año"],
                res["Revista"],
                ", ".join(res["Autores"]),
                res["PDF"],
                res["Abstract"]
            ])

    print(f"✅ Archivo CSV generado: {csv_file}")

finally:
    driver.quit()