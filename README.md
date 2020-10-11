<p align="center">
  <img src="https://github.com/pblottiere/littodyn/blob/master/logo.png" height="128"/>
</p>

### Installation

#### Windows

You can download the zip file on `https://github.com/pblottiere/littodyn`. Then
you have to unzip the directory in
`C:\Users\Login\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins` and
prepare the directory to look like:

- plugins\littodyn\README.md
- plugins\littodyn\metadata.txt
- plugins\littodyn\src
- ...

#### GNU/Linux

Installation from sources on GNU/Linux for the `default` profile:

```` bash
$ cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
$ git clone https://github.com/pblottiere/littodyn
````

#### Dependencies

Some Python dependencies are necessary:

- numpy
- scipy
- gdal
- scikit-learn

Note that on Windows, missing dependencies are installed when LittoDyn plugin
is activated the first time. QGIS have to be restarted in this case.

Then:

- restart QGIS
- activate the plugin


### Test

To run algorithms on test data:

```` bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ PYTHONPATH=$(pwd) python tests/test_algs.py
````
