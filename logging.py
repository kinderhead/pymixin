islogging = True

def log(txt):
    if islogging:
        print("[\033[96mPyMixin\033[0m] " + txt)
