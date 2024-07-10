# evalautoapp

## Configuration

To run this project, you need to set up your API keys and other configuration settings.

1. **Copy the Example Configuration File**

   Copy the `config.example.yaml` file to `config.yaml`:

   ```sh
   cp config.example.yaml config.yaml

2. **Edit the Configuration File**

   In `config.yaml`, replace placeholder values with your actual API keys and other sensitive information.

3. **IMPORTANT: Add to .gitignore**

   Secure your information by making sure `config.yaml` is added to `.gitignore` to avoid accidentally committing your API key.

**Handle Configuration in Code**

```python
import yaml

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

config = load_config()
api_key = config.get('api_key')
