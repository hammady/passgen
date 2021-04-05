# Passgen
Web service for generating location/time aware Apple Wallet passes.

## System requirements

- [Docker](https://www.docker.com/)
- Apple stuff, check [Passbook](https://github.com/devartis/passbook).

## Build

```bash
docker build . -t passgen:1
```

## Run

```bash
docker run -it --rm passgen:1
```
