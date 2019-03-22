# Manual Dataset tagger

This is a small Flask application with the simple purpose of tagging some text data in order to use them further away to train models.

It is at the moment a pretty simple application only working for binary classification.

## Data sources

It assumes that you feed it either:
  - A jsonline file in which each object has a `text` field
  - A csv file with a `text_content` column

The mandatory fileds are the one containing the text you want to classify.

## Dependencies

If you wish to use this app, you should at least have:
  - Python > 3.5
  - virtualenv (https://virtualenv.pypa.io/en/latest/)


## How to use

Simply clone this repository and run:
```
make virtualenv

source build/virtualenv/bin/activate
make all
```

This will run a development server you can use. Deployement on  production servers is not yet supported.


