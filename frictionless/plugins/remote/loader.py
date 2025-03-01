import io
import requests.utils
from ...loader import Loader


class RemoteLoader(Loader):
    """Remote loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.remote import RemoteLoader`

    """

    remote = True

    # Read

    def read_byte_stream_create(self):
        fullpath = requests.utils.requote_uri(self.resource.fullpath)
        session = self.resource.control.http_session
        timeout = self.resource.control.http_timeout
        byte_stream = RemoteByteStream(fullpath, session=session, timeout=timeout).open()
        if self.resource.control.http_preload:
            buffer = io.BufferedRandom(io.BytesIO())
            buffer.write(byte_stream.read())
            buffer.seek(0)
            byte_stream = buffer
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        file = f"{self.resource.name}.{self.resource.format}"
        url = self.resource.fullpath.replace(file, "")
        response = self.resource.control.http_session.post(url, files={file: byte_stream})
        response.raise_for_status()
        return response


# Internal


class RemoteByteStream:
    def __init__(self, source, *, session, timeout):
        self.__source = source
        self.__session = session
        self.__timeout = timeout

    def __iter__(self):
        while True:
            bytes = self.read(8192)
            if not bytes:
                break
            yield from bytes.splitlines(keepends=True)

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return True

    @property
    def closed(self):
        return self.__closed

    def open(self):
        self.__closed = False
        self.seek(0)
        return self

    def close(self):
        self.__closed = True

    def tell(self):
        return self.__response.raw.tell()

    def flush(self):
        pass

    def read(self, size=-1):
        if size == -1:
            size = None
        return self.__response.raw.read(size)

    def read1(self, size=-1):
        return self.read(size)

    def seek(self, offset, whence=0):
        assert offset == 0
        assert whence == 0
        self.__response = self.__session.get(
            self.__source, stream=True, timeout=self.__timeout
        )
        self.__response.raise_for_status()
        self.__response.raw.decode_content = True
