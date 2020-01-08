# Install Python packages

During this workshop we will use various Python packages that you should install before starting to go through the codes.

## Installation on Windows

Create Python environment for the packages by running from command prompt (possibly with admin rights):

```
$ cd C:\..\routing-workshop\env
$ conda env create -f routing_windows.yml
$ conda activate routing
$ pip install python_igraph-0.7.1.post6-cp37-cp37m-win_amd64.whl
```

## Installation on Unix-systems

```
$ cd /home/.../routing-workshop/env
$ conda env create -f routing_unix.yml

```

## Test that the installations were successful

Note: This should be run with the activated environment (i.e. `routing`).
```
$ python test_imports.py
```

You should receive text `"All required packages were successfully installed."` if the installations were successful. 
