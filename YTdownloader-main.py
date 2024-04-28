import tkinter as tk
from tkinter import filedialog
from pytubefix import YouTube
from pytubefix.exceptions import AgeRestrictedError, ExtractError, VideoUnavailable
from pytubefix.cli import on_progress
from time import sleep
import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from http.client import IncompleteRead
from colorama import init, Fore
import inspect
import sys
import subprocess

init()

retry_count = 0

bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
ffmpeg_path = os.path.abspath(
    os.path.join(bundle_dir, r"C:\ffmpeg_for_python\ffmpeg.exe")
)


def combine(video, audio):
    if "REPLIT_ENVIRONMENT" in os.environ:
        output_path = "./downloads"
    else:
        output_path = os.path.join(os.path.expanduser("~"), "Downloads")

    output_filename = os.path.splitext(os.path.basename(video))[0] + "z.mp4"

    output_path = os.path.join(output_path, output_filename)

    cmd = f'{ffmpeg_path} -i "{video}" -i "{audio}" -c:v copy -c:a aac "{output_path}"'

    subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
    )


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
                # print(f"Deleted file: {file}")
            except Exception as e:
                print(f"{Fore.RED}Error deleting file: {file}. Reason: {e}")


# ------------------------------------------------------------------------------------------------------


def get_available_resolutions(video_url):
    try:
        yt = YouTube(video_url, on_progress_callback=on_progress)
        streams = yt.streams.filter(adaptive=True).filter(mime_type="video/webm")
        resolutions = []
        for stream in streams:
            resolution = stream.resolution
            if resolution and resolution not in resolutions:
                resolutions.append(resolution)
        return resolutions
    except:
        print(f"\n\t\t{Fore.RED}**** Invalid Url ****")


# ------------------------------------------------------------------------------------------------------


def download_video_with_user_choice_single_fast(video_url, resolution):
    global retry_count
    try:
        yt = YouTube(video_url, on_progress_callback=on_progress)
        stream = yt.streams.filter(progressive=True, resolution=resolution).first()
        title = stream.title

        filesize_bytes = stream.filesize
        filesize_mb = filesize_bytes / (1024 * 1024)

        # Determine the output path based on the environment
        output_path = determine_output_path()

        print(f"\n{Fore.MAGENTA}Downloading..... {filesize_mb:.2f} MB {title}")
        title = re.sub(r'[<>:"/\\|?*\']', "", title)
        stream.download(output_path=output_path, filename=f"{title}z.mp4")
        print(f"{Fore.CYAN}Download completed successfully!\n")
        with open("temp_links.txt", "a+") as f:
            f.write(f"{title} --> {video_url}\n")
        return title
    except IncompleteRead:
        retry_count += 1
        if retry_count <= 2:
            print(
                f"\n\t\t{Fore.RED}**** Incomplete Download. Retrying download... ****"
            )
            return download_video_with_user_choice_single_fast(video_url, resolution)
        else:
            return print(
                f"\n\t\t{Fore.RED}Try downloading {title} Url:{video_url} using option 1..."
            )
    except Exception as e:
        # print(f"Error: {e}")
        return title


def determine_output_path():
    # Check if the code is running on Replit
    if "REPLIT_ENVIRONMENT" in os.environ:
        return "./downloads"
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# ------------------------------------------------------------------------------------------------------


def download_video_with_user_choice_single(video_url, resolution):
    global retry_count
    if resolution in [
        "1080p",
        "720p",
        "480p",
        "360p",
        "240p",
        "144p",
        "1440p",
        "2160p",
        "4320p",
    ]:

        try:
            yt = YouTube(video_url, on_progress_callback=on_progress)
            stream = yt.streams.filter(
                adaptive=True, mime_type="video/webm", resolution=resolution
            )
            if stream:
                video = stream.first()
                filesize_bytes = video.filesize
                filesize_mb = filesize_bytes / (1024 * 1024)
                output_path = determine_output_path()
                title = yt.title
                print(
                    f"{Fore.MAGENTA}Downloading {title} in {resolution} resolution {filesize_mb:.2f} MB..."
                )
                title = re.sub(r'[<>:"/\\|?*\']', "", title)

                video.download(output_path=output_path, filename=f"{title}.mp4")

                path = f"{output_path}/{title}.mp4"
                download_audio(video_url)

                # print("hello")
                combine(path, f"{output_path}/{title}.mp3")
                # print("hello")
                delete_files_with_name(output_path, title)

                print(f"{Fore.CYAN}Video downloaded successfully!\n")
                with open("temp_links.txt", "a+") as f:
                    f.write(f"{title} --> {video_url}\n")
                return title, 0
            else:
                print(f"{Fore.RED}No video found for the selected resolution.")
                return "No title", 404
        except IncompleteRead:
            retry_count += 1
            if retry_count <= 3:
                print(
                    f"\n\t\t{Fore.RED}**** Incomplete Donwload. Retrying download... ****"
                )
                return download_video_with_user_choice_single_fast(
                    video_url, output_path, resolution="720p"
                )
            else:
                return print(
                    f"\n\t\t{Fore.RED}Try downloading {title} Url:{video_url} using option 1..."
                )
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            # print("Error: ", e)
            return title, 0
        except Exception as e:
            print("Error:", e)
            return title, 404


