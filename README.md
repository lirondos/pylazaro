# pylazaro
A library for lexical borrowing detection (a.k.a loanwords) in Spanish, with a focus on anglicism detection.

### Installation
To install `pylazaro` simply run the following command from the command line: 

```
   pip install pylazaro
   ```

To uninstall `pylazaro` simply run the following command from the command line:    
```
   pip uninstall pylazaro
   ```

### Get started
A working example on how to detect borrowings in a text using `pylazaro`:

```
>>> from pylazaro import Lazaro

# We create our borrowing detection tagger
>>> tagger = Lazaro()

# The text we want to analyze for borrowing detection
>>> text = "Inteligencia artificial aplicada al sector del blockchain, la e-mobility y las smarts grids entre otros; favoreciendo las interacciones colaborativas."

# We run our tagger on the text we want to analyze
>>> result = tagger.analyze(text)

# We get results
>>> result.borrowings()
[('blockchain', 'ENG'), ('e-mobility', 'ENG'), ('smarts grids', 'ENG')]

>>> result.tag_per_token()
[('Inteligencia', 'O'), ('artificial', 'O'), ('aplicada', 'O'), ('al', 'O'), ('sector', 'O'), ('del', 'O'), ('blockchain', 'B-ENG'), (',', 'O'), ('la', 'O'), ('e-mobility', 'B-ENG'), ('y', 'O'), ('las', 'O'), ('smarts', 'B-ENG'), ('grids', 'I-ENG'), ('entre', 'O'), ('otros', 'O'), (';', 'O'), ('favoreciendo', 'O'), ('las', 'O'), ('interacciones', 'O'), ('colaborativas', 'O'), ('.', 'O')]
```

### More info 
* Documentation on how to use `pylazaro` in [Read the docs](https://pylazaro.readthedocs.io/).
* The code is available on [GitHub](https://github.com/lirondos/pylazaro).
* `pylazaro` gives access to the models described on [this ACL paper](https://aclanthology.org/2022.acl-long.268/)
* Questions? Bugs? Requests? Ideas? Feel free to reach me [via email](mailto:ealvarezmellado@gmail.com), open [a GitHub issue](https://github.com/lirondos/pylazaro/issues) or ping me [on Twitter](https://twitter.com/lirondos).