# 📤 TikTok Content Uploader

An asynchronous CLI tool built with Python for automatically uploading video and photo content to platforms like TikTok using Playwright.

---

## 🚀 Features

- Upload videos and photos using a headless browser.
- Modular architecture - easily add new uploaders.
- Structured logging for better traceability.
- Supports proxy settings, storage state, and session persistence.

---

## 🧩 Project Structure

<pre>
📦 tiktok_content_uploader/
├── common/
│   ├── exceptions.py                     # Custom exceptions
│   ├── logging_setup.py                  # Logging configuration
│   ├── module_loader.py                  # Dynamic module loader
│   ├── proxy.py                          # Short scripts related to proxy convertion/parsing
│   └── utils.py                          # Helper functions
├── config/
│   └── mainconfig.py                     # Main configuration
├── storage_states/                       # Folder to store the browser sessions
├── uploaders/
│   ├── base/
│   │   └── base_uploader.py              # Abstract base uploader (Playwright context)
│   └── tiktok_content_uploader/
│       └── content_uploader.py           # TikTok uploader implementation
├── chromium/                             # Folder for chrome to unpack
├── photos/                               # Folder for photos to upload
├── videos/                               # Folder for videos to upload
├── main.py                               # Entry point (CLI)
├── .gitignore
├── requirements.txt
└── README.md
</pre>

---

## ⚙️ Installation

```bash
git clone https://github.com/konstantinknv/tiktok_content_uploader.git
cd tiktok_content_uploader
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🎛 Arguments
| Argument           | Description                            | Example                          |
| ------------------ | -------------------------------------- | -------------------------------- |
| `-r`, `--uploader` | The name of the uploader module to use | `tiktok`                         |
| `method`           | What type of content to upload         | `upload_photo` or `upload_video` |

---

## 📁 Folder Structure for Media

* ```media/videos/``` - place video files here if using ```upload_video```
* ```media/photos/``` - place photo files here if using ```upload_photo```
##### Note: Only files with supported extensions (e.g., .mp4, .jpg) will be collected, based on your config.

---

## 📄 Environment Variables
### 🔐 Example .env file

### TikTok uploader credentials
```
TIKTOK_UPLOADER_AUTH_USERNAME=your_username
TIKTOK_UPLOADER_AUTH_PASSWORD=your_password
```

### Optional: HTTP/HTTPS proxy settings
```
TIKTOK_UPLOADER_HTTP_PROXY=http://your-proxy:port
TIKTOK_UPLOADER_HTTPS_PROXY=https://your-proxy:port
```

---

## 🧪 Usage
You can run the media uploader via the command line using the following syntax:
```bash
python main.py -r <uploader_name> <method>
```

---

## ✅ Example
```bash
python main.py -r tiktok upload_video
```
This will use the tiktok uploader and upload all video files from the configured folder.
