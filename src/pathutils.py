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
    for info in os.ilistdir(dir):
        if info[1] == 0x4000:
            rmdirr(f"{dir}/{info[0]}")
        elif info[1] == 0x8000:
            os.remove(f"{dir}/{info[0]}")
    os.rmdir(dir)
