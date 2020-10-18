# Author: Anaximeno Brito


import readinst
import os
from hashes import *
from time import sleep
from alive_progress import alive_bar
from termcolor import colored
import py

hashlist = hashes

# don't change this number
BUF_SIZE = 32768


def gen_data(dt):
    if dt:
        yield dt


# read all sums
def all_sums(f_name):
    with alive_bar(len(hashlist), bar='blocks', spinner='dots') as bar:
        for s_type in hashlist:
            with open(f_name, 'rb') as f:
                hashlist["md5"] = hashlib.md5()
                while True:
                    try:
                        data = gen_data(f.read(BUF_SIZE))
                        hashlist[s_type].update(next(data))
                        sleep(0.00001)  # when lower is this value, faster will be the reading,
                        # but it will use more CPU
                    except StopIteration:
                        break
            bar()


# read and set the file's sum
def readata(f_name, s_type):

    def rep(s):
        t = 0
        while s > 0:
            s -= BUF_SIZE
            t += 1
            yield t

    size = os.path.getsize(f_name)
    times = 0
    for x in rep(size):
        times = x

    with alive_bar(times, bar='filling', spinner='dots') as bar:
        with open(f_name, 'rb') as f:
            while True:
                try:
                    data = gen_data(f.read(BUF_SIZE))
                    hashlist[s_type].update(next(data))
                    sleep(0.00001)  # when lower is this value, faster will be the reading,
                    # but it will use more CPU
                    bar()
                except StopIteration:
                    break


# check if the file's sum is equal to the given sum
def check(f_sum, s_type, f_name):
    x = int(f_sum, 16)
    h = hashlist[s_type].hexdigest()

    lin = '-' * 100

    if int(h, 16) == x:
        print(colored(f"#SUCESS, '{f_name}' {s_type}sum matched!", "green"))
    else:
        print(colored(f"%unsuccess, '{f_name}' {s_type}sum didn't matched!\n", "red"))

    ''' * To make a verbose response *
    if int(h, 16) == x:
        print('\n' + lin)
        print(colored(f"  #SUCESS, '{f_name}' {s_type}sum matched!", "green"))
        print(lin)
        print(f"\n-> '{f_name}' {s_type}sum: {h}")
        print(f"\n-> Match with the given sum: {f_sum}")
    else:
        print('\n' + lin)
        print(colored(f"  %unsuccess, '{f_name}' {s_type}sum didn't matched!", "red"))
        print(lin)
        print(f"\n-> '{f_name}' {s_type}sum: {h}")
        print(f"\n-> Don't Match with the given sum: {f_sum}")
    '''

# if we have the file's name and sum
def normal(s_type, f_name, f_sum):
    if readinst.analyze_file(f_name, f_sum):
        readata(f_name, s_type)
        check(f_sum, s_type, f_name)


# if the file's name and sum is in a sum.txt file
def text(txt):
    found, not_found = readinst.analyze_text(txt)
    del not_found  # unnecessary here

    if found:
        f_name, f_sum, s_type = found[0]

        readata(f_name, s_type)
        check(f_sum, s_type, f_name)


# get all sums
def allsums(f_name):
    if readinst.exists(f_name):
        all_sums(f_name)
        output = ""
        for typo in hashlist:
            output += f" {typo}sum: {hashlist[typo].hexdigest()}\n"
        print(f"\nAll '{f_name}' sums below: ")
        print(output)
    else:
        print(f"checksum: error: '{f_name}' was not found in this directory!")


# if we want only show the sum and no to compare it
def only_sum(s_type, f_name):
    if readinst.exists(f_name):
        readata(f_name, s_type)
        print(f"'{f_name}' {s_type}sum is: {hashlist[s_type].hexdigest()}")
    else:
        print(f"checksum: error: '{f_name}' was not found in this directory!")


def multi_files(text):
    found, not_found = readinst.analyze_text(text)
    if found:
        for i in range(len(found)):
            f_name, f_sum, s_type = found[i]

            readata(f_name, s_type)
            check(f_sum, s_type, f_name)

            # reinitialize the sums data
            del hashlist[s_type]
            hashlist[s_type] = hashes_n2[s_type]
        if not_found:
            nf = ''
            for n in not_found:
                nf += not_found[n] + '\n '
            print(f"\nThe file(s) below was not found: {nf}")
