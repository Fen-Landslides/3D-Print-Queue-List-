### 3D 列印排隊系統

一個基於 **Firebase Firestore** 的簡易 3D 列印排隊 / 叫號系統，支援：

- **即時同步**：多台電腦 / 平板 / 手機同時查看與操作隊列。
- **拖曳排序**：用滑鼠拖曳卡片左側把手即可調整優先順序。
- **進度控管**：支援「等待中」「進行中」「已完成」三種狀態，並記錄開始與完成時間。
- **預估時間 ETA**：可輸入預估列印時間，進行中時會顯示剩餘分鐘數。
- **材料 / 顏色備註**：可記錄材料與顏色需求。
- **管理 PIN**：刪除 / 退回 / 復原需輸入 PIN，避免一般使用者誤操作。
- **CSV 匯出**：可匯出目前隊列與完成紀錄，方便統計與留存。
- **PWA 安裝**：支援安裝為桌面 / 手機 App，並具備離線快取。
- **完成通知**：開啟瀏覽器通知權限後，列印完成時會彈出通知。

---

### 目錄

- **專案結構**
- **功能說明**
- **快速開始**
- **Firebase 設定步驟**
- **部署建議**
- **進階設定**
- **授權**

---

### 專案結構

- `index.html`：主頁面與全部前端邏輯（Tailwind CDN + Firebase JS SDK）。
- `manifest.webmanifest`：PWA 設定（名稱、圖示、主題色等）。
- `sw.js`：Service Worker，用來快取靜態資源，支援離線瀏覽。
- `icon-192.png` / `icon-512.png`：PWA App 圖示。

---

### 功能說明

- **新增列印項目**
  - 輸入描述（件名 / 學號 / 需求）、ETA 分鐘與材料 / 顏色（可選），按「新增」即可寫入 Firestore。
- **等待列（`等待列` 區塊）**
  - 顯示所有 `waiting` 狀態的項目，依照 `order` 欄位排序。
  - 可透過拖曳卡片左側把手重新排序，順序變更會回寫到 Firestore。
  - 每張卡片可操作：
    - `開始`：改為 `serving` 狀態並記錄 `startedAt`。
    - `刪除`：刪除該項目（若設定 PIN，需先輸入）。
- **目前進行中（`目前進行中` 區塊）**
  - 顯示所有 `serving` 狀態的項目。
  - 依 `etaMin` 與 `startedAt` 計算剩餘時間。
  - 每張卡片可操作：
    - `完成`：改為 `done` 並記錄 `finishedAt`，若已開啟通知會彈出提示。
    - `退回等待`：狀態改回 `waiting`（若設定 PIN，需先輸入）。
- **已完成項目**
  - 不顯示在主列表，但可透過「完成紀錄（區間）」匯出 CSV 查看。
  - 卡片操作 `復原到等待` 時會把狀態改回 `waiting`，並清除 `finishedAt`。
- **管理 PIN**
  - 透過「設定 / 移除 PIN」按鈕設定 4–8 位數字 PIN，會儲存在瀏覽器 `localStorage`。
  - 目前只有 **刪除 / 退回等待 / 復原到等待** 三種操作需要輸入 PIN。
  - 「開始下一位」與「開始 / 完成」動作不需要 PIN，以方便操作。
- **完成通知**
  - 按下「開啟完成通知」後，瀏覽器會要求通知權限。
  - 權限允許後，列印項目標記為完成時會以系統通知顯示。
- **CSV 匯出**
  - `匯出 CSV`：將目前集合中的所有文件（不分狀態）匯出。
  - `完成紀錄（區間）`：輸入起訖日期，只匯出在時間區間內完成 (`status == done`) 的項目，並計算實際耗時分鐘數。

---

### 快速開始

> 專案為靜態前端頁面，不需要 Node.js 後端。只要有一個支援 HTTPS 的靜態空間（例如 Firebase Hosting / Vercel / Netlify / GitHub Pages 等）即可。

