import ffmpeg
import os

# se quiser adicionar dinamicamente:
# os.environ['PATH'] += os.pathsep + r"C:\ffmpeg\bin"

input_file  = "videos/video1.mp4"            # ou "videos\\video1.mp4"
output_file = "videos/video1_compressed.mp4"

(
    ffmpeg
    .input(input_file)
    .output(output_file,
            vcodec='libx264',
            video_bitrate='800k',
            acodec='aac',
            audio_bitrate='128k',
            preset='medium',
            movflags='faststart'
    )
    .run(overwrite_output=True)
)
