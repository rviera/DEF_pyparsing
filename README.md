# DEF (Design Exchange Format) parser with PyParsing

DEF (Design Exchange Format) parser with PyParsing. It's quite slow so far. It takes around 3min to parse the complete example_2.def file.


## Usage

```python
import DefParser

# For now, you must define a list of .def files 
# to parse inside the class DefParser (self.def_files)

def_parser = DefParser()
def_parser.run()

# or run directly:

python3 parser_def_1.py

# python3 parser_def_1.py  # with global variables
# python3 parser_def_2.py  # variables inside each class
# python3 parser_def_3.py  # without multiprocessing
```
To parse the whole file set the following to False:
self.ignore_pins = False
self.ignore_specialnets = False
self.ignore_nets = False

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
