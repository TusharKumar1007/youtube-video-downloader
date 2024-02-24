import tkinter as tk
from tkinter import filedialog
from pytube import YouTube
from time import sleep
import os
import platform
from moviepy.editor import VideoFileClip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from moviepy.editor import VideoFileClip, AudioFileClip


def combine(video, audio, title):

    video_clip = VideoFileClip(video)
    audio_clip = AudioFileClip(audio)

    video_clip = video_clip.set_audio(audio_clip)

    output_path = os.path.join(os.path.expanduser("~"), f"Downloads\\{title}z.mp4")
    video_clip.write_videofile(output_path, codec="libx264")


# ------------------------------------------------------------------------------------------------------


def open_mp4_file(file_path):
    if platform.system() == "Windows":
        # print(file_path)
        os.startfile(file_path)


# ------------------------------------------------------------------------------------------------------


def delete_files_with_name(downloads_folder, file_prefix):

    files = os.listdir(downloads_folder)

    pattern = re.compile(rf"{re.escape(file_prefix)}\.(mp4|mp3)$", flags=re.IGNORECASE)

    for file in files:

        if pattern.match(file):

            file_path = os.path.join(downloads_folder, file)
            try:

                os.remove(file_path)
                print(f"Deleted file: {file}")
            except Exception as e:
                print(f"Error deleting file: {file}. Reason: {e}")


# ------------------------------------------------------------------------------------------------------


def get_available_resolutions(video_url):
    try:
        yt = YouTube(video_url)
        streams = yt.streams.filter(file_extension="mp4")
        resolutions = []
        for stream in streams:
            resolution = stream.resolution
            if resolution and resolution not in resolutions:
                resolutions.append(resolution)
        return resolutions
    except Exception as e:
        print("Error:", e)
        return []


# ------------------------------------------------------------------------------------------------------


def download_video_with_user_choice_single(video_url, output_path, resolution):
    if resolution in [
        "1080p",
        "720p",
        "480p",
        "360p",
        "240p",
        "144p",
        "1440p",
        "2160p",
    ]:
        download_audio(video_url)

    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension="mp4", resolution=resolution).first()
        if stream:
            print(f"Downloading video in {resolution} resolution...")
            title = stream.title
            title = re.sub(r'[<>:"/\\|?*\']', "", title)

            stream.download(output_path=output_path, filename=f"{title}.mp4")

            path = f"{output_path}{title}.mp4"
            combine(path, f"{output_path}{title}.mp3", title)

            downloads_folder = os.path.expanduser("~\\Downloads")

            delete_files_with_name(downloads_folder, title)

            print("Video downloaded successfully!")
            return title
        else:
            print("No stream found for the selected resolution.")
    except Exception as e:
        print("Error:", e)


# ------------------------------------------------------------------------------------------------------


def fetch_links_from_text_file():
    links = []
    with open("ytlinks.txt", "r+") as f:
        for line in f.readlines():
            links.append(line.rstrip())
    return links


# ------------------------------------------------------------------------------------------------------


def donwload_single():
    video_url = input("Enter Video Url: ")
    output_path = os.path.join(os.path.expanduser("~"), "Downloads\\")
    resolutions = get_available_resolutions(video_url)
    print("\nAvailable resolutions:")
    for i, resolution in enumerate(resolutions):
        print(f"{i + 1}. {resolution}")
    choice = int(input("Enter the number corresponding to the desired resolution: "))
    selected_resolution = resolutions[choice - 1]
    yt_title = download_video_with_user_choice_single(
        video_url, output_path, selected_resolution
    )

    video_file_path = os.path.join(output_path, f"{yt_title}z.mp4")

    open_video = input(
        "Do you want to Play video now press 1 to play or any other key to leave: "
    )

    if open_video == "1":
        try:
            open_mp4_file(video_file_path)
        except:
            print("There is an error opening the file... Try opening manually")


# ------------------------------------------------------------------------------------------------------


def download_video_with_user_choice_batch(video_url, output_path, default_res):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(progressive=True, resolution=default_res).first()
        title = stream.title
        print(f"\nDownloading..... {title}")
        stream.download(output_path)
        print("Download completed successfully!\n")
        with open("temp_links.txt", "a+") as f:
            f.write(f"{title} --> {video_url}\n")
        return stream.title
    except Exception as e:
        print(f"Error: {e}")


# ------------------------------------------------------------------------------------------------------


def download_batch(yt_link_list, default_res="720p"):
    if len(yt_link_list) == 0:
        return "\n\t**** No Url added. Add Url first Use option 4 ****\n"
    resolution = input(
        "Enter resolution 360 or 720 type (no) to download at the highest Quality available:  "
    )
    if resolution not in ["no", "No", "NO"]:
        default_res = resolution + "p"
    print(
        f"\n\t\t**** Number of Videos at {default_res} to be Downloaded: {len(yt_link_list)} ****"
    )
    for index, link in enumerate(yt_link_list):
        video_url = f"{link}"
        print(f"Downloading {index+1}/{len(yt_link_list)}")
        output_path = os.path.join(os.path.expanduser("~"), "Downloads\\")
        download_video_with_user_choice_batch(video_url, output_path, default_res)


