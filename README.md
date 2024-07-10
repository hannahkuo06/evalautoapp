# evalautoapp

## Configuration

To run this project, you need to set up your API keys and other configuration settings.

1. **Copy the Example Configuration File**

   Copy the `config.example.yaml` file to `config.yaml`:

   ```sh
   cp config.example.yaml config.yaml

In your code, load the configuration from the appropriate file and handle the settings accordingly.

**Handle Configuration in Code**

**Example using YAML**:

```python
import yaml

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

config = load_config()
api_key = config.get('api_key')
database_url = config.get('database_url')
