# Passgen
Web service for generating location/time aware Apple Wallet passes.

## System requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/) (optional)

## Required Configuration

The following environment variables are required (except the last one):

```bash
APPLE_PRIVATE_KEY_PASSWORD
APPLE_PASS_TYPE_IDENTIFIER
APPLE_TEAM_IDENTIFIER
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_BUCKET
AWS_SECRETS_PREFIX
SKIP_DOWNLOAD_SECRETS
```

The `APPLE_*` variables can be obtained by following the guide at
[Passbook](https://github.com/devartis/passbook).

The `AWS_*` variables are required to download Apple secrets and the `api_keys.yaml`
from AWS S3. During development, you only need to download them once,
or just use local files (place them in the `./secrets` folder).
In this case just set `SKIP_DOWNLOAD_SECRETS` to any non-empty value.

The following files should exist on the AWS bucket under the configured prefix (leave empty if on root):

- `private.key`
- `certificate.pem`
- `apple-wwdrca.pem`
- `api_keys.yaml`

An example `api_keys.yaml` can be found in the root of this repo (`api_keys-example.yaml`).

## Development

### With Docker Compose

If you do not have Docker Compose installed, skip to the next section.

```bash
docker-compose up --build
```

Then navigate to http://localhost:3000.

### Build

```bash
docker build . -t passgen:1
```

### Run

```bash
docker run -it \
  -e APPLE_PRIVATE_KEY_PASSWORD=<VALUE> \
  -e APPLE_PASS_TYPE_IDENTIFIER=<VALUE> \
  -e APPLE_TEAM_IDENTIFIER=<VALUE> \
  -e SKIP_DOWNLOAD_SECRETS=1 \
  -p 3000:3000 --rm passgen:1
```

Then navigate to http://localhost:3000.

## Production

### Build

```bash
docker build . -f prod.dockerfile -t passgen:prod
```

### Run

```bash
docker run -d \
  -e APPLE_PRIVATE_KEY_PASSWORD=<VALUE> \
  -e APPLE_PASS_TYPE_IDENTIFIER=<VALUE> \
  -e APPLE_TEAM_IDENTIFIER=<VALUE> \
  -e AWS_ACCESS_KEY_ID=<VALUE> \
  -e AWS_SECRET_ACCESS_KEY=<VALUE> \
  -e AWS_BUCKET=<VALUE> \
  -p 3000:3333 -e PORT=3333 --rm passgen:prod
```

Then navigate to http://localhost:3000.

### Heroku

Basically, you need to create a heroku app, set up environment variables and set
the stack to container:

```bash
heroku stack:set container
```

Finally link your repository to heroku and set up automatic builds.
For more information please refer to the official docs
[here](https://devcenter.heroku.com/categories/deploying-with-docker).

### Docker Swarm

Assuming you have a swarm cluster:

1. Deploy the secrets

```bash
docker secret create private.key.1 /path/to/private.key
docker secret create certificate.pem.1 /path/to/certificate.pem
docker secret create apple-wwdrca.pem.1 /path/to/apple-wwdrca
docker secret create api_keys.yaml.1 /path/to/api_keys.yaml
```

2. Deploy the configs  (to override the generated passes icon)

```bash
docker config create icon.png.1 /path/to/icon.png
```

3. Deploy the stack

With the correct tag set in `docker-compose.yaml`, run the following:

```bash
docker stack deploy -c docker-compose.yaml passgen
```