# ------------------------------------------------------------------------------------------------------


def save_links_to_text_file():
    print("\n\t\t*****You can type (Q) to quit adding*****")
    getLink = ""
    while getLink not in ["Q", "q"]:
        getLink = input("Enter the Youtube video link: ")
        if getLink not in ["q", "Q"]:
            with open("ytlinks.txt", "a+") as f:
                f.write(getLink + "\n")


# ------------------------------------------------------------------------------------------------------


def clear_file():
    with open("ytlinks.txt", "w") as f:
        f.write("")


# ------------------------------------------------------------------------------------------------------


def file_gui_selection():
    root = tk.Tk()
    root.title("File Selection")
    file_path = None

    def open_file_dialog():
        nonlocal file_path
        file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        print("Selected file:", file_path)
        file_path = file_path.replace("/", "\\")
        root.destroy()

    button = tk.Button(root, text="Select File", command=open_file_dialog)
    button.pack(pady=20)
    root.mainloop()
    return file_path


# ------------------------------------------------------------------------------------------------------


def mp4_to_mp3(file_path):
    try:
        if file_path is None:
            print("\n***** No file selected *****")
            return
        output_dir = os.path.expanduser("~\\Downloads")
        output_filename = input("Enter name for audio file: ") + ".mp3"
        output_path = os.path.join(output_dir, output_filename)
        if os.path.exists(output_path):
            print("File already exists. Please choose a different name.")
            return
        video_clip = VideoFileClip(file_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_path)
        audio_clip.close()
        video_clip.close()
        print("Conversion completed successfully!")
    except Exception as e:
        print(f"Error: {e}")


# ------------------------------------------------------------------------------------------------------


def download_playlist():
    chrome_options = Options()

    chrome_options.add_argument("--headless")

    option_list = ["Audio", "Video"]

    for i, x in enumerate(option_list):
        print(f"\t\t{i+1} --> {x} ")

    user_input = input("Enter your choice: ")
    if user_input not in ["1", "2"]:
        return print("\t\t**** Invalid choice ****\n")

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    user_link = input("Enter the URL: ")
    driver.get(user_link)

    video_link_list = driver.find_elements(By.ID, "video-title")

    link_list = []
    for video in video_link_list:
        # print(video.get_attribute("href"))
        link_list.append(video.get_attribute("href"))
    if user_input == "1":
        for url in link_list:
            download_audio(url)
    if user_input == "2":
        download_batch(link_list)

    driver.quit()


# -----------------------------------------------------------------------------------------------------------------


def download_audio(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    yt_title = audio_stream.title

    yt_title = re.sub(r'[<>:"/\\|?*\']', "", yt_title)

    output_path = os.path.join(os.path.expanduser("~"), "Downloads\\")
    print(f"\nDownloading {yt_title} as Audio...\n ")
    audio_stream.download(output_path=output_path, filename=f"{yt_title}.mp3")
    print("**** Audio Download Complete ****\n")


# -----------------------------------------------------------------------------------------------------------------


def main():
    while True:
        print("\n**** You can press Q to quit any time ****\n")

        list_options = [
            "Download only single Video",
            "Download Multiple Videos",
            "Download YouTube Playlist",
            "Download Only audio",
            "Add links to file",
            "Clear Youtube link File data",
            "Convert video(MP4) to Audio(MP3)",
        ]

        for index, choise in enumerate(list_options):
            print(f"{index+1} --> {choise}")
        main_ans = input("\nEnter Your choice: ")
        if main_ans.lower() == "q":
            break
        if main_ans not in ["1", "2", "3", "4", "5", "6", "7"]:
            print("Invalid choice. Please try again.")
            continue

        if main_ans == "1":
            try:
                donwload_single()
            except:
                print(f"\n\t\t**** Invalid Url ****")

        elif main_ans == "2":
            os.system("cls" if os.name == "nt" else "clear")
            link_lst = fetch_links_from_text_file()
            print(download_batch(link_lst))

        elif main_ans == "3":
            os.system("cls" if os.name == "nt" else "clear")
            print("\n\t\t**** Make Sure The playlist Is Public ****")
            try:
                download_playlist()
            except:
                print("\n**** Check your Internet connection and try again ****\n")

        elif main_ans == "4":
            video_url = input("Enter the YouTube video URL: ")
            try:
                download_audio(video_url)
            except Exception as e:
                print(e)
        elif main_ans == "5":
            save_links_to_text_file()

        elif main_ans == "6":
            try:
                clear_file()
                print("\n\t\t**** File clear Succesfully ****\n")
            except:
                print("\t\t!!! Try cleaning Manually !!!")

        elif main_ans == "7":
            try:
                file_path = file_gui_selection()
                mp4_to_mp3(file_path)
            except:
                print("\t\t****Cannot find the file specified****\t\t")


# -----------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\t\tQuitting in 5 seconds ....")
        sleep(5)
