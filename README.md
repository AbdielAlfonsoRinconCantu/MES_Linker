# MES_Linker

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)

TCP/IP server template for industrial MES w/ GUI

<img width="1830" height="1080" alt="MES_Linker" src="https://github.com/user-attachments/assets/78e35a26-d067-42d2-9ad4-dad8badf8d80" />

## Table of contents

1. [Overview](#overview)


## Overview

A python-based socket TCP/IP GUI for connecting two clients, every message `Device_1` receives will be forwarded to `MES Socket`, this app is meant as an open-source fast-template for creating local MES apps to route communications between various devices and a database (`MES Socket`).


## Installation

### Using .exe
Download `MES_Linker.exe`.

### Using Python
Make sure the following is installed:
- [python](https://www.python.org/downloads/)

- [py-window-styles](https://github.com/Akascape/py-window-styles)

- [Sun-Valley-ttk-theme](https://github.com/rdbende/Sun-Valley-ttk-theme)

On a terminal:
```bash
pip install sv-ttk pywinstyles
git clone https://github.com/AbdielAlfonsoRinconCantu/MES_Linker.git
```

## Usage
### Using .exe
Double-click `MES_Linker.exe`.


### Using Python
On a terminal:
```bash
cd ~/MES_Linker
python MES_Linker.py
```


## Developer's guide

This app is meant to be a template, here is how you can adapt the code to fit your use case:

### Adding a new connection:

In `# Queues`, add:
```python
<your_socket>_Queue = queue.Queue()
```

In `Start_socket_threads()`, add:
```python
threading.Thread(target=build_a_socket, args=(<your_socket>_Socket_button,
    "<your_socket>", <your_socket>_Socket_Host, <your_socket>_Socket_Port, <your_socket>_Queue)).start()
```

In `Change_addresses_button_Function()`, add:
```python
targets = [
    ...

    ('<your_socket>', <your_socket>_text_box),

    ...
]

...

<your_socket>_Label = ...
<your_socket>_Label.grid(...)
<your_socket>_text_box = ...
<your_socket>_text_box.grid(...)
<your_socket>_text_box.insert(...)
```

In `Main_screen_Header_frame`, add:
```python
<your_socket>_button = ...
<your_socket>_Socket_button.pack(...)
```

### Handling new messages:

In `received_message_interpreter()`, add:
```python
match server_name:
...
    case "<your_socket>":
        # write your logic here
...
```


### Adding new persistent variables:

In `MES_Linker_Settings_Load()`, add:
```python
defaults = { ..., "<your_variable>": <your_default_value>, ...}

...

<your_variable> = MES_Linker_Settings_Load()["<your_variable>"]
```

In `MES_Linker_Settings_Save()` add:
```python
data = { ... "<your_variable>": <your_variable>, ... }

<your_variable> = <your_variable>_text_box.get().strip()
```

In `Change_station_button_Function()` add:
```python
<your_variable>_Label = ...
<your_variable>_Label.grid(...)
<your_variable>_text_box = ...
<your_variable>_text_box.insert(...)
```