# ------------------------------------------------------------------------------------------------------


def fetch_links_from_text_file():
    links = []
    with open("ytlinks.txt", "r+") as f:
        for line in f.readlines():
            links.append(line.rstrip())
    return links


# ------------------------------------------------------------------------------------------------------


def get_available_resolutions_fast(video_url):
    yt = YouTube(video_url, on_progress_callback=on_progress)
    streams = yt.streams.filter(progressive=True)
    resolutions = set(stream.resolution for stream in streams)
    return sorted(resolutions)


# ------------------------------------------------------------------------------------------------------


def donwload_single():
    video_url = input("Enter Video Url: ").strip()
    output_path = os.path.join(os.path.expanduser("~"), "Downloads\\")
    choice_lst = [
        "Blazing Fast download(Limited Resolutions)",
        "Fast Download(More fps and Resolutons)",
    ]

    for i, x in enumerate(choice_lst):
        print(f"\t\t{i+1} --> {x}")

    fast_moreres_choice = input("Enter your choice: ").strip()

    if fast_moreres_choice == "1":
        resolutions = get_available_resolutions_fast(video_url)
    else:
        resolutions = get_available_resolutions(video_url)

    if not resolutions:
        return print(
            f"\n\t\t{Fore.RED}**** This video might be recently uploaded.Try after 24 Hours or Try using option 1--> Blazing fast ****"
        )
    print(f"\n{Fore.YELLOW}Available resolutions:")
    for i, resolution in enumerate(resolutions):
        print(f"{i + 1}. {resolution}")

    try:
        choice = input(
            "Enter the number corresponding to the desired resolution: "
        ).strip()

        if choice.isdigit():
            choice = int(choice)
        else:
            raise Exception

        if choice <= 0:
            raise IndexError
        selected_resolution = resolutions[choice - 1]
    except IndexError:
        return print(f"\n\t\t{Fore.RED}**** Invalid choice ****")
    except Exception:
        return print(f"\n\t\t{Fore.RED}**** Enter correct Information ****")

    if fast_moreres_choice == "1":
        yt_title = download_video_with_user_choice_single_fast(
            video_url, selected_resolution
        )
    else:
        yt_title, return_code = download_video_with_user_choice_single(
            video_url, selected_resolution
        )

    video_file_path = os.path.join(output_path, f"{yt_title}z.mp4")

    open_video = input(
        "Do you want to Play video now press 1 to play or any other key to leave: "
    ).strip()

    if open_video == "1":
        try:
            open_mp4_file(video_file_path)
        except Exception as e:
            print(e)
        except:
            print(
                f"{Fore.RED}There is an error opening the file... Try opening manually"
            )


# ------------------------------------------------------------------------------------------------------


def download_video_with_user_choice_batch(video_url, output_path, default_res):
    try:
        retry_count = 0
        yt = YouTube(video_url, on_progress_callback=on_progress)
        stream = yt.streams.filter(progressive=True, resolution=default_res).first()
        title = stream.title

        filesize_bytes = stream.filesize
        filesize_mb = filesize_bytes / (1024 * 1024)

        print(f"\n{Fore.MAGENTA}Downloading..... {title} ({filesize_mb:.2f} MB)")

        stream.download(output_path)
        print(f"{Fore.CYAN}Download completed successfully!\n")
        with open("temp_links.txt", "a+") as f:
            f.write(f"{title} --> {video_url}\n")
        return stream.title
    except IncompleteRead:
        retry_count += 1
        if retry_count <= 2:
            print(
                f"\n\t\t{Fore.RED}**** Incomplete Donwload. Retrying download... ****"
            )
            return download_video_with_user_choice_single_fast(
                video_url, output_path, default_res
            )
        else:
            return print(
                f"\n\t\t{Fore.RED}Try downloading {title} Url:{video_url} using option 1..."
            )
    except Exception as e:
        # print(f"Error: {e}")
        pass


# ------------------------------------------------------------------------------------------------------


