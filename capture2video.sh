mencoder mf://capture/*.png -mf fps=50:type=png -ovc lavc \
    -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o capture.avi
