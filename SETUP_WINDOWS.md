# 🪟 Beginner's guide (Windows) — no coding needed

This walks you through it step by step. You only do **Part 1 once**. After
that you just use **Part 2** whenever you want a new tab.

---

## Part 1 — One-time setup

### Step 1: Install Python
1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **Download Python** button.
3. Open the file you downloaded.
4. **VERY IMPORTANT:** at the bottom of the first window, tick the box that
   says **"Add Python to PATH"**. ✅
5. Click **Install Now** and let it finish.

### Step 2: Get this project's files
- If you downloaded this as a ZIP, right-click it and choose **Extract All**.
- Remember the folder where the files ended up (e.g. your Desktop).

### Step 3: Run the setup helper
- In that folder, find **`setup_windows.bat`** and **double-click it**.
- A black window opens and installs everything. The first time this can take
  **several minutes** and downloads a lot — that's normal. Leave it open.
- When it says **"All done!"** you can close it.

> If it says Python wasn't found, you missed the "Add Python to PATH" tick in
> Step 1. Just reinstall Python with that box ticked, then try again.

---

## Part 2 — Make a tab (do this any time)

1. Open the song on **YouTube**.
2. Copy its link (click the address bar at the top, then Ctrl+C).
3. In the project folder, **double-click `make_tab.bat`**.
4. When it asks, **right-click to paste** the link, then press **Enter**.
5. Wait a few minutes. When it's done, your tab opens automatically in Notepad
   and is saved as **`my_bass_tab.txt`** in the folder.

That's it! 🎉

---

## How to read the tab

The four lines are the four strings of a bass. The numbers are which fret to
press; `0` means play the string without pressing anything ("open").

```
G|------------------------0-------|
D|----------------2-0-------3-2-0-|
A|--------------------3-2---------|
E|0-0-3-5-7-5-3-0-----------------|
```

Read it **left to right**, like a sentence. Lower line = thicker string.

---

## If something goes wrong

Don't panic — copy the message from the black window and send it to me. Common
fixes:

| Message mentions... | What it usually means |
| --- | --- |
| `Python was not found` | Reinstall Python and tick **Add Python to PATH**. |
| `ffmpeg` | The audio helper didn't install; re-run `setup_windows.bat`. |
| `yt-dlp failed` | The link was wrong, private, or your internet dropped. |
| `no bass notes detected` | The song's bass was too quiet/unclear to hear. |

> Note: the very first tab you make is slower because the program downloads its
> "ear" (the AI that separates the bass). After that it's quicker.