def download_batch(yt_link_list, default_res="720p"):
    if len(yt_link_list) == 0:
        raise Exception
    resolution = input(
        "Enter resolution 360, 480, 720 or 1080 press enter to download at the highest Quality available:  "
    ).strip()

    if resolution in ["360", "480", "720", "1080"]:
        default_res = resolution + "p"

    print(
        f"\n\t\t{Fore.CYAN}**** Number of Videos at {default_res} to be Downloaded: {len(yt_link_list)} ****"
    )
    for index, link in enumerate(yt_link_list):
        video_url = f"{link}"
        print(f"{Fore.CYAN}Downloading {index+1}/{len(yt_link_list)}")
        output_path = os.path.join(os.path.expanduser("~"), "Downloads\\")

        if default_res in ["480p", "1080p"]:
            title, psudo_error_code = download_video_with_user_choice_single(
                link, default_res
            )
            # print(psudo_error_code)
            if psudo_error_code == 404:
                print(f"\n{Fore.YELLOW}Trying to download in 360p\n")
                download_video_with_user_choice_batch(video_url, output_path, "360p")

        else:
            download_video_with_user_choice_batch(video_url, output_path, default_res)


# ------------------------------------------------------------------------------------------------------


def save_links_to_text_file():
    print(f"\n\t\t{Fore.YELLOW}*****You can type (Q) to quit adding*****")
    getLink = ""
    while getLink not in ["Q", "q"]:
        getLink = input("Enter the Youtube video link: ").strip()
        if getLink not in ["q", "Q"]:
            with open("ytlinks.txt", "a+") as f:
                f.write(getLink + "\n")


# ------------------------------------------------------------------------------------------------------


def clear_file():
    choice = input("Are you sure? type yes to confirm: ").lower()
    if choice == "yes":
        with open("ytlinks.txt", "w") as f:
            f.write("")
        return True
    else:
        return False


# ------------------------------------------------------------------------------------------------------


def file_gui_selection():
    root = tk.Tk()
    root.title("File Selection")
    file_path = None
    file_name = None

    def open_file_dialog():
        nonlocal file_path, file_name
        file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        print("Selected file:", file_path)
        file_path = file_path.replace("/", "\\")
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        root.destroy()

    button = tk.Button(root, text="Select File", command=open_file_dialog)
    button.pack(pady=20)
    root.mainloop()
    return file_path, file_name


# ------------------------------------------------------------------------------------------------------


def mp4_to_mp3(file_path, file_name="audio.mp3"):
    if not file_path or not os.path.exists(file_path):
        print(f"\n{Fore.RED}***** Invalid file path *****")
        return

    user_options = [
        "Convert with high speed, same quality as in video",
        "Convert to best quality 320Kbps",
    ]

    print("\nSelect conversion option:")
    for index, choice in enumerate(user_options):
        print(f"\t\t{Fore.CYAN}{index+1} --> {Fore.GREEN}{choice}")

    user_choice = ""
    while user_choice not in ["1", "2"]:
        user_choice = input("Enter your choice (1 or 2), or 'q' to quit: ").strip()
        if user_choice.lower() == "q":
            return

    output_filename = (
        input("Enter name for audio file (or press Enter for auto-detect): ").strip()
        or file_name
    ) + ".mp3"

    try:
        output_dir = os.path.expanduser("~\\Downloads")
        output_path = os.path.join(output_dir, output_filename)

        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            file_path,
            "-vn",
            "-acodec",
            "libmp3lame",
            "-y",
        ]

        if user_choice == "1":
            ffmpeg_cmd += ["-b:a", "128k"]
        else:
            ffmpeg_cmd += ["-b:a", "320k"]

        ffmpeg_cmd.append(output_path)
        if user_choice == "1":
            print(f"\n{Fore.MAGENTA}**** Conversion in progress 128kbps ****\n")
        else:
            print(f"\n{Fore.MAGENTA}**** Conversion in progress 320kbps ****\n")
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"{Fore.CYAN}Conversion completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}An error occurred: {e}")


# ------------------------------------------------------------------------------------------------------


def download_playlist():
    chrome_options = Options()

    chrome_options.add_argument("--headless")

    option_list = ["Audio", "Video"]

    for i, x in enumerate(option_list):
        print(f"\t\t{i+1} --> {x} ")

    user_input = input("Enter your choice: ").strip()
    if user_input not in ["1", "2"]:
        return print(f"\t\t{Fore.RED}**** Invalid choice ****\n")

    if platform.system() == "Windows":
        os.system("webdriver-manager.cmd > NUL 2>&1")
    else:
        os.system("webdriver-manager > /dev/null 2>&1")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=chrome_options
    )
    user_link = input("Enter the URL: ").strip()
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
    yt = YouTube(url, on_progress_callback=on_progress)

    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    yt_title = audio_stream.title

    if "REPLIT_ENVIRONMENT" in os.environ:
        output_path = "./downloads"
    else:

        output_path = os.path.join(os.path.expanduser("~"), "Downloads")
    yt_title = re.sub(r'[<>:"/\\|?*\']', "", yt_title)

    caller = inspect.stack()[1].function

    if caller not in ["download_video_with_user_choice_single"]:
        print(f"\n{Fore.MAGENTA}Downloading {yt_title} as Audio...\n ")
    audio_stream.download(output_path=output_path, filename=f"{yt_title}.mp3")
    if caller not in ["download_video_with_user_choice_single"]:
        print(f"{Fore.CYAN}**** Audio Download Complete ****\n")


