import os
from mutagen.mp3 import MP3
from pydub import AudioSegment, silence
import pandas as pd
import numpy as np
import signal
import os
import ctypes
import sys
import argparse
from tqdm import tqdm

# Set the console encoding to UTF-8
if os.name == 'nt':
    import msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def rgb_to_ansi(r, g, b):
    """
    Convert RGB values to the closest ANSI color code.
    """
    # Calculate the closest 8-bit color code
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232

    return 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)

# Define the RGB color
rgb_color = (49, 51, 158)

# Convert RGB to ANSI escape code for background
ansi_bg_code = rgb_to_ansi(*rgb_color)
PPT_BG_BLUE = ''

# Define ANSI escape code for white text
WHITE_TEXT = '\033[38;5;15m'

# Define ANSI escape codes for bold and color
BOLD = '\033[1m'
ITALIC = '\033[3m'
RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
GREY = '\033[37m'
PURPLE = '\033[35m'
CYAN = '\033[36m'
ORANGE = '\033[38;5;208m'
PINK = '\033[38;5;201m'
LIGHT_BLUE = '\033[38;5;123m'
# Cool ANSI escape codes
# BLINK is an ANSI escape code for blinking text
# Example usage: print(f"{BLINK}This text will blink{RESET}")
BLINK = '\033[5m'
UNDERLINE = '\033[4m'
REVERSE = '\033[7m'
# PPT_BLUE = f'\033[38;5;{ansi_code}m'

# Define a color mapping
COLOR_MAP = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "default": (49, 51, 158),
}

def signal_handler(signum, frame):
    print(f"\n{YELLOW}Process interrupted by user. Cleaning up...{RESET}")
    sys.exit(0)

def validate_path(path: str) -> bool:
    """
    Validate if the path exists and contains MP3 files.
    
    :param path: Path to check
    :return: True if valid, False otherwise
    """
    if not os.path.exists(path):
        print(f"{RED}Error: Path does not exist: {path}{RESET}")
        return False
        
    has_mp3 = any(f.lower().endswith('.mp3') 
                  for _, _, files in os.walk(path) 
                  for f in files)
    if not has_mp3:
        print(f"{YELLOW}Warning: No MP3 files found in {path}{RESET}")
        return False
        
    return True

