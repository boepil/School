# Image Review System

This system allows a team to review a folder of tagged images in real-time. It consists of a Python script to compress images and extract XMP/IPTC tags, and a static web interface that syncs approvals/rejections using Firebase Realtime Database.

## 1. Setup Environment

Make sure you have Python installed. Install the necessary packages:
```bash
pip install pyexiv2 Pillow
```

## 2. Process Images

Your original images should be in the `All/` folder.
Run the python script:
```bash
python process_images.py
```
This will:
1. Find all images in `All/`.
2. Extract the person's name from XMP/IPTC tags.
3. Resize images to a max of 1600px and compress them.
4. Save the compressed images to `review/images/` and generate a `review/manifest.json`.

## 3. Firebase Setup

The web application uses Firebase Realtime Database to sync the review state.

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add Project** and follow the steps. You can disable Google Analytics.
3. In the left menu, click **Build > Realtime Database** and click **Create Database**.
4. Choose your location and start in **Test Mode** (or start in Locked mode and update rules later).
5. Go to the **Rules** tab of your Realtime Database and set them to allow read/write for now (for an internal team):
   ```json
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
   ```
6. Click **Project Settings** (gear icon top left).
7. Scroll down to "Your apps" and click the **Web** icon (`</>`).
8. Register the app (e.g., "Image Reviewer").
9. Copy the `firebaseConfig` object and paste it into `review/index.html` inside the `<script type="module">` block. (Note: The provided configuration has already been added to the current `index.html`).

## 4. Local Testing

To test the application locally before deploying:
```bash
cd review
python -m http.server 8000
```
Open `http://localhost:8000` in your browser.

## 5. Deployment to GitHub Pages

1. Initialize a git repository if you haven't already:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
   *(Note: The `.gitignore` prevents your raw images in `/All/` from being uploaded).*
2. Push to a repository on GitHub.
3. In your GitHub repository, go to **Settings > Pages**.
4. Under **Build and deployment**, set Source to **Deploy from a branch**.
5. Select your `main` or `master` branch and select the `/review` folder if it was a subfolder, OR better yet:
   - If you only want to deploy the `review/` folder, you can use the `gh-pages` branch method:
   ```bash
   git subtree push --prefix review origin gh-pages
   ```
   Then set GitHub Pages to serve from the `gh-pages` branch.

Alternatively, you can just host the `review/` folder on any static host like Netlify or Vercel simply by dropping the folder into their dashboard.
