import re
import requests
from bs4 import BeautifulSoup
import csv
from lxml import html


def write_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Episode No.",
            "Episode Name",
            "Synopsis",
            "Plot",
            "Characters Appeared",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for episode_number, (name, synopsis, plot, char) in data.items():
            writer.writerow(
                {
                    "Episode No.": episode_number,
                    "Episode Name": name,
                    "Synopsis": synopsis,
                    "Plot": plot,
                    "Characters Appeared": char,
                }
            )


def get_url():
    url = "https://kimetsu-no-yaiba.fandom.com/wiki/Category:Episodes"

    # send a request to the URL and get the response
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
        },
    )

    # parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    blocks = soup.find_all("a", class_="category-page__member-link")
    base_url = "https://kimetsu-no-yaiba.fandom.com"
    hrefs = [base_url + a["href"] for a in blocks]

    def extract_episode_number(url):
        return int(re.findall(r"\d+", url)[-1])

    hrefs = sorted(hrefs, key=extract_episode_number)
    print("Got the urls")
    return hrefs


def get_episode_info(urls):
    episode_info = {}
    for url in urls:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3 Edge/16.16299"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        eps = soup.find("h1", class_="page-header__title").get_text().strip()
        title = (
            soup.find(
                "h2", class_="pi-item pi-item-spacing pi-title pi-secondary-background"
            )
            .get_text()
            .strip()
        )
        p_tags = soup.find_all("p")
        synopsis = p_tags[2].text.strip()
        plot = ""
        ul_tags = soup.find_all("ul")
        char = ul_tags[55].text.strip()
        char = char.replace("\n", ", ")
        # Remove the last comma and space

        for p_tag in p_tags[3:]:
            plot += p_tag.get_text().strip() + " "
        plot = plot.replace("/", "")
        episode_number = eps.split()[-1]
        episode_name = "".join(title)
        episode_info[episode_number] = (episode_name, synopsis, plot, char)
    return episode_info


urls = get_url()
episodes_info = get_episode_info(urls)
write_to_csv(episodes_info, "demon_slayer.csv")
