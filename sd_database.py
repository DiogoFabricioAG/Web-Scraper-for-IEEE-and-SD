from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import csv
import time

# Configurar opciones de Chrome
options = webdriver.ChromeOptions()

# 1️⃣ Usa un perfil real de Chrome (cambia TU_USUARIO por el tuyo)
options.add_argument(r"user-data-dir=C:\Users\Diogo\AppData\Local\Google\Chrome\User Data")
options.add_argument("--profile-directory=Default")

# 2️⃣ Evita detección de Selenium
options.add_argument("--disable-blink-features=AutomationControlled")

# 3️⃣ Proxy (opcional, si necesitas cambiar de IP)
# options.add_argument("--proxy-server=http://usuario:contraseña@ip_proxy:puerto")

# Iniciar WebDriver con las opciones
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Aplicar stealth para ocultar Selenium
stealth(driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

# Navegar a ScienceDirect
driver.get("https://www.sciencedirect.com/")

try:
    # 1️⃣ Buscar en ScienceDirect con &show=100
    search_query = '("Startup" OR "Entrepreneurship") AND ("Chatbot" OR "Generative AI") AND "Trends" NOT ("Healthcare" OR "Finance")'
    base_url = "https://www.sciencedirect.com/search?qs="
    full_url = f"{base_url}{search_query}&show=100"
    driver.get(full_url)
    
    time.sleep(5)  # Esperar que cargue la página

    # Encontrar la lista de artículos
    articles = driver.find_elements(By.CSS_SELECTOR, "ol.search-result-wrapper li.ResultItem")

    results = []
    
    for article in articles:
        try:
            # Extraer datos
            title_element = article.find_element(By.CSS_SELECTOR, "h2 a")
            title = title_element.text
            doi = article.get_attribute("data-doi")
            year = article.find_element(By.CSS_SELECTOR, ".srctitle-date-fields span:nth-child(2)").text
            journal = article.find_element(By.CSS_SELECTOR, ".subtype-srctitle-link").text
            authors = [a.text for a in article.find_elements(By.CSS_SELECTOR, "ol.Authors li span.author")]
            
            # Verificar si hay enlace al PDF
            try:
                pdf_link = article.find_element(By.CSS_SELECTOR, "a.download-link").get_attribute("href")
            except:
                pdf_link = "No disponible"

            # Guardar datos
            results.append({
                "Título": title,
                "DOI": doi,
                "Año": year,
                "Revista": journal,
                "Autores": authors,
                "PDF": pdf_link
            })
        except Exception as e:
            print(f"Error extrayendo un artículo: {e}")

    # Guardar resultados en CSV
    csv_file = "articulos.csv"
    headers = ["Título", "DOI", "Año", "Revista", "Autores", "PDF"]

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Escribir encabezados

        for res in results:
            writer.writerow([
                res["Título"],
                res["DOI"],
                res["Año"],
                res["Revista"],
                ", ".join(res["Autores"]),  # Convertir lista de autores en una cadena
                res["PDF"]
            ])

    print(f"✅ Archivo CSV generado: {csv_file}")

finally:
    driver.quit()