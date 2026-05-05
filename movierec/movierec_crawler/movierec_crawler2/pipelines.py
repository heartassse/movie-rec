import json
from datetime import datetime
from pathlib import Path


class JsonLinesPipeline:
    """
    将 item 以 JSON Lines 形式写入本地文件，默认输出到 data_raw 目录。
    - DoubanMovieItem -> movies.jsonl
    - DoubanMovieCommentItem -> comments.jsonl
    """

    def open_spider(self, spider):
        out_dir = getattr(spider, "out_dir", "data_raw")
        self.base_dir = Path(out_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.movies_f = (self.base_dir / "movies.jsonl").open("a", encoding="utf-8")
        self.comments_f = (self.base_dir / "comments.jsonl").open("a", encoding="utf-8")

    def close_spider(self, spider):
        self.movies_f.close()
        self.comments_f.close()

    def process_item(self, item, spider):
        # 补充 crawled_at 字段（如果没有的话）
        if "crawled_at" in item and not item.get("crawled_at"):
            item["crawled_at"] = datetime.utcnow().isoformat()

        # 懒导入，避免循环依赖
        from .items import DoubanMovieCommentItem, DoubanMovieItem

        line = json.dumps(dict(item), ensure_ascii=False)

        if isinstance(item, DoubanMovieItem):
            self.movies_f.write(line + "\n")
        elif isinstance(item, DoubanMovieCommentItem):
            self.comments_f.write(line + "\n")
        else:
            # 兜底：未知类型也写入 movies.jsonl，防止数据丢失
            self.movies_f.write(line + "\n")

        return item
