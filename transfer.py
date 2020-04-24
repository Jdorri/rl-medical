import subprocess
import glob

username = 'hgc19'  # <--- CHANGE HERE

subprocess.run(["scp", "-pr", "./call_gpu_copy.py", username + "@gpucluster.doc.ic.ac.uk:Documents/rl-medical"])

files = glob.glob("./examples/LandmarkDetection/DQN/*.py")
for file in files:
    subprocess.run(["scp", "-pr", file, username + "@gpucluster.doc.ic.ac.uk:Documents/rl-medical/examples/LandmarkDetection/DQN"])





sshProcess = subprocess.Popen(['ssh',
                               username + "@gpucluster.doc.ic.ac.uk"],
                               stdin=subprocess.PIPE,
                               stdout = subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0)

sshProcess.stdin.write(f"python3 Documents/rl-medical/call_gpu_copy.py\n")
sshProcess.stdin.close()
