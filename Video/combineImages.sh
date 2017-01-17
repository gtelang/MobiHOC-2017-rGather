# This was used to make video from a outputted images which ran the dynamic 4-apx clustering algorithm for trajectories
# versus the algorithm for static point-sets run at each time-step. 
rm *.mp4
ffmpeg -f image2 -framerate 3 -i dynamic_algorithm_%03d.png dynamic_algorithm.mp4
ffmpeg -f image2 -framerate 3 -i static_repeat_%03d.png static_repeat.mp4
ffmpeg -i dynamic_algorithm.mp4 -i static_repeat.mp4 -filter_complex "[0:v:0]pad=iw*2:ih[bg]; [bg][1:v:0]overlay=w" video_compare.mp4
