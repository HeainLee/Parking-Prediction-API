import os 

LOG = ' log'.replace('\u2028','')

if not os.path.exists(LOG) or not os.path.isdir(LOG):
    os.mkdir(LOG)