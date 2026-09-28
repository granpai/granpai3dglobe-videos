#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
for input in output/*.webm; do
  name="$(basename "$input" .webm)"
  case "$name" in
    hvac) title='9 LOCATIONS. ONE MAP.'; sub='Show every branch with interactive pins.';;
    timeline) title='WATCH YOUR COMPANY GROW.'; sub='Turn milestones into an interactive story.';;
    global-impact) title='EVERY PROJECT, ONE GLOBE.'; sub='Browse locations in the sidebar.';;
  esac
  font=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
  trim="$(node -p "require('./output/${name}.json').trimSeconds")"
  ffmpeg -hide_banner -loglevel error -y -ss "$trim" -i "$input" -filter_complex "[0:v]fps=30,scale=1080:675[screen];color=c=0x071422:s=1080x1920:r=30[bg];[bg][screen]overlay=0:610:shortest=1,drawtext=fontfile=${font}:text='${title}':fontcolor=white:fontsize=49:x=(w-text_w)/2:y=390,drawtext=fontfile=${font}:text='${sub}':fontcolor=0x80e8f2:fontsize=29:x=(w-text_w)/2:y=1340,drawtext=fontfile=${font}:text='Made for WordPress':fontcolor=white:fontsize=34:x=(w-text_w)/2:y=1520,drawtext=fontfile=${font}:text='3dglobe.granpai.com':fontcolor=0x00d8ee:fontsize=39:x=(w-text_w)/2:y=1610,format=yuv420p[v]" -map '[v]' -t 16 -an -c:v libx264 -preset veryfast -crf 23 -movflags +faststart "output/${name}.mp4"
done