# -----------------------------------------------------------------------------------------------------------------


def download_hls_video(hls_url):
    try:

        file_name = input("Enter file name: ")
        if not file_name:
            print("Invalid file name. Please provide a valid file name.")
            return
        file_name = re.sub(r"[^\w\s-]", "_", file_name)

        output_file = os.path.join(
            os.path.expanduser("~"), "Downloads", f"{file_name}.mp4"
        )
        print(f"{Fore.YELLOW}\nDownloading {file_name}...")

        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            hls_url,
            "-c",
            "copy",
            "-y",
            output_file,
        ]

        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"{Fore.CYAN}Downloaded successfully!")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error: {e}")
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}\n\t\t**** Aborting Download ****")


# -----------------------------------------------------------------------------------------------------------------


def main():
    while True:
        print(f"{Fore.LIGHTYELLOW_EX}\n**** You can press Q to quit any time ****\n")

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
            print(f"{Fore.CYAN}{index+1} --> {Fore.GREEN}{choise}")
        main_ans = input("\nEnter Your choice: ").strip()
        if main_ans.lower() == "q":
            break
        if main_ans not in ["1", "2", "3", "4", "5", "6", "7", "#"]:
            print(f"{Fore.RED}Invalid choice. Please try again.")
            continue

        if main_ans == "1":
            try:
                donwload_single()
            except AgeRestrictedError as e:
                print(
                    f"\n\t\t{Fore.RED}**** This video is age-restricted and cannot be downloaded ****"
                )
            except ExtractError as e:
                print(
                    f"\n\t\t{Fore.RED}**** There was an error extracting video data. Please check your network connection ****"
                )
            except VideoUnavailable as e:
                print(
                    f"\n\t\t{Fore.RED}**** This video is not available. It may have been removed or made private ****"
                )
            except Exception as e:
                print(f"\n\t\t{Fore.RED}**** Invalid Url ****{e}")

        elif main_ans == "2":
            try:
                link_lst = fetch_links_from_text_file()
                download_batch(link_lst)

            except:
                print(f"\n\t\t{Fore.YELLOW}**** Please add links using option 5 ****")
                sleep(2)

        elif main_ans == "3":
            os.system("cls" if os.name == "nt" else "clear")
            print(f"\n\t\t{Fore.YELLOW}**** Make Sure The playlist Is Public ****")
            try:
                download_playlist()
            except ExtractError as e:
                print(
                    f"\n\t\t{Fore.RED}**** There was an error extracting video data. Please check your network connection ****"
                )
            except VideoUnavailable as e:
                print(
                    f"\n\t\t{Fore.RED}**** This video is not available. It may have been removed or made private ****"
                )
            except:
                print(
                    f"\n{Fore.RED}**** Check your Internet connection and try again ****\n"
                )

        elif main_ans == "4":
            video_url = input("Enter the YouTube video URL: ").strip()
            try:
                download_audio(video_url)
            except ExtractError as e:
                print(
                    f"\n\t\t{Fore.RED}**** There was an error extracting video data. Please check your network connection ****"
                )
            except VideoUnavailable as e:
                print(
                    f"\n\t\t{Fore.RED}**** This video is not available. It may have been removed or made private ****"
                )
            except Exception as e:
                print(e)
        elif main_ans == "5":
            save_links_to_text_file()

        elif main_ans == "6":
            try:
                res = clear_file()
                if res:
                    print(f"\n\t\t{Fore.CYAN}**** File clear Succesfully ****\n")
                else:
                    print(
                        f"\n\t\t{Fore.YELLOW}**** Aborting clear. File data is preserved ****\n"
                    )
            except:
                print(f"\t\t{Fore.BLUE}!!! Try cleaning Manually !!!")

        elif main_ans == "7":
            try:
                file_path, file_name = file_gui_selection()
                mp4_to_mp3(file_path, file_name)
            except:
                print(f"\t\t{Fore.RED}**** Cannot find the file specified ****\t\t")
        elif main_ans == "#":
            user_input_m3u8 = input("Enter .m3u8 Url: ")
            download_hls_video(user_input_m3u8)


# -----------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n\t\t{Fore.RED}Quitting in 5 seconds ....")
        sleep(5)
