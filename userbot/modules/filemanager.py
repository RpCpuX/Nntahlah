# Credits to Userge for Remove and Rename

import io
import os
import os.path
import shutil
import time
from datetime import datetime
from os.path import basename, dirname, exists, isdir, isfile, join, relpath, splitext
from shutil import rmtree
from tarfile import TarFile, is_tarfile
from zipfile import BadZipFile, ZipFile, is_zipfile

from natsort import os_sorted
from py7zr import Bad7zFile, SevenZipFile, is_7zfile
from rarfile import BadRarFile, RarFile, is_rarfile

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register
from userbot.utils import humanbytes

MAX_MESSAGE_SIZE_LIMIT = 4095


@register(outgoing=True, pattern=r"^\.ls(?: |$)(.*)")
async def lst(event):
    if event.fwd_from:
        return
    cat = event.pattern_match.group(1)
    path = cat if cat else os.getcwd()
    if not exists(path):
        await event.edit(
            f"There is no such directory or file with the name `{cat}` check again!"
        )
        return
    if isdir(path):
        if cat:
            msg = f"**Folders and Files in `{path}`** :\n\n"
        else:
            msg = "**Folders and Files in Current Directory** :\n\n"
        lists = os.listdir(path)
        files = ""
        folders = ""
        for contents in os_sorted(lists):
            catpath = path + "/" + contents
            if not isdir(catpath):
                size = os.stat(catpath).st_size
                if contents.endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += "🎵 "
                elif contents.endswith(".opus"):
                    files += "🎙 "
                elif contents.endswith(
                    (".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")
                ):
                    files += "🎞 "
                elif contents.endswith(
                    (".zip", ".tar", ".tar.gz", ".rar", ".7z", ".xz")
                ):
                    files += "🗜 "
                elif contents.endswith(
                    (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")
                ):
                    files += "🖼 "
                elif contents.endswith((".exe", ".deb")):
                    files += "⚙️ "
                elif contents.endswith((".iso", ".img")):
                    files += "💿 "
                elif contents.endswith((".apk", ".xapk")):
                    files += "📱 "
                elif contents.endswith(".py"):
                    files += "🐍 "
                else:
                    files += "📄 "
                files += f"`{contents}` (__{humanbytes(size)}__)\n"
            else:
                folders += f"📁 `{contents}`\n"
        msg = msg + folders + files if files or folders else msg + "__empty path__"
    else:
        size = os.stat(path).st_size
        msg = "The details of given file :\n\n"
        if path.endswith((".mp3", ".flac", ".wav", ".m4a")):
            mode = "🎵 "
        elif path.endswith(".opus"):
            mode = "🎙 "
        elif path.endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
            mode = "🎞 "
        elif path.endswith((".zip", ".tar", ".tar.gz", ".rar", ".7z", ".xz")):
            mode = "🗜 "
        elif path.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")):
            mode = "🖼 "
        elif path.endswith((".exe", ".deb")):
            mode = "⚙️ "
        elif path.endswith((".iso", ".img")):
            mode = "💿 "
        elif path.endswith((".apk", ".xapk")):
            mode = "📱 "
        elif path.endswith(".py"):
            mode = "🐍 "
        else:
            mode = "📄 "
        time.ctime(os.path.getctime(path))
        time2 = time.ctime(os.path.getmtime(path))
        time3 = time.ctime(os.path.getatime(path))
        msg += f"**Location :** `{path}`\n"
        msg += f"**Icon :** `{mode}`\n"
        msg += f"**Size :** `{humanbytes(size)}`\n"
        msg += f"**Last Modified Time:** `{time2}`\n"
        msg += f"**Last Accessed Time:** `{time3}`"

    if len(msg) > MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "ls.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=path,
            )
            await event.delete()
    else:
        await event.edit(msg)


@register(outgoing=True, pattern=r"^\.rm(?: |$)(.*)")
async def rmove(event):
    """Removing Directory/File"""
    cat = event.pattern_match.group(1)
    if not cat:
        await event.edit("`Missing file path!`")
        return
    if not exists(cat):
        await event.edit("`File path not exists!`")
        return
    if isfile(cat):
        os.remove(cat)
    else:
        rmtree(cat)
    await event.edit(f"Removed `{cat}`")


