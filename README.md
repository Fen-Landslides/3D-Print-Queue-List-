### 3D Printing Queuing System ###

It is just an simple 3D printing wueuing system based on **Firebase Firestore**, it features：

- **Always-Update Sycronization**：You can check the queue in all of your device.
- **Sorted by Warp**：You can sort the queue anytime by warping the cards up and down.
- **Progress Control**：There are three status for each card: "Waiting", "On-going", "Done". The starting and ending time will be logged.
- **Estimated Time ETA**：Input the estimated time and it shows the remaining.
- **Material / Colour**：Allowed to record the material and colour desired.
- **Lock PIN**：Avoiding mishandling by setting and requiring Pin before making move.
- **CSV export**：Make it easy to chart and save the results by saving the current queue and finished progress.
- **PWA Install**：Having phone/ desktop client, and they cache your setting and progress offline.
- **Notification**：Notice you when a progress done.

---

### Table of content ###

- **The Structure**
- **Features**
- **A Quick Start**
- **How to set the Firebase**
- **Recommended setting**
- **Advanced setting**
- **Authorisation**

---

### The Structure

- `index.html`：The main page and the Front-End logic（Tailwind CDN + Firebase JS SDK).
- `manifest.webmanifest`：PWA Setting（name、icon、theme, etc).
- `sw.js`：Service Worker，it cache the static information and hence allowing offline browsing.
- `icon-192.png` / `icon-512.png`：PWA App Icon.

---

### Features

- **New Item**
  - Input Desciption（name of item / Student ID / Demand）、ETA time, desired material and colour (Optional). Input them to Firestore by pressing "ADD".
- **The Queue（`The Queue` block）**
  - Showing all items in status `waiting`，sorted by `order`.
  - Wrapping the cards to sort the cards，the changes will be write into Firestore.
  - Card's handling：
    - `Start`：Change the status to `serving` and record the `startedAt`.
    - `Delete`：Delete the item, lock pin necessaried.
- **On-Going（`On-Going` block）**
  - Show all item under `serving`,
  - Calculate the remaining time with `etaMin` and `startedAt`。
  - Card's movement：
    - `Done`：Labelled as `done` and record the `finishedAt`，notice the users if allowed.
    - `Wait`：Change the status to `waiting`, lock pin required.
- **Finished**
  - Only be seen in "Finished Item".
  - "Back to wait" change the status to "waiting" and erase the finishedAT.
- **PIN management**
  - "Set/ Remove Pin" set 4-8 bits pin and store the pin to 'localStorage`。
  - Only **"Delete"** / **"Wait"** / **"Back to wait"** require PIN。
  - "Next progress", "Start", "Done" do not require pin.。
- **Notification**
  - After clicking on "Notify when finished"，the browser will require the permission to notify.
  - Notification would pump out when a progress finished and notification allowed.
- **CSV Export**
  - `Export CSV：Export all file ignoring their status.
  - `Finished Record (Period)`：，只匯出在時間區間內完成 (`status == done`) 的項目，並計算實際耗時分鐘數。

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

### Authorisation

若原始專案未附帶授權條款，建議在此補充專案的授權方式（例如 MIT License），以便他人合法使用與修改。你也可以依實際需求標註版權宣告與使用限制。


