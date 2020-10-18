# Author: Anaximeno Brito

from hashes import hashes as hashlist
import os


sumslist = {}

for item in hashlist:
    sumslist[item + "sum"] = item
    sumslist[item + "sums"] = item


tp = ''  # for posterior use
for item in sumslist:
    tp += '\n ' + item


def is_readable(file):
    if exists(file):
        try:
            with open(file, "rt") as f:
                f.read(1)
                return True
        except UnicodeDecodeError:
            print(f"checksum: error: {file} is unreadable, must be a file with the sums and filename inside!")
            return False
    else:
        print(f"checksum: error: {file} do not exits in this dir!")


# check the existence of the file
def exists(file):
    try:
        with open(file, 'rb') as target:
            if target:
                return True
    except IOError:
        return False


# check if the value is an hexadecimal value
def _hex(hexa):
    try:
        int(hexa, 16)
        return True
    except ValueError:
        return False


# analyze the existence and the sum conditions
def analyze_file(f_name, f_sum):
    if exists(f_name) and _hex(f_sum):
        return True
    elif not exists(f_name):
        print(f"checksum: error: '{f_name}' was not found here in this directory!")
    elif not _hex(f_sum):
        print(f"checksum: error: '{f_sum}' is not an hexadecimal number!")


def type_of_sum(text):
    if is_readable(text):
        sum_name, file_ext = os.path.splitext(text)
        del file_ext  # unnecessary already
        if sum_name in sumslist:
            return sumslist[sum_name]
        else:
            print(f"checksum: error: '{sum_name}' is unsupported already!")
            print("'-a' method uses the file name to specify the type of sum that should be used," +
                  f" so the file name actually supported are: {tp}")
            return False


# analyze the content of the sum.txt given
def analyze_text(text):
    if not type_of_sum(text):
        return False, False
    try:
        file_base = {}
        with open(text, "rt") as t:
            try:
                l = 0
                for line in t:
                    l += 1
                    file_sum, file_name = line.split()
                    file_base[file_name] = file_sum
            except ValueError:
                print(f"checksum: error: '{text}' must have the " +
                      f"file sum and the file name in each line!\nIrregularity in line {l}")
                return False, False
            not_found = []
            found = []
            t = 0
            for files in file_base:
                t += 1
                if exists(files):
                    found.append((files, file_base[files], type_of_sum(text)))
                    if t == len(file_base):
                        if found:
                            return found, not_found
                elif not exists(files):
                    not_found.append(files)
                    if len(not_found) == len(file_base):
                        nfound = ""
                        for nf in not_found:
                            nfound += "\n -> " + nf
            
                        print(f"checksum: error: None of these '{text}' file(s) " +
                              f"below was found in this directory: {nfound}")

                        return False, False
    except FileNotFoundError:
        print(f"checksum: error: '{text}' was not found!")
        return False, False
