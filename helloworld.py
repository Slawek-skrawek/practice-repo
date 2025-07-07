import os
import subprocess


print("Hello World")

#os.popen("gnome-calculator")

os.chdir("/home/slawek/work/myproj")

# os.popen("newt target create nordic_pca10040-firstloop")
# os.popen("newt target set nordic_pca10040-firstloop app=apps/firstloop")
# os.popen("newt target set nordic_pca10040-firstloop bsp=@apache-mynewt-core/hw/bsp/nordic_pca10040")
# os.popen("newt target set nordic_pca10040-firstloop build_profile=debug")
# os.popen("newt create-image nordic_pca10040-firstloop timestamp")

project_path = "/home/slawek/work/myproj"

# subprocess.check_call('newt target create nordic_pca10040-firstloop',
#                       env=None, cwd=project_path, shell=True, executable='/bin/bash')

subprocess.check_call('newt target set nordic_pca10040-firstloop app=apps/firstloop',
                      env=None, cwd=project_path, shell=True, executable='/bin/bash')
subprocess.check_call('newt target set nordic_pca10040-firstloop bsp=@apache-mynewt-core/hw/bsp/nordic_pca10040',
                      env=None, cwd=project_path, shell=True, executable='/bin/bash')
subprocess.check_call('newt target set nordic_pca10040-firstloop build_profile=debug',
                      env=None, cwd=project_path, shell=True, executable='/bin/bash')

subprocess.check_call('newt create-image nordic_pca10040-firstloop timestamp',
                      env=None, cwd=project_path, shell=True, executable='/bin/bash')
