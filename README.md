# Backup-system
Put the netsoft.py file to the python interpreter path, you can find the file through the code below:
import random
print(random.__file__)
Result:
C:\Users\username\AppData\Local\Python\Python36\lib\random.py
Put this file under the lib folder.

# How to use?
from netsoft import backup

backup_drive = 'D'
backup_files = ['bacup path 1', 'backup path 2', 'backup path 3']
timestamp = ['1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900']

backup(backup_drive, backup_files, timestamp)