def detect_silence(audio_segment, silence_thresh=-40.0, min_silence_len=500):
    """
    Detect silence in an audio file.
    
    :param audio_segment: AudioSegment object.
    :param silence_thresh: Silence threshold in dBFS.
    :param min_silence_len: Minimum length of silence in milliseconds.
    :return: List of silence intervals.
    """
    return silence.detect_silence(audio_segment, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

def analyze_broken_sound(file_path):
    """
    Analyze an MP3 file for broken sound issues.
    
    :param file_path: Path to the MP3 file.
    :return: Dictionary with analysis results.
    """
    result = {
        "Playable": True,
        "Contains Silence": False,
        "Silence Duration (s)": 0,
        "Contains Clipping": False,
        "Clipping Count": 0,
        "Issues": None
    }

    try:
        # Load the audio file
        audio = AudioSegment.from_mp3(file_path)

        # Detect silence
        silence_intervals = detect_silence(audio)
        silence_duration = sum([(end - start) for start, end in silence_intervals]) / 1000  # Convert to seconds
        if silence_duration > 0:
            result["Contains Silence"] = True
            result["Silence Duration (s)"] = silence_duration

        # Detect clipping
        samples = np.array(audio.get_array_of_samples())
        max_amplitude = np.iinfo(samples.dtype).max
        clipping_count = np.sum(samples >= max_amplitude) + np.sum(samples <= -max_amplitude)
        if clipping_count > 0:
            result["Contains Clipping"] = True
            result["Clipping Count"] = clipping_count
            result["Clipping Percentage"] = f"{(clipping_count / len(samples)) * 100:.2f}%"

    except Exception as e:
        result["Playable"] = False
        result["Issues"] = f"Error analyzing file: {str(e)}"

    return result

def examine_music_folder(folder_path, output_excel):
    """
    Examine a folder containing MP3 files for quality, validity, and broken sound.
    Export the results to an Excel sheet.

    :param folder_path: Path to the folder containing MP3 files.
    :param output_excel: Path to save the Excel report.
    """

    # Ensure output directory exists
    output_dir = os.path.dirname(output_excel) or '.'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Check if output file is writable
    try:
        with open(output_excel, 'a') as f:
            pass
    except PermissionError:
        print(f"{RED}Error: No permission to write to {output_excel}{RESET}")
        return
    except IOError as e:
        print(f"{RED}Error: Cannot write to {output_excel}: {e}{RESET}")
        return
    
    report_data = []

    # Supported file extension
    valid_extension = ".mp3"

    # First, count total MP3 files
    total_files = sum(1 for root, _, files in os.walk(folder_path) 
                     for file in files if file.lower().endswith(valid_extension))
    print(f"{YELLOW}{BOLD}Total MP3 files: {total_files}{RESET}")

    # Walk through the folder
    with tqdm(total=total_files, desc="Processing files", unit="file") as pbar:
        for root, _, files in os.walk(folder_path):
            for file in files:
                # print(f"< Processing {file} ...")
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[-1].lower()
                
                if file_ext == valid_extension:
                    pbar.set_description(f"Processing {file[:40]}...")
                    try:
                        # Check file metadata
                        audio_info = MP3(file_path)
                        bitrate = audio_info.info.bitrate // 1000  # Convert to kbps
                        duration = audio_info.info.length  # Duration in seconds
                        sampling_rate = audio_info.info.sample_rate
                        channels = audio_info.info.channels
                        
                        # Analyze for broken sound
                        broken_sound_results = analyze_broken_sound(file_path)

                        # Add file data to the report
                        report_data.append({
                            "File Name": file,
                            "File Path": file_path,
                            "Bitrate (kbps)": bitrate,
                            "Sampling Rate (Hz)": sampling_rate,
                            "Channels": channels,
                            "Duration (s)": round(duration, 2),
                            "Playable": broken_sound_results["Playable"],
                            # "Contains Silence": broken_sound_results["Contains Silence"],
                            # "Silence Duration (s)": broken_sound_results["Silence Duration (s)"],
                            "Contains Clipping": broken_sound_results["Contains Clipping"],
                            "Clipping Count": broken_sound_results["Clipping Count"],
                            "Issues": broken_sound_results["Issues"]
                        })

                    except Exception as e:
                        # Handle metadata errors
                        report_data.append({
                            "File Name": file,
                            "File Path": file_path,
                            "Bitrate (kbps)": None,
                            "Sampling Rate (Hz)": None,
                            "Channels": None,
                            "Duration (s)": None,
                            "Playable": False,
                            "Contains Silence": False,
                            "Silence Duration (s)": 0,
                            "Contains Clipping": False,
                            "Clipping Count": 0,
                            "Issues": f"Error loading file: {str(e)}"
                        })
                # print(f"> Done {file} ...")
                pbar.update(1)

    # Convert to DataFrame and export to Excel
    report_df = pd.DataFrame(report_data)
    report_df = report_df.sort_values(by=["Playable", "Clipping Count"], ascending=False)
    report_df.to_excel(output_excel, index=False, engine="openpyxl")
    print(f"> Report saved to: {output_excel}")

    # Add summary statistics
    total_files = len(report_data)
    playable_files = sum(1 for item in report_data if item["Playable"])
    files_with_clipping = sum(1 for item in report_data if item["Contains Clipping"])
    
    print(f"\n{BOLD}Summary Report:{RESET}")
    print(f"{BLUE}Total files processed: {total_files}{RESET}")
    print(f"{GREEN}Playable files: {playable_files}{RESET}")
    print(f"{YELLOW}Files with clipping: {files_with_clipping}{RESET}")
    if total_files - playable_files > 0:
        print(f"{RED}Unplayable files: {total_files - playable_files}{RESET}")

# # Example usage
# folder_to_check = r"\\192.168.100.17\\資訊團隊\\08.資料備份區\\GOLDDADDY移機前備份20241217\\html\\poetry\\files\\01"
# output_report = "report.xlsx"
# examine_music_folder(folder_to_check, output_report)

# Enable virtual terminal processing on Windows
def enable_virtual_terminal_processing():
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kernel32.SetConsoleMode(handle, mode)

VERSION = "1.0.0"

if __name__ == "__main__":
    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Call the function to enable virtual terminal processing
    if os.name == 'nt':
        enable_virtual_terminal_processing()

    # Welcome page with ASCII art
    print(f"{YELLOW}{REVERSE}Welcome to the Music Validity Checker!{RESET}\n")
    
    print(f"{ORANGE}範例: 複製下面的命令並貼上到命令提示字元。{RESET}")
    print(f"{ORANGE}{BOLD}check_music_validity.exe --input input_directory --output report.xlsx{RESET}\n")

    parser = argparse.ArgumentParser(
        description=(
            f'Music Validity Checker v{VERSION}\n\n'
            '************\n'
            'Maintainer: Astra <astralee95@gmail.com>\n'
            '************\n\n'
            '功能說明:\n'
            '- 檢查 MP3 檔案是否可播放\n'
            '- 檢測音訊品質問題\n'
            '- 產生詳細的 Excel 報告\n\n'
            '範例:\n'
            'check_music_validity.exe --input input_directory/ --output report.xlsx'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input',  type=str, default="test/", help='Path to the input directory (輸入資料夾)')
    parser.add_argument('--output', type=str, default="report.xlsx", help='Path to the output report excel file (預設輸出 report.xlsx 檔名)')

    args = parser.parse_args()

    # Print the input arguments to the console
    print(f"{GREY}*********************")
    print(f"Input directory     : {ITALIC}{args.input:<12}{RESET} (必須提供資料夾路徑)")
    print(f"Output file         : {ITALIC}{args.output:<12}{RESET} (如果沒有提供, 則使用 report.xlsx 為檔名)")
    print(f"*********************{RESET}")

    if not args.output:
        args.output = "report.xlsx"
        print(f"Output file     : {ITALIC}report.xlsx{RESET} (如果沒有提供, 則使用 report.xlsx 為檔名)")
    else:
        print(f"Output file     : {ITALIC}{args.output:<12}{RESET} (如果沒有提供, 則使用 report.xlsx 為檔名)")
    print("")

    if not validate_path(args.input):
        print(f"{RED}{BOLD}錯誤: 輸入資料夾不存在 '{args.input}'。{RESET}")
    else:
        print(f"{YELLOW}{BOLD}正在生成測試音檔中...{RESET}\n")
        examine_music_folder(args.input, args.output)
        print(f"{YELLOW}{BOLD}\n音檔測試完成。請至 {args.output} 查看報告。{RESET}")
