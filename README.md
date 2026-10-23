# 🍔 智慧點餐系統（Order System）

使用 Python 與 Streamlit 開發的互動式智慧點餐系統，具備菜單瀏覽、購物車管理、優惠折扣計算與個人化餐點推薦等功能。系統採用模組化設計，將商業邏輯與使用者介面分離，提高程式碼的可維護性與擴充性。
> 💡 **詳細技術文件**：關於核心 API 參數、`MenuItem` 資料結構與詳細執行流程，請參閱 [系統技術規格書 (DOCS.md)](./DOCS.md)。

---

## ✨ 主要功能

* **菜單管理**：讀取 CSV 菜單資料，支援分類與編號查詢。
* **購物車管理**：支援新增/移除品項、數量累加與小計計算。
* **優惠折扣**：支援固定金額折抵、百分比優惠碼及自動套餐折扣判斷。
* **智慧推薦**：根據預算上限、喜好標籤與避開標籤篩選最佳餐點。
* **結帳收據**：產生結構化訂單資料與格式化文字收據。

---

## 📂 專案架構（Project Structure）

```text
Order-System/
├── data/
│   └── menu.csv              # 菜單資料庫 (CSV)
├── main.py                   # 專案進入點
├── ui.py                     # Streamlit 網頁介面與 Session 狀態管理
├── menu.py                   # 菜單讀取與 MenuItem 資料結構
├── cart_module.py            # 購物車邏輯與收據產生
├── discount_module.py        # 優惠碼與套餐折扣計算
├── recommender.py            # 智慧推薦演算法
├── requirements.txt          # 依賴套件清單
└── README.md                 # 專案說明文件
```

### 📋 模組職責說明

| 檔案                 | 職責說明                                            |
|----------------------|-----------------------------------------------------|
| `main.py`            | 初始化菜單並啟動 Streamlit 介面                     |
| `ui.py`              | 呈現點餐介面、購物車 UI 與推薦結果                  |
| `menu.py`            | 解析 `menu.csv` 並轉換為 `MenuItem` 物件            |
| `cart_module.py`     | 處理購物車增刪、金額小計與收據格式化                |
| `discount_module.py` | 驗證優惠碼與自動判斷套餐組合（主食+飲料+副餐+甜點） |
| `recommender.py`     | 依預算及口味標籤進行餐點篩選與排序                  |

---

## 🚀 快速開始（Quick Start）

### 1. 取得專案

```bash
git clone https://github.com/Rice-Wo/Order-System.git
cd Order-System
```

### 2. 建立與啟動虛擬環境（建議）

* **Windows**:
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. 安裝相依套件

```bash
pip install -r requirements.txt
```

*(若未建立 `requirements.txt`，請至少安裝 `pip install streamlit`)*

### 4. 啟動系統

```bash
streamlit run main.py
```

啟動後開啟瀏覽器訪問 `http://localhost:8501` 即可使用。

---

## 🛠️ 技術棧（Tech Stack）

* **Language**: Python 3.10+
* **Frontend / UI**: Streamlit
* **Data Format**: CSV
* **VCS**: Git / GitHub

---

## 👥 小組分工（Team Collaboration）

| 項目           | 負責內容                                  |
|----------------|-------------------------------------------|
| **菜單管理**   | CSV 資料解析、異常處理與                  |
| **購物車管理** | 購物車狀態維護、小計邏輯與收據輸出        |
| **優惠折扣**   | 優惠碼比對、套餐判定演算法與最佳折扣選擇  |
| **智慧推薦**   | 標籤比對、預算過濾與推薦排序              |
| **介面整合**   | Streamlit UI 設計、Session State 狀態同步 |