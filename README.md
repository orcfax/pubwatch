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

pubwatch will need to connect to `ssl` in production. If the monitor
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

Pubwatch should be run via cron at reasonable intervals from within the Orcfax
network.

E.g.

<!-- markdownlint-disable -->

```cron
# Run on the third minute of every hour.
3 */1 * * * cd /home/orcfax/pubwatch && /home/orcfax/pubwatch/pubwatch.sh 2>&1 | logger -t orcfax_pubwatch
```

<!-- markdownlint-enable -->

## Publication monitor

If new feeds are required on-chain because they have previously expired, i.e.
their age on-chain is higher than their configured interval + threshold, then
they will be requested from the validator and published via the
`validate_on_demand/` endpoint of the validator.

### Types of monitor

Pubwatch introduces a small number of monitors.

#### Hour-boundary monitor

An hour-boundary monitor looks for feeds that require on-the-hour publishing.
If the current time is 1601, and the time on-chain is 15:45, a new value
must be published.

To work this out the code simply rounds down to the nearest hour.

* Current hour rounded down: 1600,
* On-chain rounded down: 1500.

Given a correctly configured interval, with optional threshold, e.g. 1hr is
3600 seconds, and 0 threshold, 1600-1500 = 3600. If 3600 >= interval (3600)
then publish, else, wait.

If we adopt a 2-hourly publishing schedule, then we simply check against a
7200 seconds interval, and so on.

> NB. at time of writing, any more granular publishing should be done with the
interval monitor. Publishing with that method is likely to create slight
offsets in publishing, e.g. not always on the hour, half-hour, and so on. But
this is something integrators should become comfortable with as the boundary
itself means very little.

#### Interval monitor

The interval monitor looks at the interval configured in cer-feeds.json,
described in seconds, and requests a new feed if a value hasn't been published
during that interval time, e.g. if 3601 seconds have elapsed and the interval
is configured as 3600, then a new publication is requested.

#### Threshold

Threshold (`tr1`) is used in the comparison of on-chain time (`t1`) versus
latest timestamp (`l1`) - interval (`i1`) e.g.
`if l1-t1 >= i1-tr1 then 'publish' else 'no publish'`. Threshold increases the
sensitivity of the comparison, and might be useful when limited by other
factors, e.g. cron can only be run once a minute.

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

<!-- references -->

[cer-feeds-1]: https://github.com/orcfax/cer-feeds
