# Passgen
Web service for generating location/time aware Apple Wallet passes.

## System requirements

- [Docker](https://www.docker.com/)

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
or just use local files. In this case just set `SKIP_DOWNLOAD_SECRETS` to any non-empty value.

The following files should exist on the AWS bucket under the configured prefix (leave empty if on root):

- `private.key`
- `certificate.pem`
- `apple-wwdrca.pem`
- `api_keys.yaml`

An example `api_keys.yaml` can be found in the root of this repo (`api_keys-example.yaml`).

## Development

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
