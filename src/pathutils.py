import os


def ensure_dirs(path, offset=0):
    """
    Ensure that all directories in a path exist.
    """
    dirs = path.split("/")
    if path[0] == "/":
        del dirs[0]
        dirs[0] = "/" + dirs[0]

    for idx in range(len(dirs) - offset):
        test = "/".join(dirs[0 : idx + 1])
        try:
            os.listdir(test)
        except:
            os.mkdir(test)


def ensure_parent_dirs(path):
    ensure_dirs(path, 1)


def rmdirr(dir):
    """
    Recursively remove directory.
    Will delete everything inside.
    """
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    os.rmdir(dir)
