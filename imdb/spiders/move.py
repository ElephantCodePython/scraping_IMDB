import scrapy, re, logging
from scrapy_playwright.page import PageMethod
from selectolax.lexbor import LexborHTMLParser
from scrapy.loader import ItemLoader
from imdb.items import ImdbItem


# scroll page
scroll_js = """ () => new Promise(async (resolve) => {
    let count = 0; const maxCount = 10;
    while (count < maxCount) {
        const heightOld = document.documentElement.scrollHeight;
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 500));
        const heightNew = document.documentElement.scrollHeight;
        if (heightNew === heightOld) { count++; } else { count = 0; }
    }
    resolve();
})
"""

# pat
_PAT = re.compile(
        r'(TV-(?:Y7|Y|G|PG|14|MA)|'   # US TV
        r'NC-17|PG-13|PG|G|R|X|'      # US MPA
        r'FSK\s?(?:0|6|12|16|18)|'    # Germany
        r'PG12|R15\+|R18\+|'          # Japan
        r'MA15\+|R18\+|X18\+|RC|M|'   # Australia
        r'0\+|6\+|12\+|16\+|18\+|'    # Russia
        r'18A|14A|'                   # Canada
        r'R18|12A|18|15|12|U|'        # UK BBFC
        r'UA|A|S|'                    # India
        r'All|15|'                    # Korea
        r'10|16|'                     # France
        r'AL|6|9|'                    # Netherlands 
        r'TP|7|'                      # Spain
        r'T|VM14|VM18|'               # Italy
        r'12|18)',
        re.IGNORECASE
    )

# --- Movie info parser ---
def info_move(information):
    result = {}
    for info in information:
        s = info.text(strip=True)

        # Year
        if s.isdigit():
            y = int(s)
            if 1900 <= y <= 2050:
                result["release_year"] = str(y)

        # Year range
        match = re.match(r'^(\d{4})\s*[-_–]?\s*(\d{4})$', s)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            if 1900 <= start <= end <= 2050:
                result["release_year"] = f"{start}-{end}"

        # Runtime
        match = re.match(r'^(\d+\s*h(?:ours?)?\s*)?(\d+\s*m(?:in(?:utes)?)?)?$', s.lower())
        if match:
            runtime_str = " ".join([g for g in match.groups() if g])
            if runtime_str:
                result["runtime"] = runtime_str.strip()


        # Rating
        ratings = _PAT.findall(s)
        if ratings:
            result["age_rating"] = ratings[0]

    return result


# --- TV info parser ---
def info_TV(information):
    result = {}
    FORMAT_PAT = re.compile(
        r'\b(?:TV\s+Mini\s+Series|TV\s+Series|TV\s+Movie|TV\s+Special|'
        r'Video\s+Game|Video|Podcast\s+Series|Movie)\b',
        re.IGNORECASE
    )

    for info in information:
        s = info.text(strip=True)

        # Year
        if s.isdigit():
            y = int(s)
            if 1900 <= y <= 2050:
                result["release_year"] = str(y)

        # Year or Year range
        match = re.match(r'^(\d{4})(?:\s*[-_–]\s*(\d{0,4}))?$', s)
        if match:
            start = int(match.group(1))
            end = match.group(2)

            if end and end.isdigit():
                end = int(end)
                if 1900 <= start <= end <= 2050:
                    result["release_year"] = f"{start}-{end}"
            else:
                if 1900 <= start <= 2050:
                    result["release_year"] = str(start)

        # Episodes
        match = re.search(r'(\d+)\s*(eps?|episodes?)', s, re.IGNORECASE)
        if match:
            result["episodes_count"] = match.group(1)

        # Rating
        ratings = _PAT.findall(s)
        if ratings:
            result["age_rating"] = ratings[0]

        # Title type
        match = FORMAT_PAT.search(s)
        if match:
            result["title_type"] = match.group(0)

    return result



