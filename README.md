# Pylazaro
A library for lexical borrowing detection (a.k.a loanwords) in Spanish.

### Installation
```
   pip install git+https://github.com/ConstantineLignos/quickvec.git
   pip install pylazaro
   python -m pylazaro download 
   ```

### Get started
A working example on how to detect borrowings in a text using ```pylazaro```:

```
>>> from pylazaro import Lazaro

# We create our borrowing detection tagger
>>> tagger = Lazaro()

# The text we want to analyze for borrowing detection
>>> text = "Inteligencia artificial aplicada al sector del digital health, la e-mobility, las smarts grids entre otros; favoreciendo las interacciones colaborativas."

# We run our tagger on the text we want to analyze
>>> result = tagger.analyze(text)

# We get results
>>> result.get_borrowings()
[('digital health', 'ENG'), ('e-mobility', 'ENG'), ('smarts grids', 'ENG')]
```