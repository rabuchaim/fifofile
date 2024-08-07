#!/usr/bin/env python3
"""FiFoFile v1.0.0 - A class that makes it easy to read and write lines in fifo files (named pipes)"""
"""
 ______ _ ______    ______ _ _
|  ____(_)  ____|  |  ____(_) |
| |__   _| |__ ___ | |__   _| | ___
|  __| | |  __/ _ \|  __| | | |/ _ \
| |    | | | | (_) | |    | | |  __/
|_|    |_|_|  \___/|_|    |_|_|\___|

  Author.: Ricardo Abuchaim - ricardoabuchaim@gmail.com
  Github.: https://github.com/rabuchaim/fifofile
"""

__all__ = ['FiFoFile']

import os, stat, select, threading, time
from typing import Generator

class FiFoFileError(Exception):
    def __init__ (self, message):
        self.message = '\033[38;2;255;99;71m'+str(message)+'\033[0m'
        super().__init__(self.message)
    def __str__(self):
        return self.message
    def __repr__(self):
        return self.message

class FiFoFile():
    __appname__ = 'FiFoFile'
    __version__ = "1.0.0"
    def __init__(self, fifo_file_path:str, create_if_not_exists:bool=False, create_mode:str='0o666', polling_timeout:float=1.0):
        """
        A class that makes it easy to read and write lines in fifo files (named pipes). 
        
        Args:
            - fifo_file_path (str): The path to the FIFO file.
            - create_if_not_exists (bool, optional): If True, creates the FIFO file if it doesn't exist. Defaults to False.
            - create_mode (str, optional): The file mode to use when creating the FIFO file. Defaults to '0o666'.
            - polling_timeout (float, optional): The timeout value for polling the FIFO file. Defaults to 1.0.
        
        Usage example 1:

            ```
            fifo = FiFoFile('my_fifo_file.fifo')
            counter = 0
            for line in fifo.readline():
                counter += 1
                print(line)
                if counter == 50:
                    fifo.stop_reading()
                    print(">>>>>>> STOPPED AS REQUESTED")
                    break
            ```
        Usage example 2:
            ```
            with FiFoFile('my_fifo_file.fifo') as fifo:
                for line in fifo.readline():
                    print(line)
            ```
        """
        self.__stop_event = threading.Event()
        self.fifo_file_path = fifo_file_path
        self.polling_timeout = polling_timeout
        try:
            stat.S_ISFIFO(os.stat(self.fifo_file_path).st_mode)
        except Exception as ERR:
            if not create_if_not_exists:
                raise FiFoFileError(f"File '{self.fifo_file_path}' is not a valid fifo file.")
            else:
                try:
                    int(create_mode, 8)
                except:
                    raise FiFoFileError(f"Invalid create mode '{create_mode}' - Must be an octal number like '0o666', '0o664', '0o644'...")
                os.mkfifo(self.fifo_file_path)
                os.chmod(self.fifo_file_path, int(create_mode, 8))
        
    @staticmethod
    def create_fifo_file(fifo_file_path:str, create_mode:str='0o666', raise_if_exists:bool=False):
        """Create a fifo file. Is a static method, you don't need to instantiate the class to use it.
        
        Usage:
            
            ```
            if FiFoFile.create_fifo_file('/var/log/my_syslog.fifo', create_mode='0o600', raise_if_exists=False):
                print('Fifo file created')
            else:
                print('Failed to create the fifo file')
            ```
        """
        try:
            int(create_mode, 8)
        except:
            raise FiFoFileError(f"Invalid create mode '{create_mode}' - Must be an octal number like '0o666', '0o664', '0o644'...")
        
        if raise_if_exists and os.path.exists(fifo_file_path):
            raise FiFoFileError(f"File '{fifo_file_path}' already exists")
        elif os.path.exists(fifo_file_path):
            return False
        
        try:
            os.mkfifo(fifo_file_path)
            os.chmod(fifo_file_path, int(create_mode, 8))
            return True
        except Exception as ERR:
            raise FiFoFileError(f"Failed to create fifo file '{fifo_file_path}' {str(ERR)}")
            
    def __enter__(self):
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.stop_reading() 
            self.__fifo.close()
        except:
            pass
        finally:
            print("CLOSED")
        
    @staticmethod
    def is_fifo_file(fifo_file_path:str)->bool:
        """Check if a file is a fifo file. Is a static method, you don't need to instantiate the class to use it.
        
        Usage:
        
            ```
            if FiFoFile.is_fifo_file('/var/log/my_syslog.fifo'):
                print('It is a fifo file')
            else:
                print('It is NOT a fifo file')
            ```
        """
        try:
            stat.S_ISFIFO(os.stat(fifo_file_path).st_mode)
        except:
            return False
        return True
    
    def stop_reading(self):
        """Stop the reading process"""
        self.__stop_event.set()
        
    def _open_fifo(self, fifo_file_path:str, mode:str='r'):
        """Open a fifo file and returns the file descriptor"""
        try:
            self.__fifo = open(fifo_file_path, mode)
        except Exception as ERR:
            raise FiFoFileError(f"Error opening fifo file '{fifo_file_path}' - {ERR}") from None
        return self.__fifo
    
    def writeline(self, line:str, flush:bool=True):
        """Write a line to the fifo file"""
        FIFO = self._open_fifo(self.fifo_file_path, 'w')
        try:
            FIFO.write(line)
            if flush:
                FIFO.flush()
        except Exception as ERR:
            raise FiFoFileError(f"Error writing to fifo file '{self.fifo_file_path}' - {ERR}") from None
        finally:
            FIFO.close()
            
    def read(self,size:int)->Generator[str, None, None]:
        """Read a line from the fifo file and returns as a generator"""
        FIFO = self._open_fifo(self.fifo_file_path, 'r')
        poller = select.epoll()
        read_only = select.EPOLLIN | select.EPOLLPRI | select.EPOLLHUP | select.EPOLLERR | select.EPOLLMSG 
        poller.register(FIFO.fileno(),read_only)
        while True:
            events = poller.poll(self.polling_timeout)
            for fd, event in events:
                if event & (select.EPOLLIN | select.EPOLLPRI):
                    if self.__stop_event.is_set():
                        try:
                            poller.unregister(FIFO.fileno())
                        finally:
                            FIFO.close()
                            return
                    try:
                        fifo_line = FIFO.read(size)
                        if not fifo_line:
                            continue
                        yield fifo_line
                    except:
                        continue
                elif event & select.EPOLLHUP:
                    # It is necessary to monitor this event if syslog/rsyslog/syslog-ng is restarted
                    # The application may consume a lot of CPU if it does not reopen the file again.
                    poller.unregister(FIFO.fileno())
                    FIFO.close()
                    FIFO = False
                    while FIFO is False:
                        try:
                            FIFO = self._open_fifo(self.fifo_file_path, 'r')
                            poller.register(FIFO.fileno(),read_only)
                        except Exception as ERR:
                            time.sleep(1)
    
    def readline(self,strip_line:bool=True)->Generator[str, None, None]:
        """Read a line from the fifo file and returns as a generator"""
        def read_line_stripped(fifo_line):
            return fifo_line.strip()
        def read_line(fifo_line):
            return fifo_line
        FIFO = self._open_fifo(self.fifo_file_path, 'r')
        poller = select.epoll()
        read_only = select.EPOLLIN | select.EPOLLPRI | select.EPOLLHUP | select.EPOLLERR | select.EPOLLMSG 
        poller.register(FIFO.fileno(),read_only)
        if strip_line:
            read_line = read_line_stripped
        while True:
            events = poller.poll(self.polling_timeout)
            for fd, event in events:
                if event & (select.EPOLLIN | select.EPOLLPRI):
                    if self.__stop_event.is_set():
                        try:
                            poller.unregister(FIFO.fileno())
                        finally:
                            FIFO.close()
                            return
                    try:
                        fifo_line = FIFO.readline()
                        if not fifo_line:
                            continue
                        yield read_line(fifo_line)
                    except:
                        continue
                elif event & select.EPOLLHUP:
                    # It is necessary to monitor this event if syslog/rsyslog/syslog-ng is restarted
                    # The application may consume a lot of CPU if it does not reopen the file again.
                    poller.unregister(FIFO.fileno())
                    FIFO.close()
                    FIFO = False
                    while FIFO is False:
                        try:
                            FIFO = self._open_fifo(self.fifo_file_path, 'r')
                            poller.register(FIFO.fileno(),read_only)
                        except Exception as ERR:
                            time.sleep(1)
        
# if __name__ == '__main__':
#     fifo = FiFoFile('/var/log/a_valid_fifo.fifo')
#     counter = 0
#     for line in fifo.readline():
#         counter += 1
#         print(line)
#         if counter == 50:
#             fifo.stop_reading()
#             print(">>>>>>> STOPPED AS REQUESTED")
#             break

#     with FiFoFile('/var/log/a_valid_fifo.fifo') as fifo:
#         counter = 0
#         for line in fifo.readline():
#             counter += 1
#             print(line)
#             if counter == 50:
#                 fifo.stop_reading()
#                 break
#     print(">>>>>>> STOPPED AS REQUESTED")
    
