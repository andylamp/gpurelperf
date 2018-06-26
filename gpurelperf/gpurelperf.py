import json
import os
import platform
import re
import shutil
import sys
import time
import logging
from operator import itemgetter
from pathlib import Path
from subprocess import run, PIPE

import requests

benchURI = "https://browser.geekbench.com/cuda-benchmarks.json"
bench_filename = "cur_bench.json"
nvsmi = "nvidia-smi"
nvsmi_args = "--list-gpus"
bench_dict = dict()
gpu_ratios = list()
gpu_ratios_min = list()
# 30 days modify
modify_threshold = 24 * 30

WIN_PATHS = [
    "C:\\Program Files\\NVIDIA Corporation\\NVSMI\\"
]


def fetch_json():
    """This function fetches the current JSON data from geekbench

    :return: nothing
    """
    logging.info("Fetching benchmark data")
    # get a streaming request
    r = requests.get(benchURI, stream=True)
    # which is then streamed to `cur_bench.json` in
    # the current directory.
    with open(bench_filename, 'wb') as sfd:
        for stream_chunk in r.iter_content(chunk_size=128):
            sfd.write(stream_chunk)


def fetch_benchmarks():
    """ This function fetches the benchmarks from geekbench and writes them
    to a file. This is only done if the file does not exist or has not been
    updated in a long time.

    :return: nothing
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, bench_filename)
    file = Path(file_path)
    logging.info("Fetching benchmarks...")
    if not file.is_file():
        fetch_json()
    else:
        p = os.path.getmtime(file_path)
        c_time = time.time()
        dist = round((c_time - p) / 3600)
        logging.info("\tFile exists and was last modified {} hours ago".format(dist))
        if dist > modify_threshold:
            logging.warning("\tNeed to fetch benchmarks again, as they are old.")
            fetch_json()
        else:
            logging.info("\tFile age is within bounds, not fetching again.")
    # now parse them
    parse_benchmarks()


def parse_benchmarks():
    """This function parses the JSON data and finds the graphics cards as well as
    their names.

    :return: nothing
    """
    print("Parsing benchmarks")
    bench_data = json.load(open(bench_filename, 'r'))
    devs = bench_data["devices"]
    for d in devs:
        bench_dict[d["name"]] = int(d["score"])

    bench_list = sorted(bench_dict.items(), key=itemgetter(1))
    logging.info("Current Best/Worst:")
    logging.info("\tBest card: {}: {}".format(bench_list[-1][0], bench_list[-1][1]))
    logging.info("\tWorst card: {}: {}".format(bench_list[0][0], bench_list[0][1]))


def get_sys_cards():
    """This function retrieves the system cards using nvsmi for linux and windows;
    macOS support is in the works.

    :return: returns a tuple containing the in `gpu_ratios_min` and actual `gpu_ratios`; the
    difference being that the latter is sorted in ascending order while the other one is random.
    """
    # fetch the benchmarks (if needed)
    fetch_benchmarks()
    # now get current cards from nvsmi
    logging.info("Getting current system cards")
    if platform.system() == 'Windows':
        nvsmi_p = get_nvsmi_win()
    elif platform.system() == 'Darwin':
        nvsmi_p = get_nvsmi_macos()
    else:
        nvsmi_p = get_nvsmi_unix()
    # check the returned value
    if nvsmi_p is None:
        raise Exception("Could not find Nvidia SMI or cannot access it...")

    # check if we got something None
    if nvsmi_p is None:
        print("Not supported on this platform yet")
        return 0, 0

    # else continue
    r = run([nvsmi_p, nvsmi_args], stdout=PIPE, encoding="utf-8")
    # print(r.stdout)
    filter_nvsmi_output(r.stdout)
    # finally return the values
    return gpu_ratios_min, gpu_ratios


def filter_nvsmi_output(nvsmi_out):
    """Function that parses the nvsmi output, it assumes that all have a common format, as defined by
    nvidia.

    :param nvsmi_out: nvidia smi raw output
    :return: the parsed values, namely graphics card names and their scores in a dictionary in which the key is
    the graphics card name and the value is its score like so: ['name': 'score']
    """
    logging.info("Filtering nvsmi output...")
    min = sys.maxsize
    for line in nvsmi_out.splitlines():
        # print("Line: {}".format(line))
        flt_line = re.search(r':(.*?)\(UUID', line).group(1).strip()
        # print("Filtered line: {}".format(flt_line))
        l_min = bench_dict[flt_line]
        if l_min < min:
            min = l_min
            logging.info("\tMatched entry from dictionary: {} for tag: {}".format(l_min, flt_line))
        gpu_ratios.append((flt_line, l_min))
    # finally calculate the ratios
        logging.info("Calculating card ratios:")
    for i, (g, v) in enumerate(gpu_ratios):
        gpu_ratios[i] = (g, round(float(v) / float(min), 2))
        gpu_ratios_min.append(round(float(v) / float(min), 2))
        logging.info("\tCard index: {}, Name: {}, Ratio: {}".format(i, g, gpu_ratios_min[i]))


def get_nvsmi_win():
    """Function that probes the nvsmi in windows

    :return: the path of nvsmi or `None`
    """
    logging.info("Detected System: Windows")
    nvsmi_exe = nvsmi + ".exe"
    for p in WIN_PATHS:
        loc_path = os.path.join(p, nvsmi_exe)
        if shutil.which(loc_path) is not None:
            return loc_path
    return None


def get_nvsmi_unix():
    """Function that probes the nvsmi in Unix

    :return: the path of nvsmi of `None`
    """
    logging.info("Detected System: Unix-like")
    return shutil.which(nvsmi)


def get_nvsmi_macos():
    """Function that problems the nvsmi in macOS -- since nvsmi is not available
    in macOS officially, we need to use a native extension (cuda-smi) to do this.

    This is a WIP.
    :return: `None`
    """
    logging.info("Detected System: MacOS")
    logging.warning("MacOS net yet supported.")
    return None


if __name__ == '__main__':
    """
    The main stub, which fetches the benchmarks and then 
    shows the ratios.
    """
    # fetch and parse benchmarks
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s: %(levelname)s - %(message)s")
    fetch_benchmarks()
    get_sys_cards()