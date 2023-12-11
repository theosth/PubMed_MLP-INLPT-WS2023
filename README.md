# PubMed_MLP-INLPT-WS2023

## Contributors

| **Username**      | **Real Name**      |
|---------------|----------------|
|  theosth       | Theo Stempel-Hauburger       |
|BenediktV | Benedikt Vidic |
|llambdaa | Lukas Rapp |
|4kills | Dominik Ochs |

## Setup project environment

### OpenSearch

For development purposes, especially for an easy installation of *OpenSearch*, we use *Docker*. 
On Windows, one can install OpenSearch directly on the system. We have not tested that, though.

On Mac, we use *Colima* together with the free-to-use, open-source Docker Engine. When installing *docker-compose* via *brew* remember to symlink it to docker as plugin. The instructions can be found on the brew page.
Furthermore you have to add the following code snippet to your Colima vm configuration (via `colima start --edit`): 
```yaml
provision:
  - mode: system
    script: sysctl -w vm.max_map_count=262144
```  

On Windows we can recommend using the Docker Engine directly via *WSL2*. You'll likely have to 
add `vm.max_map_count = 262144` to the `/etc/sysctl.conf` of your WSL2 installation to persist the change, 
as well as `sysctl -w vm.max_map_count=262144` to make the initial change. However, we have not tested this, and it might not be necessary.

For Windows or Mac, one can also use *Docker Desktop* (free for educational use). 

After installation of Docker and Docker Compose, simply use `docker compose up` in the base directory. 

### Python

1. Setup a venv with python
```bash
python -m venv .venv
```

2. Activate venv
```bash
source .venv/bin/activate
```

3. Install requirements from requirements.txt
```bash
pip install -r requirements.txt
```

4. Create a .env.loacl file in the root directory and add the following variables
```env
HF_TOKEN=YOUR_HUGGINGFACE_API_TOKEN
```

## Run project
```bash
./run.sh
```
