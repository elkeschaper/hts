.. _docs:


Docs
####

We use Sphinx to generate our docs.
The backbone of our docs are .rst files.

Our docs are on github.io (http://elkeschaper.github.io/hts/index.html)

Important hint: The code only works within the virtual environment which is installed.
Start it first by tipping into the command line:

workon hts


Generate docs: html from rst
****************************



::

    cd docs
    make html



Deploy new docs
***************


All files on the #gh-pages branch are automatically pushed to github.io
To deploy your new .html files to this branch, do::

    cd docs
    ./deploy.sh