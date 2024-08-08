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

## Output

Logging will be visible to the user as follows:

<!-- markdownlint-disable -->

```log
2024-08-08 14:47:55 INFO :: feed_helper.py:29:read_feed_data() :: cer-feeds version: 2024.08.06.0002
2024-08-08 14:47:55 INFO :: feed_helper.py:30:read_feed_data() :: number of feeds: 13
2024-08-08 14:47:55 INFO :: pubwatch.py:286:pubwatch() :: policy: 900d528f3c1864a1376db1afc065c9b293a2235f39b00a67455a6724
2024-08-08 14:47:59 INFO :: pubwatch.py:289:pubwatch() :: unspent datum: 75
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '923'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/IBTC-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/IETH-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/MIN-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/SNEK-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/SHEN-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-EUR' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/ADA-EUR' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/FACT-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LQ-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/WMT-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/WMT-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/NEWM-ADA' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/NEWM-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-DJED' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-IUSD' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USDM' delta: '2876'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/HUNT-ADA' delta: '2877'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '2877'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '4708'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/IBTC-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/IETH-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/MIN-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/SNEK-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/SHEN-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-EUR' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/ADA-EUR' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/FACT-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LQ-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/WMT-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/WMT-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/NEWM-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/NEWM-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-DJED' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-IUSD' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USDM' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/HUNT-ADA' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '6476'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/IBTC-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/IETH-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/SNEK-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/SHEN-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-EUR' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/ADA-EUR' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/FACT-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LQ-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/WMT-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/WMT-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/NEWM-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/NEWM-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-DJED' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-IUSD' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USDM' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/HUNT-ADA' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '10077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '55238'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '64077'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '65716'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '66618'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-DJED' delta: '85676'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-IUSD' delta: '85676'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USDM' delta: '85676'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/HUNT-ADA' delta: '85676'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '85676'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '85802'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/MIN-ADA' delta: '87484'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '88266'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-IUSD' delta: '88266'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/HUNT-ADA' delta: '161276'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '162298'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USD' delta: '163020'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '163812'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '163932'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '164053'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/WMT-ADA' delta: '172076'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/WMT-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/LENFI-ADA' delta: '172076'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/NEWM-ADA' delta: '172076'
2024-08-08 14:47:59 INFO :: pubwatch.py:269:compare_intervals() :: feed: 'CER/NEWM-ADA' not being monitored
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-DJED' delta: '172076'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-IUSD' delta: '172076'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/ADA-USDM' delta: '172076'
2024-08-08 14:47:59 INFO :: pubwatch.py:264:compare_intervals() :: feed 'CER/HUNT-ADA' delta: '172076'
2024-08-08 14:47:59 INFO :: pubwatch.py:292:pubwatch() :: no new pairs needed on-chain...
```

<!-- markdownlint-enable -->

If new feeds are required on-chain because they have previously expired, i.e.
their age on-chain is higher than their configured interval, then they will be
requested from the validator and published via the `validate_on_demand/`
endpoint of the validator.

[cer-feeds-1]: https://github.com/orcfax/cer-feeds
