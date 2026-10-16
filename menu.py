import csv
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger("menu")


@dataclass
class MenuItem:
    item_id: str
    name: str
    price: int
    category: str
    taste_tags: List[str]


class Menu:
    """
    菜單
    """

    DEFAULT_CSV_PATH: str = "./data/menu.csv"

    def __init__(self) -> None:
        self._items: Dict[str, MenuItem] = {}
        self.load_menu(self.DEFAULT_CSV_PATH)

    def load_menu(self, csv_path: str) -> Dict[str, MenuItem]:
        """讀取 CSV 檔並載入至 MenuItem 物件字典中"""
        self._items.clear()
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 解析 taste_tags，以 '|' 做切分
                tags = [tag.strip() for tag in row["taste_tags"].split("|") if tag.strip()]

                item = MenuItem(
                    item_id=row["item_id"].strip(),
                    name=row["name"].strip(),
                    price=int(row["price"]),
                    category=row["category"].strip(),
                    taste_tags=tags
                )
                self._items[item.item_id] = item

        return self._items

    def get_all_items(self) -> List[MenuItem]:
        """取得所有菜單品項"""
        return list(self._items.values())

    def search_by_id(self, item_id: str) -> Optional[MenuItem]:
        """依據 item_id 查詢單品項，若不存在回傳 None"""
        return self._items.get(item_id)

if __name__ == "__main__":  # test
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("測試menu中")

    menu = Menu()
    A = menu.get_all_items()
    print(A)
