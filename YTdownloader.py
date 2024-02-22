import tkinter as tk
from tkinter import filedialog
from cv2 import exp
from pytube import YouTube
import os
import platform
from moviepy.editor import VideoFileClip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def open_mp4_file(file_path):
    if platform.system() == "Windows":
        os.startfile(file_path)


# ------------------------------------------------------------------------------------------------------


def get_available_resolutions(video_url):
    yt = YouTube(video_url)
    streams = yt.streams.filter(progressive=True)
    resolutions = set(stream.resolution for stream in streams)
    return sorted(resolutions)


# ------------------------------------------------------------------------------------------------------


def download_video_with_user_choice(video_url, output_path, resolution):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(progressive=True, resolution=resolution).first()
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
    yt_title = download_video_with_user_choice(
        video_url, output_path, selected_resolution
    )
    open_video = input(
        "Do you want to Play video now press 1 to play or any other key to leave: "
    )
    if open_video == "1":
        file_path = (
            os.path.join(os.path.expanduser("~"), "Downloads\\") + f"{yt_title}.mp4"
        )
        try:
            open_mp4_file(file_path)
        except:
            print("There is an error opening the file... Try opening manually")


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
        download_video_with_user_choice(video_url, output_path, default_res)


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

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    user_link = input("Enter the URL: ")
    driver.get(user_link)

    video_link_list = driver.find_elements(By.ID, "video-title")

    link_list = []
    for video in video_link_list:
        # print(video.get_attribute("href"))
        link_list.append(video.get_attribute("href"))
    download_batch(link_list)

    driver.quit()


# -----------------------------------------------------------------------------------------------------------------


def main():
    while True:
        print("\n**** You can press Q to quit any time ****\n")
        list_options = [
            "Download only single Video",
            "Download Multiple Videos",
            "Download YouTube Playlist",
            "Add links to file",
            "Clear Youtube link File data",
            "Convert video(MP4) to Audio(MP3)",
        ]
        for index, choise in enumerate(list_options):
            print(f"{index+1} --> {choise}")
        main_ans = input("\nEnter Your choice: ")
        if main_ans.lower() == "q":
            break
        if main_ans not in ["1", "2", "3", "4", "5", "6"]:
            print("Invalid choice. Please try again.")
            continue
        if main_ans == "1":
            try:
                donwload_single()
            except:
                print("\n\t\t**** Invalid Url ****")
        elif main_ans == "2":
            os.system('cls' if os.name == 'nt' else 'clear')
            link_lst = fetch_links_from_text_file()
            print(download_batch(link_lst))
        elif main_ans == "3":
            os.system('cls' if os.name == 'nt' else 'clear')
            print('\n\t\t**** Make Sure The playlist Is Public ****')
            download_playlist()
        elif main_ans == "4":
            save_links_to_text_file()
        elif main_ans == "5":
            try:
                clear_file()
                print("\n\t\t**** File clear Succesfully ****\n")
            except:
                print("\t\t!!! Try cleaning Manually !!!")
        elif main_ans == "6":
            try:
                file_path = file_gui_selection()
                mp4_to_mp3(file_path)
            except:
                print("\t\t****Cannot find the file specified****\t\t")


if __name__ == "__main__":
    main()
