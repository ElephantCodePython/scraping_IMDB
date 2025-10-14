import re, scrapy
from itemloaders.processors import TakeFirst, MapCompose

def strip_text(value):
    if value:
        return value.strip()
    return value


def clean_rank(value):
    value = strip_text(value)
    match_rank = re.match(r'^(\d+)', value)
    return match_rank.group(1) if match_rank else ''

def remove_parentheses(value):
    value = strip_text(value)
    return value.strip('()') if value else value

def remove_number_prefix(value):
    value = strip_text(value)
    pattern = r'^\d+\.\s*(.*)$'
    return re.sub(pattern, r'\1', value)

class ImdbItem(scrapy.Item):
    category = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=TakeFirst()
    )
    rank = scrapy.Field(
        input_processor=MapCompose(clean_rank),
        output_processor=TakeFirst()
    )
    original_title = scrapy.Field(
        input_processor=MapCompose(remove_number_prefix),
        output_processor=TakeFirst()
    )
    release_year = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=TakeFirst()
    )
    runtime = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=TakeFirst()
    )
    age_rating = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=TakeFirst()
    )
    episodes_count = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=TakeFirst()
    )
    title_type = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=TakeFirst()
    )
    rating_stars = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=TakeFirst()
    )
    votecount = scrapy.Field(
        input_processor=MapCompose(remove_parentheses),
        output_processor=TakeFirst()
    )
