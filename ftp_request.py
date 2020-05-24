from ftplib import FTP
import os

ftp = FTP(host='25.41.161.243')
print(ftp.login('user'))

data = ftp.retrlines('LIST')
print(data)

# ftp.cwd('movies')
f = open('game.exe', 'wb')
ftp.retrbinary('RETR ' + 'game.exe', f.write)

f = open('sheet.jpg', 'wb')
ftp.retrbinary('RETR ' + 'sheet.jpg', f.write)

path = os.getcwd()
os.startfile(path + '\game.exe')