class Movies:
    @staticmethod
    def move(title, category, with_rank=False, parse_movie=False, parse_tv=False):
        loader = ItemLoader(item=ImdbItem(), selector=title)

        # category
        loader.add_value('category', category)

        # rank
        if with_rank:
            rank_el = title.css_first('div[class*="meter-const-ranking"][class*="meter-title-header"]')
            loader.add_value('rank', rank_el.text() if rank_el else '')

        # name
        name_el = title.css_first('h3[class*="title__text"][class*="title__text--reduced"]')
        loader.add_value('original_title', name_el.text() if name_el else '')

        # parser movie
        if parse_movie:
            try:
                informations = title.css('span[class*="title-metadata"]')
                info = info_move(informations)
                loader.add_value('release_year', info.get("release_year", ""))
                loader.add_value('runtime', info.get("runtime", ""))
                loader.add_value('age_rating', info.get("age_rating", ""))
            except Exception as e:
                logging.error(f'parser move: {e}')

        # parser TV
        if parse_tv:
            try:
                informations = title.css('span[class*="title-metadata"]')
                info = info_TV(informations)
                loader.add_value('release_year', info.get("release_year", ""))
                loader.add_value('episodes_count', info.get("episodes_count", ""))
                loader.add_value('age_rating', info.get("age_rating", ""))
                loader.add_value('title_type', info.get("title_type", ""))
            except Exception as e:
                logging.error(f'parser tv: {e}')

        # rating stars
        rating_stars = title.css_first('span[class*="rating-star--rating"]')
        loader.add_value('rating_stars', rating_stars.text() if rating_stars else '')

        # votecount
        votecount = title.css_first('span[class*="rating-star--voteCount"]')
        loader.add_value('votecount', votecount.text() if votecount else '')

        return loader.load_item()


class MoveSpider(scrapy.Spider):
    name = "move"
    allowed_domains = ["www.imdb.com"]

    def start_requests(self):
        urls = {
            'top_250_movies': 'https://www.imdb.com/chart/top/?ref_=hm_nv_menu',
            'most_popular_movies': 'https://www.imdb.com/chart/moviemeter/?ref_=chttp_nv_menu',
            'top_250_tv': 'https://www.imdb.com/chart/toptv/?ref_=chtmvm_nv_menu',
            'most_popular_tv': 'https://www.imdb.com/chart/tvmeter/?ref_=chttvtp_nv_menu'
        }
        for name, url in urls.items():
            yield scrapy.Request(
                url=url,
                meta=dict(
                    playwright=True,
                    name=name,
                    playwright_context = 'default',
                    playwright_page_methods=[
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod('evaluate', scroll_js)]
                ),
                callback=self.parse,
                errback=self.errback_handler
            )

    def errback_handler(self, failure):
        request = failure.request
        name = request.meta.get("name")

        self.logger.error(f"FAILED URL: {request.url} | NAME: {name}")
        self.logger.error(repr(failure))

        if not request.meta.get("retried", False):
            new_request = request.copy()
            new_request.meta["retried"] = True
            yield new_request


    def parse(self, res):
        self.logger.info(f"PAGE URL: {res.url} | NAME: {res.meta.get('name')}")
        nodes = LexborHTMLParser(res.text)
        name = res.meta.get('name', '').lower()
        titles = nodes.css('li[class*="metadata-list-summary-item"]')
        category = name

        if 'movies' in name:
            if 'top' in name:
                for title in titles:
                    try:
                        yield Movies.move(title, category, with_rank=False, parse_movie=True)
                    except Exception as e:
                        logging.error(f'title parse failed:{e}')
            elif 'popular' in name:
                for title in titles:
                    try:
                        yield Movies.move(title, category, with_rank=True, parse_movie=True)
                    except Exception as e:
                        logging.error(f'title parse failed:{e}')

        elif 'tv' in name:
            if 'top' in name:
                for title in titles:
                    try:
                        yield Movies.move(title, category, with_rank=False, parse_tv=True)
                    except Exception as e:
                        logging.error(f'title parse failed:{e}')
            elif 'popular' in name:
                for title in titles:
                    try:
                        yield Movies.move(title, category, with_rank=True, parse_tv=True)
                    except Exception as e:
                        logging.error(f'title parse failed:{e}')


# scrapy crawl move -O SSS.json