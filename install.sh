#!/bin/sh
BOTDIR=$(dirname $0)
# Check if virtualenv exists
if [ -f $BOTDIR/bin/python ]
then
    echo "Virtualenv exists."
else
    # Create it, if it doesn't
    echo "Virtualenv doesn't exist, creating it."
    virtualenv --no-site-packages $BOTDIR
    # Install pyyaml to enable reading .travis.yml
    $BOTDIR/bin/pip install pyyaml
fi

$BOTDIR/bin/python $BOTDIR/pyfibot/util/setup.py $BOTDIR
