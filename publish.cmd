python -m pip install -U twine
python setup.py sdist bdist_wheel
twine upload dist/*
