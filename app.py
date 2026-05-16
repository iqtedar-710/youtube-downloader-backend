from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import yt_dlp
import os
import requests

app = FastAPI()
# =========================
# CORS FIX
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CREATE DOWNLOADS FOLDER
# =========================

if not os.path.exists("downloads"):
    os.makedirs("downloads")


# =========================
# HOME PAGE
# =========================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>

    <head>

        <title>YouTube Downloader</title>

        <style>

            *{
                margin:0;
                padding:0;
                box-sizing:border-box;
            }

            body{
                font-family: Arial;
                background: #0f0f0f;
                color: white;
                text-align: center;
                padding: 40px 20px;
            }

            h1{
                margin-bottom: 30px;
                font-size: 40px;
            }

            input{
                width: 90%;
                max-width: 700px;
                padding: 15px;
                border-radius: 12px;
                border: none;
                font-size: 16px;
                outline:none;
            }

            button{
                padding: 12px 22px;
                border: none;
                border-radius: 10px;
                margin: 10px;
                cursor: pointer;
                font-size: 16px;
                transition: 0.3s;
                font-weight:bold;
            }

            button:hover{
                transform:scale(1.03);
                opacity:0.9;
            }

            .fetch-btn{
                background: orange;
                color: white;
            }

            .video-btn{
                background: red;
                color: white;
            }

            .audio-btn{
                background: green;
                color: white;
            }

            .thumb-btn{
                background: #2196F3;
                color: white;
            }

            img{
                width: 100%;
                max-width: 600px;
                border-radius: 20px;
                margin-top: 20px;
                box-shadow:0 0 20px rgba(0,0,0,0.5);
            }

            .card{
                margin-top: 30px;
                background:#1b1b1b;
                padding:30px;
                border-radius:20px;
                max-width:800px;
                margin-left:auto;
                margin-right:auto;
            }

            select{
                padding: 12px;
                border-radius: 10px;
                border: none;
                margin-top: 10px;
                margin-bottom: 20px;
                font-size: 16px;
                width:250px;
            }

            .loader{
                margin-top: 20px;
                font-size: 18px;
                color: orange;
            }

            .title{
                margin-top:20px;
                margin-bottom:15px;
            }

            @media(max-width:768px){

                h1{
                    font-size:28px;
                }

                button{
                    width:100%;
                    max-width:300px;
                }

                select{
                    width:100%;
                    max-width:300px;
                }
            }

        </style>

    </head>

    <body>

        <h1>YouTube Downloader</h1>

        <input
            type="text"
            id="url"
            placeholder="Paste YouTube URL"
        >

        <br><br>

        <button
            class="fetch-btn"
            onclick="fetchInfo()"
        >
            Fetch Video Info
        </button>

        <div class="loader" id="loader"></div>

        <div
            class="card"
            id="videoInfo"
            style="display:none"
        ></div>

        <script>

            async function fetchInfo(){

                let url =
                document.getElementById("url").value;

                if(url.trim() === ""){
                    alert("Please paste a YouTube URL");
                    return;
                }

                document.getElementById("loader").innerHTML =
                "Fetching video details...";

                try{

                    let response =
                    await fetch(
                        `/info?url=${encodeURIComponent(url)}`
                    );

                    let data = await response.json();

                    let qualityOptions = "";

                    data.formats.forEach(f => {

                        qualityOptions += `
                            <option value="${f.format_id}">
                                ${f.quality}
                            </option>
                        `;
                    });

                    document.getElementById("videoInfo").style.display = "block";

                    document.getElementById("videoInfo").innerHTML = `

                        <img src="${data.thumbnail}">

                        <h2 class="title">${data.title}</h2>

                        <p>
                            Duration:
                            ${Math.floor(data.duration / 60)}
                            minutes
                            ${data.duration % 60}
                            seconds
                        </p>

                        <br>

                        <p>
                            Select Video Quality
                        </p>

                        <select id="qualitySelect">
                            ${qualityOptions}
                        </select>

                        <br>

                        <p>
                            Select Audio Quality
                        </p>

                        <select id="audioQualitySelect">

                            <option value="64">
                                64 kbps
                            </option>

                            <option value="128">
                                128 kbps
                            </option>

                            <option value="192" selected>
                                192 kbps
                            </option>

                            <option value="256">
                                256 kbps
                            </option>

                            <option value="320">
                                320 kbps
                            </option>

                        </select>

                        <br>

                        <button
                            class="video-btn"
                            onclick="downloadVideo()"
                        >
                            Download Video
                        </button>

                        <button
                            class="audio-btn"
                            onclick="downloadAudio()"
                        >
                            Download Audio
                        </button>

                        <button
                            class="thumb-btn"
                            onclick="downloadThumbnail()"
                        >
                            Download Thumbnail
                        </button>
                    `;

                    document.getElementById("loader").innerHTML = "";

                }catch(error){

                    document.getElementById("loader").innerHTML =
                    "";

                    alert("Failed to fetch video info.");
                }
            }

            function downloadVideo(){

                let url =
                document.getElementById("url").value;

                let quality =
                document.getElementById(
                    "qualitySelect"
                ).value;

                window.location.href =
                `/download?url=${encodeURIComponent(url)}&format_id=${quality}`;
            }

            function downloadAudio(){

                let url =
                document.getElementById("url").value;

                let quality =
                document.getElementById(
                    "audioQualitySelect"
                ).value;

                window.location.href =
                `/audio?url=${encodeURIComponent(url)}&quality=${quality}`;
            }

            function downloadThumbnail(){

                let url =
                document.getElementById("url").value;

                window.location.href =
                `/thumbnail?url=${encodeURIComponent(url)}`;
            }

        </script>

    </body>

    </html>
    """


# =========================
# VIDEO INFO
# =========================

@app.get("/info")
def video_info(url: str):

    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    formats = []

    added_qualities = set()

    for f in info.get("formats", []):

        height = f.get("height")
        format_id = f.get("format_id")

        if not height:
            continue

        quality = f"{height}p"

        if quality in added_qualities:
            continue

        added_qualities.add(quality)

        formats.append({
            "format_id": format_id,
            "quality": quality
        })

    formats.sort(
        key=lambda x: int(
            x["quality"].replace("p", "")
        )
    )

    return {
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "formats": formats,
    }


# =========================
# VIDEO DOWNLOAD
# =========================

@app.get("/download")
def download_video(url: str, format_id: str):

    try:

        ydl_opts = {
            "format": f"{format_id}+bestaudio/best",
            "noplaylist": True,
            "merge_output_format": "mp4",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            # Get final downloaded filename
            file_path = ydl.prepare_filename(info)

            # Search actual downloaded file
            base_name = os.path.splitext(file_path)[0]

            possible_files = [
                base_name + ".mp4",
                base_name + ".mkv",
                base_name + ".webm"
            ]

            final_file = None

            for file in possible_files:

                if os.path.exists(file):
                    final_file = file
                    break

        if not final_file:

            return {
                "error":
                "Downloaded file not found."
            }

        return FileResponse(
            path=final_file,
            filename=os.path.basename(final_file),
            media_type="application/octet-stream"
        )

    except Exception as e:

        return {
            "error":
            str(e)
        }
# =========================
# AUDIO DOWNLOAD
# =========================

@app.get("/audio")
def download_audio(url: str, quality: str = "192"):

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(title)s.%(ext)s",

        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": quality,
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        original_file = ydl.prepare_filename(info)

        file_path = (
            os.path.splitext(original_file)[0]
            + ".mp3"
        )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="audio/mpeg"
    )


# =========================
# THUMBNAIL DOWNLOAD
# =========================

@app.get("/thumbnail")
def download_thumbnail(url: str):

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    thumbnail_url = info.get("thumbnail")

    response = requests.get(thumbnail_url)

    thumbnail_path = "downloads/thumbnail.jpg"

    with open(thumbnail_path, "wb") as file:
        file.write(response.content)

    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg",
        filename="thumbnail.jpg"
    )