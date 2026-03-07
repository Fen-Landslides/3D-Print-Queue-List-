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
- **Recommended Deployment**
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
  - `Finished Record (Period)`：，Import the item which (`status == done`) within a specific time, and calculate the actual time cost by the item.

---

### A Quick Start

This project is a static frontend page, so no Node.js backend is required. A static hosting service that supports HTTPS (such as Firebase Hosting, Vercel, Netlify, or GitHub Pages) is the only thing you need.

1. **Download your project**
   - Download and unzip the project file, or use git clone to copy it to your computer.
2. **Set up your Firebase**
   - Go to the Firebase Console, create a new project, and enable the Firestore Database.
   - Go to "Build → Authentication" and enable **Anonymous Sign-in**.
3. **Get the setting of Web APP**
   - Add a "Web App" to your Firebase project and copy its **firebaseConfig**.
4. **Change the Firebase Settings in index.html**
   - Go and find：
     - `const firebaseConfig = { ... }`
   - Change the content in slot:`apiKey`、`authDomain`、`projectId` into the information of your project.
5. **Change the Queue ID (Optional)**
   - There is a line on the file：
     - `const QUEUE_ID = 'default';`
   - If you want to run many queues in one Firebase project, change this string to something like "labA" or "labB".
6. **Test on local**
   - Grab a simple static server tool to view your project, such as:
     - The Live Server extension for VSCode or Cursor.
     - Run a command in your project folder:

```bash
python -m http.server 8080
```

   - Go to `http://localhost:8080` and start the testing,
   - Please be awared that you will need to make your live with HTTP website in order to use browser notifications and specific permissions.

---

### How to set the Firebase

- **Collection name**
  - The program is likely to use：
    - `const COLLECTION = "queue_3dprint_" + QUEUE_ID`
  - For example, `QUEUE_ID = "default"`, the collection name will become `queue_3dprint_default`。

- **Document Slot**
  - `text`: It is description.
  - `etaMin`: Estimated time（minutes, can be `null`）。
  - `material`: Material / colour（Can be `null`）。
  - `status`: `"waiting" | "serving" | "done"`。
  - `order`: It is a number used for sorting (based on timestamp).
  - `createdAt`: Built time（serverTimestamp）。
  - `startedAt`: Starting time（serverTimestamp or `null`）。
  - `finishedAt`: Finished time（serverTimestamp or `null`）。

- **Recommended Rules (Please change it according to your needs)**

```txt
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /queue_3dprint_{queueId}/{docId} {
      allow read: if true;                    // Open to everyone to read.
      allow write: if request.auth != null;   // Login required (Anonymous sign-in in this place)
    }
  }
}
```

> For better security, you can restrict access more by checking specific User IDs (request.auth.uid) or building a whitelist.

---

### 

- **Firebase Hosting**
  - It is the easiest way，capable of managing Firestore within the same project.
  - Place your files in a public folder and run "firebase deploy".
- **Vercel / Netlify / GitHub Pages**
  - Since this is a pure static project, just upload the folder to these services.
  - Ensure your domain uses HTTPS so that features like notifications and anonymous login working charm.

---

### Advanced setting

- **Multiple queue**
  - You can make a copie of index.html (e.g., labA.html, labB.html) and rewrite their unique QUEUE_ID. This allows you to manage several queues within one project.
- **Default Admin Pin**
  - PIN is not hardcoded，but being set and saved to `localStorage` instead.
  - If you need to make the PIN permanent, you can check 'localStorage' when it loads or just hardcode it, but please think twice before taking actions.
- **UI Adjustment**
  - This project apply Tailwind CDN，direct change in class in `index.html` become an option, or you may add custom model by your own.

---

### Authorisation

If this project does not have a specific license, we recommend adding one (like the MIT License) so others know how they can legally use and modify your code. Feel free to add your own copyright or usage terms here.



