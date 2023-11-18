import os
import mimetypes
import zipfile
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from pytube import Playlist, YouTube
from .forms import PlaylistForm
from urllib.parse import quote

def download_video(video_url, download_path, resolution='720p'):
    video = YouTube(video_url)
    stream = video.streams.filter(res=resolution, file_extension='mp4').first()

    if stream:
        print(f"Downloading: {video.title}")
        file_path = os.path.join(download_path, f"{slugify(video.title)}.mp4")
        stream.download(download_path)
        return file_path
    else:
        print(f"Error downloading: {video.title}")
        return None

def create_zip(zip_filename, files_to_zip):
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        for file_path in files_to_zip:
            #each file to the zip file
            print(file_path)
            file_name = os.path.basename(file_path)
            zip_file.write(file_path, file_name)

def download_files(request, downloaded_files):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = '/test.zip'
    filepath = base_dir + '/media' + filename
    create_zip(filepath, downloaded_files)

    thefile = filepath
    filepath = os.path.basename(thefile)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(thefile, 'rb'), chunk_size),
                                     content_type=mimetypes.guess_type(thefile)[0])
    response['Content-Length'] = os.path.getsize(thefile)
    response['Content-Disposition'] = "Attachment;filename=%s" % filename
    return response

def download_playlist(playlist_url, download_path='media', resolution='720p'):
    playlist = Playlist(playlist_url)

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    downloaded_files = []

    for video_url in playlist.video_urls:
        file_path = download_video(video_url, download_path, resolution)
        if file_path:
            downloaded_files.append(file_path)

    return downloaded_files

def home(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist_url = form.cleaned_data['playlist_url']
            downloaded_files = download_playlist(playlist_url)
            return download_files(request, downloaded_files)
    else:
        form = PlaylistForm()

    return render(request, 'downloader/home.html', {'form': form})
