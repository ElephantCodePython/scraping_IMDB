import sqlite3
import os
from itemadapter import ItemAdapter

class ImdbPipeline:
    def open_spider(self, spider):
        db_name = "imdb_new.db"

        if os.path.exists(db_name):
            os.remove(db_name)

        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE media (
                original_title TEXT,
                release_year TEXT,
                category TEXT,
                rank TEXT,
                runtime TEXT,
                age_rating TEXT,
                episodes_count TEXT,
                title_type TEXT,
                rating_stars TEXT,
                votecount TEXT
            )
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.cursor.execute("""
            INSERT OR REPLACE INTO media (
                original_title, release_year, category, rank, runtime,
                age_rating, episodes_count, title_type, rating_stars, votecount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            adapter.get("original_title", ""),
            adapter.get("release_year", ""),
            adapter.get("category", ""),
            adapter.get("rank", ""),
            adapter.get("runtime", ""),
            adapter.get("age_rating", ""),
            adapter.get("episodes_count", ""),
            adapter.get("title_type", ""),
            adapter.get("rating_stars", ""),
            adapter.get("votecount", "")
        ))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.connection.close()
