import requests
from bs4 import BeautifulSoup

def scrape_quotes():
    url = "https://quotes.toscrape.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    quotes = soup.find_all("span", class_="text")
    authors = soup.find_all("small", class_="author")

    with open("quotes.txt", "w", encoding="utf-8") as file:
        for i in range(len(quotes)):
            file.write(quotes[i].text + "\n")
            file.write("— " + authors[i].text + "\n")
            file.write("---\n")

    print("Done! Check quotes.txt file")

scrape_quotes()
