import os
import sys
import platform
from datetime import datetime
import argparse
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip

def main():

    #Arguments
    parser = argparse.ArgumentParser(description = "Make video into GIFS")
    parser.add_argument('-f', '--file', required=True, type=str, help='Enter the .mp4 file location')
    parser.add_argument('-s', '--start', default=0, type=int, help='Enter the start time')
    parser.add_argument('-d', '--duration', default=5, type=int, help='Enter the length of GIF')
    parser.add_argument('-fp', '--fps', default=15, type=int, help='Enter the fps value you want')
    parser.add_argument('-sp','--speedup', default=1.0,type=float, help='Enter the speedup of the clip')
    parser.add_argument('-r', '--resize', default=1.0,type=float, help='Scale the video (e.g., 0.5, 1.0, etc)')
    parser.add_argument('-t', '--text', default='', type=str, help='Enter the tagline text')
    parser.add_argument('-p', '--position', default='center', type=str, help='Text position. Choices: top_left, top_right, bottom_left, bottom_right, center, top, bottom, left, right')
    parser.add_argument('-fo','--font', type=str, default='sans-serif', help='Font name or path to TTF file')
    parser.add_argument('-fs', '--fontsize', default=50, type=int, help='Font size of the text')
    parser.add_argument('-op','--opacity', default = 1.0, type=float, help="Enter the opacity of the text")
    parser.add_argument('-c', '--color', default='white', type=str, help='Color of the text')
    parser.add_argument('--loop', type=int, default=0, help='Number of times to loop GIF (0 = infinite)')
    parser.add_argument('-o', '--output', default='output.gif', type=str, help='Output GIF file name')

    #Parsing the arguments
    args = parser.parse_args()
    fileName = args.file
    start = args.start
    duration = args.duration
    fps = args.fps
    speed = args.speedup
    resize = args.resize
    text = args.text
    font = args.font
    fontSize = args.fontsize
    color = args.color
    opacity = args.opacity
    pos_input = args.position
    loop = args.loop
    output = args.output

    #other stuff
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    position_map = {
        "top_left": ("left","top"),
        "top_right": ("right","top"),
        "bottom_left": ("left","bottom"),
        "bottom_right": ("right","bottom"),
        "center": "center",
        "top": "top",
        "bottom": "bottom",
        "left": "left",
        "right": "right"
    }
    pos = position_map.get(pos_input, "center")

    #checking file
    if not os.path.exists(fileName):
        print(f"Error: File '{fileName}' not found.")
        sys.exit(1)

    #Processing
    try:
        clip = VideoFileClip(fileName)
    except OSError as e:
        print(f"Error reading video: {e}")
        sys.exit(1)

    #Checks
    if start < 0 or start >= clip.duration:
        raise ValueError("Start time out of range")
    if fps <= 0:
        raise ValueError("fps must be a positive value")
    if speed <= 0:
        raise ValueError("Speedup must be a positive value")
    if resize <= 0:
        raise ValueError("Resize must be a positive value")
    if duration <= 0 or start + duration > clip.duration:
        duration = clip.duration - start
    if opacity<0 or opacity>1:
        opacity=1
    if output == 'output.gif':
        output = f"output_{timestamp}.gif"
    clip = clip.subclip(start, start+duration)
    clip = clip.speedx(speed)

    # Estimate frames
    est_frames = duration * fps
    print(f"Estimated frames: {est_frames}")

    threshold = 300

    if est_frames > threshold:
        print("Warning: This GIF may be very large.")
        choice = input("Do you want to continue? (y = continue / n = cancel / e = edit parameters) ").lower()
        
        if choice == "n":
            print("GIF creation cancelled.")
            sys.exit(0)
        
        elif choice == "e":
            # Let user update duration, fps, or resize
            try:
                new_duration = input(f"Enter new duration in seconds (current {duration}): ")
                if new_duration.strip() != "":
                    duration = float(new_duration)
                
                new_fps = input(f"Enter new FPS (current {fps}): ")
                if new_fps.strip() != "":
                    fps = int(new_fps)
                
                new_resize = input(f"Enter resize scale (current {resize}): ")
                if new_resize.strip() != "":
                    resize = float(new_resize)
                
                # Recalculate estimated frames
                est_frames = duration * fps
                print(f"Updated estimated frames: {est_frames}")
            
            except ValueError:
                print("Invalid input. Using previous values.")

    #Resizing
    if resize != 1.0:
        clip = clip.resize(resize)

    ##Details regarding the clip
    print("Video info:")
    print(f" - Duration: {clip.duration:.2f} seconds")
    print(f" - Resolution: {clip.size[0]}x{clip.size[1]}")
    print(f" - FPS: {clip.fps}")

    # if text is not empty
    if text:
        try:
            txt = TextClip(text, font=font, fontsize=fontSize, color=color).set_position(pos).set_duration(duration).set_opacity(opacity)
            clip = CompositeVideoClip([clip,txt])
        except OSError:
            print("\n---------------------------------------------------------")
            print(f"ERROR: Font '{font}' not found.")
            print("Please install the font or specify a different one")
            print("using the -fo argument, e.g., -fo 'Liberation-Sans'")
            print("---------------------------------------------------------")
            sys.exit(1)
    #Saving the creation
    os.makedirs("output", exist_ok = True)
    output_path = os.path.join("output",output)
    clip.write_gif(output_path, fps = fps, loop = loop)
    print(f"The {output} has been created!")

    #Show after creation
    if platform.system() == "Windows":
        os.startfile(output_path)
    elif platform.system() == "Darwin":  # macOS
        os.system(f"open {output_path}")
    else:  # Linux
        os.system(f"xdg-open {output_path}")

if __name__ == '__main__':
    main()
