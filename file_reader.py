# You need to implement the "get" and "head" functions.
import os
class FileReader:
    def __init__(self):
        pass

    def get(self, filepath, cookies):
        """
        Returns a binary string of the file contents, or None.
        """
        # if os.path.isdir(filepath):
        #     os.chdir(filepath)
        if os.path.isdir(filepath):
            #print("IsADirectoryError")
            return "<html><body><h1>{:}</h1></body></html>".format(filepath).encode()
        elif os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return f.read()
        else:
            return None

    def head(self, filepath, cookies):
        """
        Returns the size to be returned, or None.
        """
        if os.path.isdir(filepath):
            #print("IsADirectoryError")
            return len("<html><body><h1>{:}</h1></body></html>".format(filepath))
        elif os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return len(f.read())
        else:
            return None
