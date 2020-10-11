<p align="center">
  <img src="https://github.com/pblottiere/littodyn/blob/master/logo.png" height="128"/>
</p>

### Installation

Installation from sources on GNU/Linux for the `default` profile:

```` bash
$ cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
$ git clone https://github.com/pblottiere/littodyn
````

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

To run a simple PCA test:

```` bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ PYTHONPATH=$(pwd) python tests/test_pca.py
````

The resulting image is `tests/pca.tif`.
