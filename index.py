import cv2
import os
import time
import numpy as np
import shutil
import sys
import msvcrt


def get_key_non_blocking():
    """Detect single keypress without blocking"""
    if msvcrt.kbhit():
        return msvcrt.getch().decode('utf-8', errors='ignore').lower()
    return None


def convert_frame_to_ascii(frame, width=80, colored=False):
    """Convert a single video frame to ASCII art"""
    ascii_chars = np.asarray(list(" .:-=+*#%@"))
    height = int(frame.shape[0] * width / frame.shape[1] / 2)
    height = max(1, height)

    frame_resized = cv2.resize(frame, (width, height))
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
    normalized = gray / 255.0
    indices = (normalized * (len(ascii_chars) - 1)).astype(int)

    if colored:
        result = ""
        for y in range(height):
            for x in range(width):
                b, g, r = frame_resized[y, x]
                result += f"\033[38;2;{r};{g};{b}m{ascii_chars[indices[y, x]]}"
            result += "\033[0m\n"
        return result
    else:
        return "\n".join("".join(ascii_chars[row]) for row in indices)


def play_video_in_terminal(video_path, width=None, fps=None, colored=False):
    """Play video as ASCII art in terminal"""
    if not os.path.exists(video_path):
        print(f"🚫 Error: '{video_path}' not found.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("⚠️ Failed to open video.")
        return

    # Auto width if not given
    if width is None:
        width = shutil.get_terminal_size().columns // 2

    # Get FPS from video if not manually set
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / (fps or (video_fps if video_fps > 0 else 24))

    os.system("cls")

    paused = False
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    current_frame = 0

    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("\n🎉 Done! Video playback finished.")
                    break

                ascii_art = convert_frame_to_ascii(frame, width, colored)

                os.system("cls")
                print(ascii_art)
                sys.stdout.flush()

                current_frame += 1

            key = get_key_non_blocking()
            if key == "q":
                print("\n🛑 Quit by user.")
                break
            elif key == " ":
                paused = not paused
                print("[⏸️ Paused]" if paused else "[▶️ Resumed]")

            if not paused:
                time.sleep(frame_delay)
            else:
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user.")

    finally:
        cap.release()
        print("\033[0m")


if __name__ == "__main__":
    video_path = input("🎬 Enter video path: ").strip()
    width_input = input("📏 Width (auto if empty): ").strip()
    fps_input = input("⚡ FPS (auto if empty): ").strip()
    color_input = input("🌈 Enable color? (y/n): ").strip().lower() == "y"

    width = int(width_input) if width_input else None
    fps = int(fps_input) if fps_input else None

    play_video_in_terminal(video_path, width, fps, color_input)
