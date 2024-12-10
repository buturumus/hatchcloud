#!/usr/bin/python3
# cam2cloud.py

"""
This imports media files from a mounted cam dir
to for example mounted home media server's dir.
    cam dir example: /mnt/DCIM/Camera , in it:
        /mnt/DCIM/Camera/IMG_20240124_160829.jpg
                         VID_20240124_112645.3gp etc.
    cloud dir example: /srv/media , in it:
        /srv/media/2000-01-23--01-23-45/
                   2000-01-24--01-23-45/
                   2000-01-25--01-23-45/ etc.
"""

import os
import re
import glob
import shutil
from datetime import datetime

from cam2cloud_priv import srv_base_dir, cam_dir
from cam2cloud_priv import cam_dir
from cam2cloud_priv import last_dirs_limit


# to consider a date rather than a name's beginning in a sorting
# (IMG_20240124_160829.jpg vs VID_20230124_160829.3gp for example)
def sort_by_date(arr, date_regex, use_reverse):
    ext_arr = [[(re.search(date_regex, i)).group(), i] for i in arr]
    ext_arr.sort(reverse=use_reverse)
    return [j for i, j in ext_arr]


# in the cloud: find media dirs from previous imports
cloud_media_dirs = [
    d for d in next(os.walk(srv_base_dir))[1]
    if re.search('20[0-9]{2}(-[0-9]{2}){2}-(-[0-9]{2}){3}', d)
]
cloud_media_dirs.sort(reverse=True)
# find(recurs.) all existing media files in (given number of) last media dirs
cloud_file_paths = []
for d in cloud_media_dirs[0:(last_dirs_limit - 1)]:
    child_filedirs = glob.glob(f'{srv_base_dir}/{d}/*', recursive=True)
    for f in child_filedirs:
        if os.path.isfile(f):
            cloud_file_paths.append(f)

# now to camera
# files' tuple to list and sort
cam_file_names = [f for f in next(os.walk(cam_dir))[2]]

# copying
files_to_copy = []
for cam_file_name in sort_by_date(cam_file_names,
                                  '20[0-9]{2}([0-9]{2}){2}_([0-9]{2}){3}',
                                  True):
    no_such_file = True
    for cloud_file_path in cloud_file_paths:
        if os.path.basename(cloud_file_path) == cam_file_name:
            no_such_file = False
            break
    if no_such_file:
        files_to_copy.append(cam_file_name)
    else:
        print(f'{cam_file_name} exists in the cloud, search stopped.')
        break

for f in files_to_copy:
    print(f)
print(f'{len(files_to_copy)} files to copy.')
if not files_to_copy:
    quit()

now_obj = datetime.now()
new_cloud_path = (
    srv_base_dir + '/'
    + now_obj.strftime('%Y-%m-%d') + '--' + now_obj.strftime('%H-%M-%S')
)
print('Making dir ' + new_cloud_path)
os.mkdir(new_cloud_path)
print('Copying:')
for f in files_to_copy:
    print(f'{cam_dir}/{f} -> {new_cloud_path}/{f}')
    shutil.copy(f'{cam_dir}/{f}', new_cloud_path)
print('done.')

