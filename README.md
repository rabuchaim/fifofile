# FiFoFile v1.0.0

A class that makes it easy to read and write lines in FiFo files (named pipes). This class was created to open a FiFo file and keep reading that file like a `tail -f`. Its use is not recommended for reading a single line.

A FiFo file does not generate I/O consumption or occupy disk space. Using a FiFo file, you can read tens of thousands of lines per second indefinitely. For sending logs to a FIFO file, we recommend using syslog-ng.

The FiFoFile class detects when syslog is restarted and automatically reopens the FiFo file, preventing the application from trying to read a file that has been closed and increasing CPU consumption.

## Installation

```
pip install fifofile
```

## Usage

Imagine a scenario where syslog-ng must send log lines to a FiFo file and you need to read those lines sent to that FiFo file.

- Create a FiFo file:
```bash
mkfifo /var/log/my_fifo_file.fifo
chmod 666 /var/log/my_fifo_file.fifo
```

- Configure syslog-ng (rsyslog or syslog) to send a copy of your application's logs directly to this fifo file.
    - syslog-ng: https://support.oneidentity.com/technical-documents/syslog-ng-open-source-edition/3.19/administration-guide/41#TOPIC-1094617
    - rsyslog: https://www.rsyslog.com/doc/configuration/modules/ompipe.html
    - syslog: https://medium.com/@mezgani/pipes-in-syslog-f10ea02a00d2

- Use the FifoFile class to read these lines in real time
```python
from fifofile import FiFoFile

fifo = FiFoFile('/var/log/my_fifo_file.fifo')
counter = 0
for line in fifo.readline():
    counter += 1
    print(line)
    if counter == 50:
        fifo.stop_reading() # is important to use this method to EXIT THE GENERATOR and CLOSE THE FIFO FILE.
        print(">>>>>>> STOPPED AS REQUESTED")
        break
```
or
```python
from fifofile import FiFoFile

with FiFoFile('/var/log/my_fifo_file.fifo') as fifo: # When you exit this block, the FiFo file is closed.
    counter = 0
    try:
        for line in fifo.readline(): # keep reading indefinitely
            print(line) # do some cool stuff with the line
    except:
        fifo.stop_reading()
```

## Methods

- **`__init__(self, fifo_file_path:str, create_if_not_exists:bool=False, create_mode:str='0o666', polling_timeout:float=1.0)`**

    Constructor method for the FiFoFile class.

    - `fifo_file_path` (str): The path to the FIFO file.
    - `create_if_not_exists` (bool, optional): If True, creates the FIFO file if it doesn't exist. Defaults to False.
    - `create_mode` (str, optional): The file mode to use when creating the FIFO file. Defaults to '0o666'.
    - `polling_timeout` (float, optional): The timeout value for polling the FIFO file. Defaults to 1.0.

- **`create_fifo_file(fifo_file_path:str, create_mode:str='0o666', raise_if_exists:bool=False) -> bool`**

    Static method to create a fifo file. You don't need to instantiate the class to use it.

    - `fifo_file_path` (str): The path to the FIFO file.
    - `create_mode` (str, optional): The file mode to use when creating the FIFO file. Defaults to '0o666'.
    - `raise_if_exists` (bool, optional): If True, raises an exception if the file already exists. Defaults to False.

- **`is_fifo_file(fifo_file_path:str) -> bool`**

    Static method to check if a file is a fifo file. You don't need to instantiate the class to use it.

    - `fifo_file_path` (str): The path to the file.

- **`stop_reading()`**

    Method to stop the reading process. Important to use this method to EXIT THE GENERATOR and CLOSE THE FIFO FILE.

- **`writeline(self, line:str, flush:bool=True)`**

    Method to write a line to the fifo file. This method opens the FiFo, writes the line, and closes the FiFo.

    - `line` (str): The line to write to the fifo file.
    - `flush` (bool, optional): If True, flushes the fifo file after writing. Defaults to True.

- **`read(self, size:int) -> Generator[Any, Any, Any]`**

    Method to read a line with a fixed size from the fifo file and return it as a generator.

    - `size` (int): The maximum number of characters to read.

- **`readline(self, strip_line:bool=True) -> Generator[str, None, None]`**

    Method to read a line (until "\n") from the fifo file and return it as a generator.

    - `strip_line` (bool, optional): If True, strips leading and trailing whitespace from the line. Defaults to True.

- **`__enter__(self)`**

    Method to support the `with` statement.

- **`__exit__(self, exc_type, exc_value, traceback)`**

    Method to support the `with` statement.


## To Do List

- Add asyncio support

## Sugestions, feedbacks, bugs...

Open an [issue](https://github.com/rabuchaim/fifofile/issues) or e-mail me: ricardoabuchaim at gmail.com