1. **下載專案**
   - 直接下載本專案壓縮檔解壓縮，或 `git clone` 到本機。
2. **建立 Firebase 專案**
   - 到 Firebase Console 建立新專案，並開啟 **Firestore 資料庫**。
   - 在「構建 → Authentication」中啟用 **匿名登入**。
3. **取得 Web App 設定**
   - 在 Firebase 專案中新增一個 Web App，複製其 `firebaseConfig`。
4. **修改 `index.html` 中的 Firebase 設定**
   - 找到：
     - `const firebaseConfig = { ... }`
   - 將裡面的 `apiKey`、`authDomain`、`projectId` 等欄位改為你專案的設定。
5. **變更隊列 ID（選用）**
   - 檔案上方有：
     - `const QUEUE_ID = 'default';`
   - 若同一個 Firebase 專案要建立多條獨立隊列，可改成不同的字串，例如 `labA`、`labB`，不同頁面使用不同 ID 即可。
6. **本機測試**
   - 建議使用任何簡單的靜態伺服器工具，像是：
     - VSCode / Cursor 的 Live Server 外掛
     - 或在資料夾下用 Python 啟動簡單伺服器：

```bash
python -m http.server 8080
```

   - 然後瀏覽 `http://localhost:8080` 測試。
   - 注意：為了使用通知與某些瀏覽器存取權限，建議使用 **HTTPS** 網站做實際部署。

---

### Firebase 設定與資料結構

- **集合名稱**
  - 程式會使用：
    - `const COLLECTION = "queue_3dprint_" + QUEUE_ID`
  - 例如 `QUEUE_ID = "default"` 則集合名稱為 `queue_3dprint_default`。

- **文件欄位**
  - `text`: 描述文字。
  - `etaMin`: 預估時間（分鐘, 可為 `null`）。
  - `material`: 材料 / 顏色（可為 `null`）。
  - `status`: `"waiting" | "serving" | "done"`。
  - `order`: 排序用整數（時間戳為主）。
  - `createdAt`: 建立時間（serverTimestamp）。
  - `startedAt`: 開始時間（serverTimestamp 或 `null`）。
  - `finishedAt`: 完成時間（serverTimestamp 或 `null`）。

- **建議 Firestore 規則範例（僅供參考，請依實際需求調整）**

```txt
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /queue_3dprint_{queueId}/{docId} {
      allow read: if true;                    // 任何人可讀
      allow write: if request.auth != null;   // 需登入（此專案使用匿名登入）
    }
  }
}
```

> 若要加強權限控管，可以額外比對 `request.auth.uid` 或加入管理者清單等，請依實際場域安全需求自行擴充。

---

### 部署建議

- **Firebase Hosting**
  - 最簡單的部署方式，可以與 Firestore 同一專案管理。
  - 將專案檔案放到 `public` 目錄後執行 `firebase deploy` 即可。
- **Vercel / Netlify / GitHub Pages**
  - 本專案是純靜態檔案，只要把整個資料夾部署上去即可。
  - 確認部署環境支援 HTTPS，以便正常使用通知與匿名登入等功能。

---

### 進階設定

- **多條隊列**
  - 可複製一份 `index.html` 為 `labA.html`、`labB.html`，改寫各自的 `QUEUE_ID`，就能用同一 Firebase 專案管理多條獨立隊列。
- **預設管理 PIN**
  - 預設不會寫死 PIN，而是透過介面設定並存入 `localStorage`。
  - 若需固定 PIN，可以在載入時檢查 `localStorage` 或直接寫死邏輯，但請務必評估安全性。
- **UI 調整**
  - 本專案使用 Tailwind CDN，可直接在 `index.html` 中調整 class 或自行加入自訂樣式。

---

### 授權

若原始專案未附帶授權條款，建議在此補充專案的授權方式（例如 MIT License），以便他人合法使用與修改。你也可以依實際需求標註版權宣告與使用限制。