@register(outgoing=True, pattern=r"^\.rn ([^|]+)\|([^|]+)")
async def rname(event):
    """Renaming Directory/File"""
    cat = str(event.pattern_match.group(1)).strip()
    new_name = str(event.pattern_match.group(2)).strip()
    if not exists(cat):
        await event.edit(f"file path : {cat} not exists!")
        return
    new_path = join(dirname(cat), new_name)
    shutil.move(cat, new_path)
    await event.edit(f"Renamed `{cat}` to `{new_path}`")


@register(outgoing=True, pattern=r"^\.zip (.*)")
async def zip_file(event):
    if event.fwd_from:
        return
    if not exists(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    input_str = event.pattern_match.group(1)
    path = input_str
    zip_name = ""
    if "|" in input_str:
        path, zip_name = path.split("|")
        path = path.strip()
        zip_name = zip_name.strip()
    if exists(path):
        await event.edit("`Zipping...`")
        start_time = datetime.now()
        if isdir(path):
            dir_path = path.split("/")[-1]
            if path.endswith("/"):
                dir_path = path.split("/")[-2]
            zip_path = join(TEMP_DOWNLOAD_DIRECTORY, dir_path) + ".zip"
            if zip_name:
                zip_path = join(TEMP_DOWNLOAD_DIRECTORY, zip_name)
                if not zip_name.endswith(".zip"):
                    zip_path += ".zip"
            with ZipFile(zip_path, "w") as zip_obj:
                for roots, _, files in os.walk(path):
                    for file in files:
                        files_path = join(roots, file)
                        arc_path = join(dir_path, relpath(files_path, path))
                        zip_obj.write(files_path, arc_path)
            end_time = (datetime.now() - start_time).seconds
            await event.edit(
                f"Zipped `{path}` into `{zip_path}` in `{end_time}` seconds."
            )
        elif isfile(path):
            file_name = basename(path)
            zip_path = join(TEMP_DOWNLOAD_DIRECTORY, file_name) + ".zip"
            if zip_name:
                zip_path = join(TEMP_DOWNLOAD_DIRECTORY, zip_name)
                if not zip_name.endswith(".zip"):
                    zip_path += ".zip"
            with ZipFile(zip_path, "w", ZIP_DEFLATED) as zip_obj:
                zip_obj.write(path, file_name)
            await event.edit(f"Zipped `{path}` into `{zip_path}`")
    else:
        await event.edit("`404: Not Found`")


@register(outgoing=True, pattern=r"^\.unzip (.*)")
async def unzip_file(event):
    if event.fwd_from:
        return
    if not exists(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    input_str = event.pattern_match.group(1)
    output_path = TEMP_DOWNLOAD_DIRECTORY + basename(splitext(input_str)[0])
    if exists(input_str):
        start_time = datetime.now()
        await event.edit("`Unzipping...`")
        if is_zipfile(input_str):
            zip_type = ZipFile
        elif is_rarfile(input_str):
            zip_type = RarFile
        elif is_tarfile(input_str):
            zip_type = TarFile
        elif is_7zfile(input_str):
            zip_type = SevenZipFile
        else:
            return await event.edit(
                "`Unsupported file types!`\n`ZIP, TAR, 7z, and RAR only`"
            )
        try:
            with zip_type(input_str, "r") as zip_obj:
                zip_obj.extractall(output_path)
        except BadRarFile:
            return await event.edit("**Error:** `Corrupted RAR File`")
        except BadZipFile:
            return await event.edit("**Error:** `Corrupted ZIP File`")
        except Bad7zFile:
            return await event.edit("**Error:** `Corrupted 7z File`")
        except BaseException as err:
            return await event.edit(f"**Error:** `{err}`")
        end_time = (datetime.now() - start_time).seconds
        await event.edit(
            f"Unzipped `{input_str}` into `{output_path}` in `{end_time}` seconds."
        )
    else:
        await event.edit("`404: Not Found`")


CMD_HELP.update(
    {
        "file": ">`.ls` <directory>"
        "\nUsage: Get list file inside directory."
        "\n\n>`.rm` <directory/file>"
        "\nUsage: Remove file or directory"
        "\n\n>`.rn` <directory/file> | <new name>"
        "\nUsage: Rename file or directory"
        "\n\n>`.zip` <file/folder path> | <zip name> (optional)"
        "\nUsage: For zipping file or folder."
        "\n\n>`.unzip` <path to zip file>"
        "\nUsage: For extracting archive file"
        "\nOnly support ZIP, TAR, 7z, and RAR file!"
    }
)
