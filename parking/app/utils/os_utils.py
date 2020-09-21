import os


def path_join(path_list):
    return os.path.join(*path_list)


def next_path(path_pattern):
    i = 1
    while os.path.exists(path_pattern+"/%s" % i):
        i += 1
    return i


def create_dir(path_):
    if not os.path.isdir(path_):
        os.makedirs(path_)
