# for uploading to PyPi

# To build
# python setup.py sdist bdist_wheel

# to upload
# twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

# https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf

# =============================================================================
# for running pytest coverage report
# py.test --cov-report html --cov femethods
# htmlcov\index.html
# or,
# pytest --cov-report html --cov=femethods tests\femethods\

# =============================================================================
# Creating an annotated git tag
# git tag -a v0.1.6dev -m "v0.1.6dev"

# And when pushing, tags are not automatically included. To include tags, run
# git push origin --tags

# =============================================================================
# Building documentation
# cd docs
# make html
