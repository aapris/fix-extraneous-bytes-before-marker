import argparse
import binascii
import os
import re
import subprocess
import sys


def run_command(cmd):
    """
    Use subprocess.Popen() to run command and capture stderr and stdout.
    :param list cmd: a command including all arguments
    :return: returncode, stdout, stderr strings
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


def find_extraneous_bytes_before_marker(filepath):
    """
    Run Imagemagick's identify command. If command outputs to stderr special
    "extraneous bytes" error message, then capture size of extra bytes and marker code.
    Return None if extraneous bytes are not found, otherwise values extracted from error message.

    NOTE: it should be possible to replace identify with some other
          program which uses libjpg behind the scenes.

    :param str filepath:
    :return: size of extrabytes (int), marker number (hex str), error message
    """
    code, out, err = run_command(['identify', filepath])
    err_str = err.decode('utf8')
    ending = "extraneous bytes before marker"
    if err_str.find(ending) < 0:
        return None, None, None
    m = re.search(r'Corrupt JPEG data: ([\d]+) extraneous bytes before marker (0x[\w]+)', err_str)
    size = int(m.group(1))
    marker = m.group(2)
    return size, marker, err_str


def main(filepath):
    log_msg = filepath + ': '
    size, marker, err_str = find_extraneous_bytes_before_marker(filepath)
    if size is None:
        log_msg += "File ok."
        print(log_msg)
        return
    with open(filepath, 'rb') as f:
        data = f.read()
    data = re.split(b'\xff(?!\x00)', data)
    for i in range(1, len(data)):
        c = data[i]
        if hex(c[0]) == marker and len(data[i - 1]) > size:
            log_msg += "Removing {} bytes before marker {}. ".format(size, marker)
            data[i - 1] = data[i - 1][:-size]
    newfile = filepath + '-xxx.jpg'
    with open(newfile, 'wb') as f:
        f.write(b'\xff'.join(data))
    # Verifying that reading the new file returns no error...
    size, marker, err_str = find_extraneous_bytes_before_marker(newfile)
    if size is None:
        log_msg += f"File now ok, saved to {newfile}"
    else:
        log_msg += f"FAILED! {err_str}"
    print(log_msg)


if __name__ == "__main__":
    main(sys.argv[1])
