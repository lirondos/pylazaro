# Pylazaro
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
   
#### Exteded installation
There is an extended installation option. This extended installation is needed if you want to run the CRF model for Lazaro. However, it is unlikely that you will ever need to run that model, as the CRF model is the worst performing model of all models offered through the library. The extended installation is probably only useful for research or development uses, but not for final users.

If you still wish to install the extended version, see below the commands you need to run. The last command will download a bunch of files (model and embeddings) that may take up some time and space to process: 

```
   pip install git+https://github.com/ConstantineLignos/quickvec.git
   pip install pylazaro
   python -m pylazaro extended
   ```

Bear in mind that if you wish to unistall the extended version, running `pip unistall pylazaro` will not suffice. You will also need to navigate to `pylazaro`'s library folder and remove the files associated with the extended installation (model and embeddings). 

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