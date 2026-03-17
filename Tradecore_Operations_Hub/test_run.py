import subprocess
import time

print("Starting app with xvfb-run...")
proc = subprocess.Popen(['xvfb-run', 'python3', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3) # Let it initialize

if proc.poll() is None:
    print("Process is running! App initialized successfully.")
    proc.terminate()
else:
    stdout, stderr = proc.communicate()
    print("Process crashed.")
    print("stdout:", stdout.decode())
    print("stderr:", stderr.decode())
