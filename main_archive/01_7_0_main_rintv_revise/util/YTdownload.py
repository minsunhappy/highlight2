from pytube import YouTube
import os
import subprocess

def download_youtube_video(video_id, source_path):
    # 파일이 존재하는지 확인
    output_path = f"{source_path}/{video_id}.mp4"
    url = f"https://www.youtube.com/watch?v={video_id}"
    if not os.path.isfile(output_path):
        # yt-dlp 명령어 설정
        command = [
            "yt-dlp",
            "-f", "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "--merge-output-format", "mp4",
            "-o", output_path,
            url
        ]

        try:
            # yt-dlp 명령어 실행
            subprocess.run(command, check=True)
            print(f"다운로드 완료: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"다운로드 중 오류 발생: {e}")
    else:
        print(f"파일이 이미 존재합니다: {output_path}")