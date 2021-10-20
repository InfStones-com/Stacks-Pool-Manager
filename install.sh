#!/bin/bash

function install_package() {

    sudo apt-get update -y

    # install python3
    if [ -z "$(which python3)" ]; then
        sudo apt install python3
    fi

    ### Download and install nvm ######
    wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
    source $HOME/.nvm/nvm.sh

    ### install # Node.js ia nvm #######
    FILE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

    cd $FILE_PATH
    nvm install node
    sudo apt install npm -y
    npm install rimraf
    npm install swagger-cli
    echo -e "\e[1;32m[INFO]: Required packages have been installed on $(hostname) at $(date +%T) on $(date +%Y-%m-%d)\e[0m"

    # install jq
    if [ "$(which jq)X" == "X" ]; then
        sudo apt-get install -y jq
    fi

    #install docker with official docker install script
    if [ "$(which docker)X" == "X" ]; then
        sudo wget -qO- https://get.docker.com/ | sh
        sudo systemctl enable docker
        sudo usermod -aG docker ubuntu
        echo -e "\e[1;32m$(date +%Y-%m-%d_%H:%M:%S) [End]: Docker installed successfully... \e[0m"
    fi

    # Install docker-compose
    if [ "$(which docker-compose)X" == "X" ]; then
        echo -e "\e[1;32m$(date +%Y-%m-%d_%H:%M:%S) [Begin]: Installing docker-compose... \e[0m"
        DOCKER_COMPOSE_VERSION=$(git ls-remote https://github.com/docker/compose | grep refs/tags | grep -oE "[0-9]+\.[0-9][0-9]+\.[0-9]+$" | sort --version-sort | tail -n 1)
        sudo sh -c "curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m) > /usr/local/bin/docker-compose"
        sudo chmod +x /usr/local/bin/docker-compose
        sudo sh -c "curl -L https://raw.githubusercontent.com/docker/compose/${DOCKER_COMPOSE_VERSION}/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose"
        echo -e "\e[1;32m$(date +%Y-%m-%d_%H:%M:%S) [Begin]: Docker-compose installed successfully... \e[0m"
    fi

    # Install package.json
    echo -e "\e[1;32m[INFO]: Installing package.json\e[0m"
    npm install
    echo 'export NODE_OPTIONS=--openssl-legacy-provider' >> $HOME/.bashrc
    source $HOME/.bashrc

}

install_package
