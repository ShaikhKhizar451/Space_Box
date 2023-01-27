import io
import os
import base64
from Social_box.googleDrive import main
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from moviepy.editor import VideoFileClip

serv = main.create_service()

image = ["jpg", "jpeg", "png", "gif"]
video = ["mp4", "WebM", "OGG", "mkv"]

# This function will upload the file to drive from temp storage and return its id
def upload_file(filename, coreFile, content_type):
    if content_type.split("/")[1] in image:
        parent = "17K8h8B0uwHYEG6nkB_dPFTOZWIa_9mNN"
        file_metadata = {"name": filename, "parents": [parent]}
    else:
        clip = VideoFileClip(coreFile)
        clip.save_frame(
            os.path.realpath(os.curdir) + "/Social_box/temp/thumbnail.jpg", t=1.00
        )
        clip.close()
        parent = "160YXqUe4oz2QP_5ZQM4QH-yWEeJYr2Kc"
        with open(
            os.path.realpath(os.curdir) + "/Social_box/temp/thumbnail.jpg", "rb"
        ) as thumb:
            f = thumb.read()
            b = bytes(f)
        file_metadata = {
            "name": filename,
            "parents": [parent],
            "contentHints.thumbnail.image": base64.urlsafe_b64encode(b).decode("utf8"),
            "contentHints.thumbnail.mimeType": "image/jpg",
        }
    try:

        media = MediaFileUpload(coreFile, mimetype=content_type)
        file = (
            serv.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        change_role_of_files(file.get("id"))
    except HttpError as error:
        print(f"An error occured: {error}")
        file = None

    return file.get("id")


# This function will change the role of file to public so that we can see post using the links
def change_role_of_files(fileid):
    try:
        file_id = fileid
        request_body = {"role": "reader", "type": "anyone"}
        response_permission = (
            serv.permissions().create(fileId=file_id, body=request_body).execute()
        )
    except HttpError as error:
        print(f"An error occured: {error}")


#  This function will return all file present in drive
def get_all_files():
    try:
        results = (
            serv.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        if not items:
            print("No files found.")
        print("Files:")
        for item in items:
            print("{0} ({1})".format(item["name"], item["id"]))
        return item
    except HttpError as error:
        print(f"An error occured: {error}")
        return f"An error occurred: {error}"


# This function will return specific file with id present in drive
def get_file_with_id(file_id):
    try:
        results = serv.files().get(fileId=file_id, fields="webContentLink").execute()
        return results
    except HttpError as error:
        print(f"An error occured: {error}")
        return f"An error occurred: {error}"


# This function will return thumbnail of file with its id
def get_file_thumbnail_with_id(file_id):
    try:
        results = serv.files().get(fileId=file_id, fields="thumbnailLink").execute()
        return results
    except HttpError as error:
        print(f"An error occured: {error}")
        return f"An error occurred: {error}"


# This function will delete the file with its id
def delete_file(file_id):
    try:
        file = serv.files().delete(fileId=file_id).execute()
        return "File Deleted successfully"
    except HttpError as error:
        print(f"An error occured: {error}")
        file = None
        return f"An error occurred: {error}"


# This function will update the file metadata using its id (This will not change the ID of file)
def update_file(file_id, coreFile, content_type):
    try:
        media = MediaFileUpload(coreFile, mimetype=content_type)
        serv.files().update(fileId=file_id, media_body=media).execute()
        return "File updated successfully"
    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
        return f"An error occurred: {error}"


# Advance feature
# This function will download the file using its id
def download_file(real_file_id):
    filename = serv.files().get(fileId=real_file_id).execute()["name"]
    request = serv.files().get_media(fileId=real_file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=file, request=request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download progress {int(status.progress() * 100)}.")
    file.seek(0)
    with open(os.path.join("./", filename), "wb") as f:
        f.write(file.read())
        f.close()
