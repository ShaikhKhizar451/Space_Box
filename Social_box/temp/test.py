from moviepy.editor import VideoFileClip
clip = VideoFileClip('video1.mkv')
clip.save_frame(r"thumbnail.jpg", t=1.00)
