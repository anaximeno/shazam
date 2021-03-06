#!/usr/bin/env python3
""" Common is a support module, which contains the principals methods
and/or functions of this programm."""
# -*- coding: utf-8 -*-
__author__ = "Anaxímeno Brito"
__version__ = '0.4.7-beta'
__license__ = "GNU General Public License v3.0"
__copyright__ = "Copyright (c) 2020-2021 by " + __author__
import os
import sys
import string
import hashlib as hlib
from time import sleep
from typing import Generator, Iterable

# TODO: add type of the error when showing it, is should be one parameter of the function print_error
class Errors:

	@staticmethod
	def print_error(*err: str, exit: bool = True, err_num: int = 1, sep: str = '\n'):
		"""Print the error message and exit.\n
		Keyword args: 
			exit --> if is to exit after showing the error (default: True),
			err_num --> number of the error (default: 1)."""
		error_message = sep.join(err)

		print(f"shazam: error: %s" % error_message)

		if exit: 
			sys.exit(err_num)

	@classmethod
	def print_files_not_found(cls, files_not_found: Iterable, exit: bool = False):
		n_not_found = len(files_not_found)
		if n_not_found == 0:
			pass

		elif n_not_found == 1:
			cls.print_error(f'cannot read: {files_not_found[0].get_fullpath()!r}', exit=exit)

		else:
			cls.print_error('Files that were not Found or cannot be read:', exit=False)

			for file in files_not_found:
				print(f'  -> {file.get_fullpath()!r}')	

			if exit:
				sys.exit(1)

	@classmethod
	def file_not_readable(cls, file, exit: bool = True):
		error = 'file not found:' if file.exists() is False else 'cannot read:' 
		cls.print_error(f'{error} {file.get_fullpath()!r}!', exit=exit)


to_install = []
try:
	from termcolor import colored as clr
except ImportError:
	to_install.append('termcolor')
try:
	from tqdm import tqdm
except ImportError:
	to_install.append('tqdm')
finally:
	if any(to_install):
		modules_to_install = ' and '.join(to_install)
		Errors.print_error(
			f"The package(s) {modules_to_install!r} must be installed before using the program!",
			f"\nInstall them with:\n\n\t $ pip install {' '.join(to_install)}\n", exit=True
		)
	else:
		del to_install


def hexa_to_int(hexa: str):
	"""Receive hexadecimal string and return integer."""
	if set(hexa).issubset(string.hexdigits):
		return int(hexa, 16)
	Errors.print_error(f"{hexa!r} is not an hexadecimal value!")


def get_hashtype_from_filename(filename: str):
	"""Analyses the filename and return the hashtype."""
	for stype in Process.HASHTYPES_LIST[::-1]:
		if stype in filename: 
			return stype
	else:
		return None


def get_hashtype_from_string_length(string: str):
	"""Return the hashtype from the length of the string"""
	type_tab = {
		32: 'md5',
		40: 'sha1',
		56: 'sha224',
		64: 'sha256',
		96: 'sha384',
		128: 'sha512'
	}

	l = len(string)

	if l in type_tab:
		return type_tab[l]
	else:
		return None


def animate(string: str, sleep_time: float = 0.1):
	for char in string:
		if char != '\n' and char != '\t':
			sleep(sleep_time)
		sys.stdout.write(char)
		sys.stdout.flush()
	print('')	# Go to new line


