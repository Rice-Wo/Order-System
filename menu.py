import csv
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger("menu")


@dataclass
class MenuItem:
    """菜單單一品項資料類別"""
    item_id: str
    name: str
    price: int
    category: str
    taste_tags: List[str]


class Menu:
    """菜單資料管理類別。

    負責讀取預設 CSV 菜單檔案並解析為內部物件，同時提供記憶體內單品查詢與全菜單清單走訪介面。
    """

    CSV_PATH: str = "./data/menu.csv"

    def __init__(self) -> None:
        self._items: Dict[str, MenuItem] = self._load_menu()

    def _load_menu(self) -> Dict[str, MenuItem]:
        """讀取預設 CSV 檔案並解析為 MenuItem 物件字典。

        :return: 以 item_id 為 Key、MenuItem 物件為 Value 的字典
        """
        items: Dict[str, MenuItem] = {}

        try:
            with open(self.CSV_PATH, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for line_num, row in enumerate(reader, start=2):
                    try:
                        tags = [tag.strip() for tag in row["taste_tags"].split("|") if tag.strip()]
                        item = MenuItem(
                            item_id=row["item_id"].strip(),
                            name=row["name"].strip(),
                            price=int(row["price"]),
                            category=row["category"].strip(),
                            taste_tags=tags,
                        )
                        items[item.item_id] = item
                    except (KeyError, ValueError) as e:
                        logger.error(f"解析 CSV 第 {line_num} 行失敗，已跳過該品項: {e}")

        except FileNotFoundError:
            logger.error(f"預設菜單檔案不存在: '{self.CSV_PATH}'")
            raise
        except Exception:
            logger.exception(f"讀取菜單時發生未預期錯誤:")
            raise
        else:
            if not items:
                logger.error(f"菜單檔案 '{self.CSV_PATH}' 未包含任何有效品項。")
                raise RuntimeError(f"菜單初始化失敗：'{self.CSV_PATH}' 無有效品項。")
            logger.info(f"成功載入 {len(items)} 個菜單品項")
            return items


    def get_all_items(self) -> List[MenuItem]:
        """取得目前所有菜單品項清單。

        :return: 包含所有 MenuItem 物件的 List
        """
        return list(self._items.values())

    def search_by_id(self, item_id: str) -> Optional[MenuItem]:
        """根據品項 ID 查詢特定的菜單單品。

        :param item_id: 品項唯一識別碼 (例如: "M001")
        :return: 找到時回傳 MenuItem 物件，若不存在則回傳 None
        """
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
