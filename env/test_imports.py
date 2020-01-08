from importlib import import_module

# Tests that all required packages can be imported
failed = []

libs = ['pandas',
        'geopandas',
        'osmnx',
        'urbanaccess',
        'ua2nx',
        'igraph',
        'networkx',
        ]

for lib in libs:
    try:
        import_module(lib)
    except ImportError:
        failed.append(lib)

if len(failed) == 0:
    print("All required packages were successfully installed.")
else:
    print("ERROR: Could not import following libraries:", failed)

