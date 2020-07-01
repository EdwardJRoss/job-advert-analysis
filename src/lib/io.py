import typing
import pathlib
import os

pathlike = typing.Union[str, pathlib.Path]


# Compare with https://github.com/python/cpython/blob/master/Lib/tempfile.py
class AtomicFileWriter:
    """Writes a file to filename only on successful completion"""
    def __init__(self, filename: pathlike, mode:str='w+b', temp_filename: typing.Optional[pathlike]= None):
        self.filename = filename
        self.mode = mode
        if temp_filename is None:
            self.temp_filename = str(filename) + '.tmp'
        else:
            self.temp_filename = temp_filename

    def __enter__(self):
        self.filehandle = open(self.temp_filename, self.mode)
        return self.filehandle

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            self.filehandle.close()
            os.replace(self.temp_filename, self.filename)
        else:
            try:
                self.filehandle.close()
            finally:
                os.unlink(self.temp_filename)
