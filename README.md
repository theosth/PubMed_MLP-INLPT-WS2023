# PubMed_MLP-INLPT-WS2023

## Contributors

| **Username**      | **Real Name**      |
|---------------|----------------|
|  theosth       | Theo Stempel-Hauburger       |
|BenediktV | Benedikt Vidic |
|llambdaa | Lukas Rapp |
|4kills | Dominik Ochs |

## Setup project environment

### Ollama

Install Ollama for your OS following the instructions at https://ollama.com/. 
We STRONGLY recommend using some kind of acceleration. It is also best to run it WITHOUT docker. 
Tested on MacOS and Ubunutu. 

### OpenSearch

On Windows, one can install OpenSearch directly on the system. Keep in mind that this somewhat complicates the insertion of 
the OpenSearch volume found under `data/opensearch`. We have not tested running it bare-bones on Windows.

#### Docker

For development purposes, especially for an easy installation of *OpenSearch*, we use *Docker*. 

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

#### Index

To skip the tedious and long process of ingesting and embedding the documents yourself, you can use our pre-packaged OpenSearch index.
To do that, create the folder `data/opensearch` and unpack our `opensearch-index.zip` into that folder. You can find `opensearch-index.zip`
in our Github release. After unpacking, check if `data/opensearch/nodes` along with other files exists. 

The structure of the data folder should look something like this:
```
data
└── opensearch
    ├── ml_cache
    │   ├── cache
    │   ├── models_cache
    │   ├── pytorch
    │   └── tokenizers
    └── nodes
        └── 0
```

If you, however, want to ingest the data yourself using `ingestor.py` (takes 3-6 hours), you can do so by just creating `data/opensearch`
and leaving it empty.

In any case, use  `docker compose up` in the base directory to start OpenSearch. 

If you used the pre-packaged index, it's still necessary to enable the model backupped in `data/opensearch` by running the following command after OpenSearch has started:
```bash
curl -XPOST "http://localhost:9200/_plugins/_ml/models/0x9sgowBKAf_E-Dqahic/_deploy"
```
or with the following command though the OpenSearch dev-tools console:
```
POST /_plugins/_ml/models/0x9sgowBKAf_E-Dqahic/_deploy
```

Now, if you want to use the hybrid search functionality, you have to run the following command to create the hybrid search pipeline after OpenSearch has started:
```bash
curl -XPUT "http://localhost:9200/_search/pipeline/basic-nlp-search-pipeline" -H 'Content-Type: application/json' -d'
{
  "description": "Post processor for hybrid search",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [
              0.3,
              0.7
            ]
          }
        }
      }
    }
  ]
}'
```

or with the following command though the OpenSearch dev-tools console:
```
PUT /_search/pipeline/basic-nlp-search-pipeline
{
  "description": "Post processor for hybrid search",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [
              0.3,
              0.7
            ]
          }
        }
      }
    }
  ]
}
```

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

4. Create a .env.local file in the root directory and add the following variables
```env
HF_TOKEN=YOUR_HUGGINGFACE_API_TOKEN
```

### Settings

If necessary (for example to adjust your OpenSearch credentials), edit `commons/env.py`. However, if you have set up the project using docker,
this should not be necessary and the defaults in `commons/env.py` should work for you. 

## Run project
```bash
./run.sh
```

## Troubleshooting
- If your machine learning model is not responding (see dashboard http://localhost:5601/app/ml-commons-dashboards/overview) try:
    - `POST /_plugins/_ml/models/<MODEL_ID>/_deploy` in the development console in the dashboard. If that doesn't work (error in returned task: model content changed)
    - Delete the model with `DELETE /_plugins/_ml/models/<MODEL_ID>` and run `set_up_embedding_model()` of `ingestor.py`. Be careful not to recreate the index! Preferably, open a python interpreter with the `python` command and `from ingestor import set_up_embedding_model` followed by `set_up_embedding_model()`