class File(object):
	"""This class holds all necessary informations and operations
	for one file object."""
	# Will store files that exists or not.
	Found = []
	Not_Found = []
	Unreadable = []

	def __init__(self, filename: str, given_hashsum: str = '', file_for_check: bool = True, **kwargs):
		self._file_is_for_check = file_for_check
		self._dir, self._fname = os.path.split(filename)
		if '.' in self._fname:
			self._name, self._extension = os.path.splitext(self._fname)
		else:
			self._name, self._extension = self._fname, ''

		if len(self._name) > 1 and self._name.startswith('*') and not self.exists():
			self._name = self._name[1:]

		# ´givensum´ is the original file sum which is give at the download place.
		self._gsum = given_hashsum

		# ´self._given_integer_sum´ is the integer value of the hash sum,
		# it will be used in comparisons for checking if the values are equal.
		self._given_integer_sum = hexa_to_int(self._gsum) if self._gsum else None
		if self._file_is_for_check is True:
			self._calculated_hashes = []
			self._hlist = {
				"md5": hlib.md5(),
				"sha1": hlib.sha1(),
				"sha224": hlib.sha224(),
				"sha256": hlib.sha256(),
				"sha384": hlib.sha384(),
				"sha512": hlib.sha512()
			}

			if self.exists() is True:
				if self.is_readable() is True:
					self.Found.append(self)
				else:
					self.Unreadable.append(self)
			else:
				self.Not_Found.append(self)

	def __str__(self):
		return self.get_fullpath()

	def get_name(self) -> str:
		"""Returns the name of the file without its extension, and without its the full path address."""
		return str(self._name)

	def get_extension(self) -> str:
		"""Returns the extension of the file."""
		return str(self._extension)

	def get_fullname(self) -> str:
		"""Returns the name of the file plus its extension, but without his full path address."""
		return self.get_name() + self.get_extension()

	def get_dir(self) -> str:
		"""Returns the current directory of this file."""
		return str(self._dir)

	def get_fullpath(self) -> str:
		"""Returns the full path of this file."""
		return os.path.join(self.get_dir(), self.get_fullname())

	def get_size(self) -> int:
		"""Returns the size in bytes of the file, only if it exists, else None."""
		if self.exists() is True:
			return os.path.getsize(self.get_fullpath())
		return None
	
	def get_given_sum(self) -> str:
		"""Returns the given sum of the file which will be used to compare with the calculated one, 
		for checking this file integrity."""
		return str(self._gsum)

	def exists(self) -> str:
		"""Returns if this objects exists on his directory."""
		return os.path.exists(self.get_fullpath())
	
	def is_dir(self) -> bool:
		"""Returns if this object is a directory."""
		return os.path.isdir(self.get_fullpath())

	def is_readable(self) -> bool:
		"""Returns if the file is readable or not. It must: exist on its directory, not be a directory and 
		be readable in the binary mode."""
		if not self.exists() or self.is_dir():
			return False
		try:
			with open(self.get_fullpath(), 'rb') as f:
				f.read(1)
			return True
		except UnicodeDecodeError:
			return False

	def get_hashsum(self, hashtype: str):
		"""Return the file's hash sum."""
		if hashtype in self._calculated_hashes:
			return self._hlist[hashtype].hexdigest()
		return None

	def gen_data(self, *, bar_anim: bool = True) -> Generator:
		"""Generates binary data. 
		
        Keyword arg: 
			bars_anim -- if True the function will show progress bars when generating the data.
		"""
		if self.is_readable() is False:
			Errors.file_not_readable(self, exit=True)

		BUF_SIZE = 32768
		times = (self.get_size() // BUF_SIZE) + (self.get_size() % BUF_SIZE)
		loop = tqdm(range(times), ncols=80, desc='CALCULATING BINARIES') if bar_anim else range(times)
		with open(self.get_fullpath(), 'rb') as f:
			for _ in loop:
				yield f.read(BUF_SIZE)
				sleep(Process.SLEEP_VALUE)	

	def update_data(self, hashtype: str, generated_data: Iterable) -> None:
		"""Updates binary data to the hashtype's class."""
		if self.is_readable() is False:
			Errors.file_not_readable(self, exit=True)

		for file_data in generated_data:
			self._hlist[hashtype].update(file_data)
		self._calculated_hashes.append(hashtype)

	def checksum(self, hashtype: str) -> bool:
		"""Compares file's sum with givensum and return the results"""
		return hexa_to_int(self.get_hashsum(hashtype)) == self._given_integer_sum


class TextFile(File):

	def __init__(self, filename: str, **kwargs):
		super().__init__(filename,
			given_hashsum=kwargs['given_hashsum'] if 'given_hashsum' in kwargs else '', 
			file_for_check=kwargs['file_for_check'] if 'file_for_check' in kwargs else False, 
			**kwargs)

	def read_content(self):
		"""Return a `list with tuples` with the content of the file,
		each tuple has the following structure: `(filesum, filename)`."""
		if self.is_readable() is False:
			Errors.file_not_readable(self, exit=True)
		try:
			with open(self.get_fullpath(), 'rt') as textfile:
				content = [
					(line.split()[0], line.split()[1]) for line in textfile
				]
			if content:
				return content
			Errors.print_error(f'{self.get_fullpath()!r} is empty!')
		except IndexError:
			Errors.print_error(f'error reading {self.get_fullpath()!r}!')
		except UnicodeDecodeError:
			Errors.print_error(f'Cannot read {self.get_fullpath()!r}!')


class Process(object):
	# When lower is the sleep value, faster will be the reading,
	# but it will increase the CPU usage, it can be changed to
	# improve the performance.
	SLEEP_VALUE = 1e-7
	# List of all supported hash sums:
	HASHTYPES_LIST = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]

	def __init__(self):
		# TODO: Check this init!!

		# ´self.found´ and ´self.unfound´ store files depending on their
		# existence/readability or not, and below them are their respective lengths.
		self._files_found = File.Found
		self._files_not_found = File.Not_Found

	def _show_file_result(self, file: File, hashtype: str):
		if file.checksum(hashtype) is True:
			color = "green"
			post_msg = 'not modified.'
		else:
			color = "red"
			post_msg = 'probably modified!!'
		return clr(f"{file.get_fullpath()!r} was {post_msg}", color)

	def checkfile(self, file: File, hashtype: str, **kwargs):
		"""Check and Compare the hash sum."""
		file_data = kwargs['file_data'] if 'file_data' in kwargs else None
		bar_anim  = kwargs['bar_anim'] if 'bar_anim' in kwargs else True
		verbosity = kwargs['verbosity'] if 'verbosity' in kwargs else True
		found, _ = self._search_files([file])

		if not any(found):
			Errors.print_error(f'{file.get_fullpath()!r} was not found!')

		file.update_data(hashtype=hashtype,
			generated_data=file_data or file.gen_data(bar_anim=bar_anim))
		print(f"\n{ ' ┌──' if verbosity else '' } {self._show_file_result(file, hashtype)}")
		if verbosity:
			print(f" │ ORIGINAL {hashtype.upper()}SUM:  {file.get_given_sum()!r}")
			print(f" │ CURRENT  {hashtype.upper()}SUM:  {file.get_hashsum(hashtype)!r}")
			print(' └──────────────')

	def calculate_sum(self, files: Iterable, hashtype: str, verbosity: bool = True):
		"""Calculates and prints the file's hash sum."""
		found, not_found = self._search_files(files)
		n_found = len(found)

		if n_found != 0:
			# TODO: mostra o tipo de hash sum que está a ser calculado, e em outros lugares tmb!
			if n_found == 1:
				file = found[0]
				file.update_data(hashtype, file.gen_data(bar_anim=True))
				print('')
				if verbosity:
					print(f"{file.get_hashsum(hashtype)} {file.get_fullpath()}")
			else:
				for file in tqdm(found, desc='CALCULATING BINARIES', ncols=80):
					file.update_data(hashtype, file.gen_data(bar_anim=False))

				if verbosity:
					print('')
					for file in found:
						print(f"{file.get_hashsum(hashtype)} {file.get_fullpath()}")
					

		if any(found) and any(not_found):
			print()  # Skip one line

		Errors.print_files_not_found(not_found)

	def checkfiles(self, files: Iterable, hashtype: str, verbosity=False):
		"""Checks and compare the hash sums of more than one files."""
		found, not_found = self._search_files(files)
		n_found = len(found)

		if n_found == 0:
			Errors.print_files_not_found(not_found, exit=True)
		elif n_found == 1:
			self.checkfile(found[0], hashtype, verbosity=verbosity)
		else:
			storedData = []
			for file in tqdm(found, desc='CALCULATING BINARIES', ncols=80):
				if verbosity is False:
					file.update_data(
						hashtype=hashtype, 
						generated_data=file.gen_data(bar_anim=False))
				elif verbosity is True:
					storedData.append(list(file.gen_data(bar_anim=False)))
				else:
					Errors.print_error('Verbose type (True or False) must be set!')


			if verbosity is True:
				for file, file_data in zip(found, storedData):
					self.checkfile(file, hashtype, file_data=file_data, bar_anim=False)
				print('')  # new line at the end
			else:
				for file in found:
					print(self._show_file_result(file, hashtype))
	
		Errors.print_files_not_found(not_found)

	def totalcheck(self, files: Iterable):
		"""Print all supported hash sums of one file."""
		found, not_found = self._search_files(files)
		n_found = len(found)

		if n_found == 0:
			Errors.print_files_not_found(not_found, exit=True)

		generated_datas = [
			list(file.gen_data(bar_anim=False))
			for file in tqdm(found, ncols=71, desc='Calculating Binaries')
		]


		def update_generator():
			for file, generated_data in zip(found, generated_datas):
				for hashtype in file._hlist.keys():
					file.update_data(hashtype, generated_data)
					sleep(Process.SLEEP_VALUE)
					yield

		ug = update_generator()

		for _ in tqdm(range(len(found[0]._hlist.keys())*n_found), ncols=75, desc='Getting Hash Sums'):
			next(ug)
		print('\n')

		for n, file in enumerate(found):
			if n > 0 and n < n_found:
				print("\n")
			print(f" ┌── {file.get_fullname()!r}")
			for hashtype in file._hlist.keys():
				print(f" │ {hashtype}: {file.get_hashsum(hashtype)} {file.get_fullpath()}")
			print(' └────────────────────')

		Errors.print_files_not_found(not_found)

	def _search_files(self, files: Iterable):
		files = set(files)

		found = list(files.intersection(File.Found))

		not_found = files.intersection(File.Not_Found)
		unreadable = files.intersection(File.Unreadable)

		not_found_and_ureadable = list(not_found.union(unreadable))

		return found, not_found_and_ureadable

	def write(self, files: Iterable, hashtype: str, name: str = None):
		found, _ = self._search_files(files)
	
		if len(found) != 0:
			filename = name or (hashtype + 'sum.txt')
			with open(filename, 'wt') as txt:
				for file in found:
					txt.write(f"{file.get_hashsum(hashtype)} {file.get_fullpath()}\n")
			animate(f"\nFile {filename!r} was created!", sleep_time=0.045)			
		else:
			Errors.print_error('No avaliable files for saving hash sums!')

