import os
import sys


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ProgressBarProgress(object):
    def __init__(self):
        self.progress = 0

    def increment(self):
        self.progress += 1

    def value(self):
        return self.progress


class DummyProgressBar(object):
    def __init__(self):
        pass

    def update_bar(self, current, max):
        pass
