import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers

HOST = "https://spb.hh.ru"
LINK_HOST = "/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_\
            field=description&enable_snippets=true&text=python"
LINK = f"{HOST}{LINK_HOST}"


def get_headers():
    return Headers(browser="Google Chrome", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


url_list = []
vacanc_scr = []


def scrap_vacancy_links():
    soup = BeautifulSoup(get_text(LINK), "lxml")
    vacanc_all = soup.find_all("a", class_="serp-item__title")
    for vacancy in vacanc_all:
        links = vacancy["href"]
        response_links = requests.get(links, headers=get_headers())
        links_parsed = BeautifulSoup(response_links.text, "lxml")
        vacancy_div = links_parsed.find("div", {"data-qa": "vacancy-description"})
        if not vacancy_div:
            continue
        if ("Django" or "Flask") in vacancy_div.text:
            url_list.append(links)
    return url_list


def scrap_vacancy():
    for urll in url_list:
        link = requests.get(urll, headers=get_headers())
        vacancy_parsed = BeautifulSoup(link.text, "lxml")
        salary = vacancy_parsed.find(
            "span", class_="bloko-header-section-2 bloko-header-section-2_lite"
        )
        if not salary:
            continue
        city = vacancy_parsed.find("p", {"data-qa": "vacancy-view-location"})
        if not city:
            city = vacancy_parsed.find("span", {"data-qa": "vacancy-view-raw-address"})
            if not city:
                continue
        company_name = vacancy_parsed.find("a", {"data-qa": "vacancy-company-name"})
        if not company_name:
            continue
        vacanc_scr.append(
            {
                "ссылка": urll,
                "зарплата": salary.text,
                "город": city.text,
                "компания": company_name.text,
            }
        )
    return vacanc_scr


if __name__ == "__main__":
    scrap_vacancy_links()
    scrap_vacancy()
    with open("vacanspb.json", "w", encoding="utf-8") as data:
        json.dump(vacanc_scr, data, indent=2, ensure_ascii=False)
