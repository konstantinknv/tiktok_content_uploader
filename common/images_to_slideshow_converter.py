from moviepy import ImageClip, concatenate_videoclips


def create_slideshow(
    image_files: list,
    output_file: str,
    duration_per_image: int = 5,
    fps: int = 24
) -> str:
    if not image_files:
        raise ValueError("No images provided.")

    clips = []
    for path in image_files:
        clip = ImageClip(path, duration=duration_per_image)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    video.write_videofile(output_file, fps=fps, codec="libx264", audio=False, ffmpeg_params=["-pix_fmt", "yuv420p"])
    return output_file
