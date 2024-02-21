<!-- htop for monitoring -->
sudo apt install htop
<!-- Git -->
sudo apt install git
<!-- curl -->
sudo apt  install curl
<!-- ollama -->
mkdir -p ~/Documents/ollama
cd ~/Documents/ollama && curl -fsSL https://ollama.com/install.sh | sh
<!-- install docker with the docker-convencience script-->
curl -fsSL https://get.docker.com -o get-docker.sh
<!-- install docker for rootless users -->
sudo apt-get install -y uidmap && cd /usr/bin && dockerd-rootless-setuptool.sh install
<!-- append docker stuff to .bashrc -->
echo 'export PATH=/usr/bin:$PATH' >> ~/.bashrc
echo 'export DOCKER_HOST=unix:///run/user/1000/docker.sock' >> ~/.bashrc
<!-- install python venv -->
sudo apt install python3.11-venv
<!-- Opensearch install instructions: https://opensearch.org/docs/latest/install-and-configure/install-opensearch/index/  -->
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
sudo apt-get update && sudo apt-get -y install lsb-release ca-certificates curl gnupg2
curl -o- https://artifacts.opensearch.org/publickeys/opensearch.pgp | sudo gpg --dearmor --batch --yes -o /usr/share/keyrings/opensearch-keyring
echo "deb [signed-by=/usr/share/keyrings/opensearch-keyring] https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/apt stable main" | sudo tee /etc/apt/sources.list.d/opensearch-2.x.list
sudo apt-get update
sudo apt-get install opensearch
sudo systemctl daemon-reload
sudo systemctl enable opensearch.service
sudo systemctl start opensearch.service
<!-- Opensearch Dashboard install -->
echo "deb [signed-by=/usr/share/keyrings/opensearch-keyring] https://artifacts.opensearch.org/releases/bundle/opensearch-dashboards/2.x/apt stable main" | sudo tee /etc/apt/sources.list.d/opensearch-dashboards-2.x.list
sudo apt-get update
sudo apt-get install opensearch-dashboards
sudo systemctl daemon-reload
sudo systemctl enable opensearch-dashboards.service
sudo systemctl start opensearch-dashboards.service



<!-- !! Dont use this yet, currently not working... -->

<!-- Get GPU-Support inside Docker-Containers: install NVIDIA Container Toolkit source: https://hub.docker.com/r/ollama/ollama -->
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
<!-- also configure for roootless mode -->
nvidia-ctk runtime configure --runtime=docker --config=$HOME/.config/docker/daemon.json
<!-- sudo systemctl --user restart docker -->
sudo nvidia-ctk config --set nvidia-container-cli.no-cgroups --in-place
<!-- install ubuntu dev tools (installs tools like GCC, g++, make ...) -->
sudo apt install build-essential 
<!-- install nvidia drivers source: https://ubuntu.com/server/docs/nvidia-drivers-installation-->
sudo ubuntu-drivers install --gpgpu
<!-- for me i chose: -->
sudo ubuntu-drivers install --gpgpu nvidia:535-server
sudo apt install nvidia-utils-535-server


<!-- just temporary for docker testing: -->

<!-- disable  opensearch and ollama services-->
sudo systemctl stop opensearch.service
sudo systemctl stop opensearch-dashboards.service
sudo systemctl stop ollama.service

<!-- start opensearch and ollama services -->
sudo systemctl start opensearch.service
sudo systemctl start opensearch-dashboards.service
sudo systemctl start ollama.service





