# pubwatch

First-line monitoring of Orcfax expired publications.

## Environment

The script requires a number of environment variables to be set.

```env
export ORCFAX_VALIDATOR=
export KUPO_URL=
export FSP_POLICY=
export VALIDITY_TOKEN=
```

## Connecting

pubwatch will need to connec to `ssl` in production. If the monitor
is being used locally, a `--local` flag can be used.

pubwatch needs a list of CER feeds available from [cer-feeds][cer-feeds-1].

Other command line arguments can be viewed using `--help`.

## Running

The script can be run from the repository, e.g.:

```sh
python pubwatch.py --help
```

or once installed via the package with:

```sh
pubwatch --help
```

## Cron

Pubwatch should be run via cron at reasonable interviews from within the Orcfax
network.

E.g.

<!-- markdownlint-disable -->

```cron
# Run on the third minute of every hour.
3 */1 * * * cd /home/orcfax/pubwatch && /home/orcfax/pubwatch/pubwatch.sh 2>&1 | logger -t orcfax_pubwatch
```

<!-- markdownlint-enable -->

## Output

Logging will be visible to the user as follows:

<!-- markdownlint-disable -->

```log
2024-08-28 09:03:01 INFO :: feed_helper.py:31:read_feeds_file() :: cer-feeds version: 2024.08.12.0001
2024-08-28 09:03:01 INFO :: feed_helper.py:32:read_feeds_file() :: number of feeds: 21
2024-08-28 09:03:01 INFO :: pubwatch.py:389:pubwatch() :: policy: 900d528f3c1864a1376db1afc065c9b293a2235f39b00a67455a6724
2024-08-28 09:03:03 INFO :: pubwatch.py:392:pubwatch() :: unspent datum: 194
2024-08-28 09:03:03 INFO :: pubwatch.py:362:compare_intervals() :: using the hour as a boundary
2024-08-28 09:03:03 INFO :: pubwatch.py:399:pubwatch() :: we need to request the following feeds: ['BTC-USD']
2024-08-28T09:03:03 INFO :: connection_managers.py:95:connect() :: validation connection manager: new 'ack' connection from 'ac796b0a-f06a-4c5a-80df-12779c64aacd' 127.0.0.1 (orcfax-pubwatch/0.0.0) {}
2024-08-28 09:03:03 INFO :: pubwatch.py:92:connect_to_websocket() :: connected to websocket
2024-08-28 09:03:03 INFO :: pubwatch.py:94:connect_to_websocket() :: {"feeds": ["BTC-USD"]}
```

<!-- markdownlint-enable -->

If new feeds are required on-chain because they have previously expired, i.e.
their age on-chain is higher than their configured interval, then they will be
requested from the validator and published via the `validate_on_demand/`
endpoint of the validator.

[cer-feeds-1]: https://github.com/orcfax/cer-feeds
