from os import makedirs, path
from shutil import copyfile
from shutil import rmtree as remove_tree
from distutils.dir_util import copy_tree
from sys import exit as die
import time
import re
import json


def unique_list(orig_list):
    # unique the orig_list array
    t_orig_list = []
    t_orig_list2 = []

    for i in range(0, len(orig_list)):
        t_f = 0  # target_found variable
        for j in range(0, len(orig_list)):
            for k in range(0, len(t_orig_list)):
                if orig_list[i] == t_orig_list[k]:
                    t_f = 1
                    break
            # create array containing number that is not unique in orig_list
            if orig_list[i] == orig_list[j] and i != j and t_f == 0:
                t_orig_list.append(orig_list[i])
                break
        if t_f == 0:
            t_orig_list2.append(orig_list[i])

    return t_orig_list2

def copy_files(orig_all_path, orig_root_path, target_root_path):
    target_folders = []
    for i in orig_all_path:
        target_path = i.replace(orig_root_path, target_root_path)
        target_folder = '\\'.join(target_path.split('\\')[:-1])
        target_folders.append(target_folder)
    target_folders = unique_list(target_folders)
    for i in target_folders:
        try:
            makedirs(i)
        except Exception as e:
            print('Error: ' + str(e))

    for i in orig_all_path:
        orig_path = i
        target_path = i.replace(orig_root_path, target_root_path)
        copyfile(orig_path, target_path)

