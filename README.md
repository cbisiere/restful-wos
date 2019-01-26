# restful-wos

A client for Clarivate Analytics' Web of Science RESTful API.

Currently sends requests and extracts data in RIS format.

## Quickstart:

### Installation

```bash
$ git clone git+https://github.com/ConnectedSystems/restful-wos.git
$ cd restful-wos
$ pip install -e .
```

### Usage

Firstly, put your Web of Science access tokens into a yaml file in the following format:

```yaml
restful_wos:
  wos_lite: YOUR ACCESS TOKEN FOR THE `LITE` API
  wos_expanded: YOUR ACCESS TOKEN `EXPANDED` API
```

Then simply pass in the location of the file to the RESTful client:

```python
import restful_wos

# Create client and send query
client = restful_wos.RESTClient('config.yml')
search_request = 'TS=(uncertain* AND (catchment OR watershed OR water))'
resp = client.query(search_request, time_span=('2018-11-01', '2018-12-31'))

# Convert parsed responses into RIS records
ris_data = restful_wos.to_ris_text(resp)

# Output to a txt file
restful_wos.write_file(ris_data, 'ris_output', overwrite=True)
```

