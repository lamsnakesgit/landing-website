import os
import glob
import pyJianYingDraft as draft
from pyJianYingDraft import DraftFolder, ScriptFile, VideoSegment

videos_dir = os.path.join(os.getcwd(), "Veo_Videos_Raw")
mp4_files = sorted(glob.glob(os.path.join(videos_dir, "veo31_*_final.mp4")))

# Put it in the user's Desktop
desktop = os.path.expanduser("~/Desktop")
capcut_projects_dir = os.path.join(desktop, "CapCut_Generated_Projects")
if not os.path.exists(capcut_projects_dir):
    os.makedirs(capcut_projects_dir)

draft_folder = DraftFolder(capcut_projects_dir)
script = draft_folder.create_draft("LoveStory_AI", 720, 1280, 30, allow_replace=True)
script.add_track(draft.TrackType.video, "main_video")

current_time = 0
for idx, mp4_path in enumerate(mp4_files):
    dur = 8000000
    target_timerange = draft.Timerange(current_time, dur)
    source_timerange = draft.Timerange(0, dur)
    
    video_seg = VideoSegment(
        material=mp4_path,
        target_timerange=target_timerange,
        source_timerange=source_timerange
    )
    
    script.add_segment(video_seg, track_name="main_video")
    current_time += dur

script.save()
print(f"CapCut draft generated successfully at: {capcut_projects_dir}")
