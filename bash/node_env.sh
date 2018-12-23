#!/bin/bash

# GitHub: https://github.com/creationix/nvm/blob/master/README.md
# install nvm
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
source ~/.bashrc

# install node
nvm install node

# use node
nvm use node