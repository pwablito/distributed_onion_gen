# Distributed TOR Vanity Onion Generator

## Components
- Master: The centralized location where generated onions are sent and new onions can be requested. Hosted as a TOR hidden service.
- Worker: Workers that run `mkp224o` to search for matching onions to send back to the master server.

## Setup
- Generate an onion for the master server using `mkp224o`.
- Add variables to `.env` (see descriptions further down):
    - MASTER_ONION
    - ADMIN_TOKEN
- Run one instance of the master node: `docker compose -f master.yml up -d`.
    - This can be run anywhere
    - The `onions` directory will contain onion configurations found by the workers.
    - The `$MASTER_ONION` environment variable points to the directory with server onion configuration (i.e. abc123abc123abc123.onion).
    - The `$ADMIN_TOKEN` environment variable contains the token for configuring the system using the index page on the browser.
- Run as many instances of the worker as desired, on as many machines as desired: `docker compose -f worker.yml`.
    - Configure the number of replicas on each node to the number of CPUs you'd like to use in `worker.yml`.
    - The `$MASTER_ONION` environment variable points to the master hidden service (i.e. abc123abc123abc123.onion).
- Access `http://{$MASTER_ONION}/` in a TOR browser, enter the token and a comma-separated filter list of domains to look for.
