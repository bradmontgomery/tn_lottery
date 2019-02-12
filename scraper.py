"""
Scrapes winner data starting at:
https://www.tnlottery.com/winners?page=0

Then counts the amounts & the games.

"""
import re
import requests
import statistics

from collections import Counter, defaultdict
from html.parser import HTMLParser


URL = "https://www.tnlottery.com/winners?page={page}"
MAX_PAGES = 20


class Parser(HTMLParser):
    """
    I want content from:

        li
            div.views-field.views-field-field-prize-amount
                div.field-content.prize-amount
    And:

        li
            div.views-field.views-field-field-game-name
                div.field-content.game-name

    """
    active = False
    which = None
    games = []
    amounts = []

    def handle_starttag(self, tag, attrs):
        classes = [val for attr, val in attrs if attr == "class"]
        classes = ' '.join(classes).split()

        if tag == "div" and 'prize-amount' in classes:
            self.active = True
            self.which = 'amounts'
        elif tag == "div" and 'game-name' in classes:
            self.active = True
            self.which = 'games'

    def handle_endtag(self, tag):
        if tag == "div":
            self.active = False

    def handle_data(self, data):
        if self.active and data and self.which == "games":
            self.games.append(data.strip())
        elif self.active and data and self.which == "amounts":
            self.amounts.append(data.strip())

    def get_data(self):
        return list(zip(self.games, self.amounts))


parser = Parser()


def fetch_and_parse(page=0):
    url = URL.format(page=page)
    resp = requests.get(url)

    content = None
    if resp.status_code == 200:
        content = resp.content.decode('utf-8')
        parser.feed(content)

    return resp.status_code


if __name__ == "__main__":

    page = 0
    while fetch_and_parse(page) == 200 and page < MAX_PAGES:
        print(f"Got page {page}...")
        page += 1

    # Grab data from the parser.
    data = parser.get_data()

    # Print some common stuff...
    print("The Most commonly won games are:")
    c = Counter([g for g, _ in data])
    for game, count in c.most_common(5):
        print(f"- {game} ({count} wins)")

    print("The most commonly won amounts are:")
    c = Counter([amount for _, amount in data])
    for amount, count in c.most_common(5):
        print(f"- {amount} ({count} wins)")

    return

    # TODO: ----- figure out how to parse amounts like: ----------------
    # - $1,000 a Week for Life
    # - $259.8 Million
    # - $61 Million
    # - VIP Rewards Drawing

    # Which games pay out the best...
    results = []
    for game, amount in [(g, a.replace("$", "").replace(",", "")) for g, a in data]:
        try:
            amts = re.finall(r'\d+', amount)
            if amts:
                results.append((game, int(amts[0])))
        except (ValueError, AttributeError, TypeError) as err:
            print(f"Unable to parse: {game}, {amount}")
            print(err)
    data = sorted(results, lambda t: t[1])

    d = defaultdict(list)
    for game, amount in data:
        d[game].append(amount)

    results = []
    for game, values in d.items():
        m = statistics.mean(values)
        results.append((game, m))
    results = sorted(results, lambda t: t[1])
    print("The best-paying games on average are:")
    for game, amount in results:
        print(f"- {game}: ${amount:,}")