class Backup:

    DAYSEC = 86400

    def __init__(self):
        # assign in create_root_backup_folder function
        self.backup_drive = ''

        # assign in create_backup function (self.this_year, self.today_date, self.backup_time)
        self.this_year = ''
        self.today_date = ''
        self.backup_time = ''

    def create_root_backup_folder(self, backup_drive):
        # create BACKUPS and log folder (check backup_drive parameter)
        if not re.search("^[A-Z]$", backup_drive):
            print('1st parameter must be a single uppercase character!')
            die()
        else:
            self.backup_drive = backup_drive
            try:
                makedirs(self.backup_drive + r':\BACKUPS\log')
            except:
                pass

    def check_backup_files(self, backup_files):
        # check backup_files parameter
        if type(backup_files) != list:
            print('2nd parameter must be a list!')
            die()

        for i in backup_files:
            if not path.isfile(i):
                print('Backup path does not exist:')
                print(i)
                die()

    def prepare_backup_files(self, backup_files):
        temp_backup_files = []
        for i in backup_files:
            if '/' in i:
                i = i.replace('/', '\\')
            temp_backup_files.append(i)
        return temp_backup_files

    def check_timestamp(self, timestamp):
        # check timestamp parameter
        error_text = """3rd parameter should be a string number list following the format ['HHMM']\nHH: hour\nMM: minute\ne.g. ['1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900']"""
        for i in timestamp:
            if bool(re.search("\d{4}", i)) and len(i) == 4 and int(i[:2]) <= 23 and int(i[2:]) <= 59:
                pass
            else:
                print(error_text)
                die()
        timestamp = unique_list(timestamp)
        timestamp.sort()

    def get_timestamp_difference(self, timestamp):
        timestamp_difference_orig, timestamp_difference = [], []
        for i in timestamp:
            timestamp_difference_orig.append(int(i[0:2]) * 60 * 60 + int(i[2:]) * 60)
            timestamp_difference.append(int(i[0:2]) * 60 * 60 + int(i[2:]) * 60)
        return timestamp_difference_orig, timestamp_difference

    def get_sleep_time(self, timestamp_difference_orig, timestamp_difference, timestamp, working_day):

        if time.localtime(time.time()).tm_wday < working_day:
            for i in range(len(timestamp_difference)):
                timestamp_difference[i] = (time.localtime().tm_hour*60*60+time.localtime().tm_min*60+time.localtime().tm_sec)-timestamp_difference_orig[i]
                if timestamp_difference[i] < 0:
                    backup_time = timestamp[i]
                    sleep_time = abs(timestamp_difference[i])
                    break
            else:
                if time.localtime(time.time()+self.DAYSEC).tm_wday < working_day:
                    timestamp_difference.sort(reverse=True)
                    timestamp.sort(reverse=True)
                    backup_time = timestamp[0]
                    sleep_time = abs(timestamp_difference_orig[0])+(self.DAYSEC-(time.localtime().tm_hour*60*60+time.localtime().tm_min*60+time.localtime().tm_sec))
                    timestamp_difference.sort()
                    timestamp.sort()
                else:
                    timestamp_difference.sort(reverse=True)
                    timestamp.sort(reverse=True)
                    backup_time = timestamp[0]
                    sleep_time = abs(timestamp_difference_orig[0])+(self.DAYSEC-(time.localtime().tm_hour*60*60+time.localtime().tm_min*60+time.localtime().tm_sec))+((7-working_day)*self.DAYSEC)
                    timestamp_difference.sort()
                    timestamp.sort()
        else:
            backup_time = timestamp[0]
            sleep_time = abs(timestamp_difference_orig[0])+(self.DAYSEC-(time.localtime().tm_hour*60*60+time.localtime().tm_min*60+time.localtime().tm_sec))+((6-time.localtime(time.time()).tm_wday)*self.DAYSEC)

        return sleep_time, backup_time, timestamp_difference

    def create_backup(self, backup_time, backup_files):
        self.this_year = str(time.localtime().tm_year)
        self.today_date = time.strftime('%Y%m%d', time.localtime())
        self.backup_time = backup_time
        timestamp_folder_path = self.backup_drive +':\\BACKUPS\\'+self.today_date+'\\'+self.backup_time
        success_backup = []

        for i in backup_files:
            folder_end = '\\'.join(i.split('\\')[:-1]).replace('\\\\', '\\')
            if ':' in i:
                folder_end = '\\' + folder_end.replace(':', '')
            backup_folder = timestamp_folder_path + folder_end
            backup_file = timestamp_folder_path + folder_end + '\\' + i.split('\\')[-1]

            # create backup folder
            try:
                makedirs(backup_folder)
            except:
                pass

            # create backup file
            if not path.isfile(backup_file):
                try:
                    copyfile(i, backup_file)
                    success_backup.append(backup_file)
                except:
                    pass
            else:
                pass

        if len(success_backup) > 0:
            self.create_log(success_backup)

    def create_log(self, success_backup):
        backup_log_path = self.backup_drive+':\\BACKUPS\\log\\'+self.this_year + '_backup_log.json'
        try:
            with open(backup_log_path, 'r', encoding='utf-8') as file:
                backup_log = json.loads(file.read())

            try:
                backup_log[self.today_date][self.backup_time] = success_backup
            except:
                backup_log[self.today_date] = {}
                backup_log[self.today_date][self.backup_time] = success_backup

            backup_log = json.dumps(backup_log)

            with open(backup_log_path, 'w', encoding='utf-8') as file:
                file.write(backup_log)
        except:
            backup_log = {}
            backup_log[self.today_date] = {}
            backup_log[self.today_date][self.backup_time] = success_backup
            backup_log = json.dumps(backup_log)

            with open(backup_log_path, 'w', encoding='utf-8') as file:
                file.write(backup_log)

def backup(backup_drive, backup_files, timestamp, working_day=5):

    worker = Backup()

    worker.create_root_backup_folder(backup_drive)

    worker.check_backup_files(backup_files)

    backup_files = worker.prepare_backup_files(backup_files)

    worker.check_timestamp(timestamp)

    # variables for calculate the next closest timestamp
    timestamp_difference_orig, timestamp_difference = worker.get_timestamp_difference(timestamp)

    # get sleep time
    sleep_time, backup_time, timestamp_difference = worker.get_sleep_time(timestamp_difference_orig, timestamp_difference, timestamp, working_day)

    time.sleep(sleep_time)

    while True:
        for i in timestamp:
            if int(backup_time[:2]) >= int(i[:2]) and int(backup_time[2:]) >= int(i[2:]):
                # start to backup here
                worker.create_backup(backup_time, backup_files)
                break

        sleep_time, backup_time, timestamp_difference = worker.get_sleep_time(timestamp_difference_orig, timestamp_difference, timestamp, working_day)

        time.sleep(sleep_time)


if __name__ == '__main__':
    pass
