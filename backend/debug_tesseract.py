import subprocess

with open("/tmp/tess.png", "wb") as f:
    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d5\xe9\x04\x00\x00\x00\x00IDAT\x08\xd7c\xf8\x0f\x00\x01\x01\x01\x00\x1a\xec\xa7\x9d\x00\x00\x00\x00IEND\xaeB`\x82')

proc = subprocess.Popen(["/opt/homebrew/bin/tesseract", "/tmp/tess.png", "-", "-l", "eng"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = proc.communicate()
print("STDOUT:", stdout[:100])
print("STDERR:", stderr[:100])
