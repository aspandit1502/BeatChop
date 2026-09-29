import librosa
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips

def generate_synced_video(video_path, audio_path, output_path):
    print(f"Loading audio from {audio_path}...")
    y, sr = librosa.load(audio_path)
    
    print("Extracting beat timestamps...")
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    if len(beat_times) < 2:
        print("Fatal error: Not enough beats detected. Pick a punchier track.")
        return

    print(f"Loading video from {video_path}...")
    vid = VideoFileClip(video_path)
    aud = AudioFileClip(audio_path)
    
    w, h = vid.size
    target_w = int(h * 9 / 16)
    
    # v2 syntax: cropped() instead of crop()
    vid = vid.cropped(x_center=w/2, width=target_w)
    
    clips = []
    vid_time = 0.0
    
    print("Slicing footage to the beat...")
    for i in range(1, len(beat_times)):
        start_beat = beat_times[i-1]
        end_beat = beat_times[i]
        duration = end_beat - start_beat
        
        if vid_time + duration > vid.duration:
            vid_time = 0.0
            
        # v2 syntax: subclipped() instead of subclip()
        clip = vid.subclipped(vid_time, vid_time + duration)
        clips.append(clip)
        vid_time += duration
        
        if end_beat > 15.0:
            break
            
    print("Assembling timeline...")
    final_vid = concatenate_videoclips(clips)
    
    # v2 syntax: with_audio() instead of set_audio()
    final_vid = final_vid.with_audio(aud.subclipped(0, final_vid.duration))
    
    print("Exporting...")
    final_vid.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac", 
        preset="ultrafast"
    )
    print("Done. Go check the output.")

if __name__ == "__main__":
    generate_synced_video("dummy.mp4", "dummy.mp3", "output_MVP.mp4")