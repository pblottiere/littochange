# LittoDyn


#### Installation

Installation from sources on GNU/Linux for the `default` profile:

```` bash
$ cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
$ git clone https://github.com/pblottiere/littodyn
````

Then:

- restart QGIS
- activate the plugin


#### Test

To run a simple PCA test:

```` bash
$ PYTHONPATH=$(pwd) python tests/test_pca.py
````
