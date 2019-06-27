# DNS load tool [![Build Status](https://travis-ci.org/lloesche/dnsload.svg?branch=master)](https://travis-ci.org/lloesche/dnsload)
Simple script to load test DNS resolution.

Either with a fixed number of concurrent lookups (`--max`) over a period of time (`--duration`)
or a one-time measurement of ramping up (`--step`) concurrent lookups up to a maximum (`--max`)

## Usage
```
usage: dnsload [-h] --domain DOMAIN [--max MAX]
               (--duration DURATION | --step STEP) [--raw] [--ns NS]
               [--verbose]

DNS Load

optional arguments:
  -h, --help           show this help message and exit
  --domain DOMAIN      Domain to lookup
  --max MAX            Max concurrent lookups (default: 100)
  --duration DURATION  For how long to load test
  --step STEP          Step size
  --raw                Perform RAW DNS lookups, bypass system libraries
  --ns NS              Nameserver to query when doing RAW lookup (default:
                       resolv.conf)
  --verbose            Verbose logging
```

## Example
Test DNS resolution from 100 to 1000 concurrent lookups in steps of 100
```
$ dnsload --domain example.com --max 1000 --step 100
```

Test DNS resolution for an hour with 100 concurrent lookups
```
$ dnsload --domain example.com --max 100 --duration 3600
```

Test RAW DNS resolution against nameservers in /etc/resolv.conf for an hour with 100 concurrent lookups
```
$ dnsload --domain example.com --max 100 --duration 3600 --raw
```

Test RAW DNS resolution against 1.1.1.1 for an hour with 100 concurrent lookups
```
$ dnsload --domain example.com --max 100 --duration 3600 --raw --ns 1.1.1.1
```

Using Docker
```
$ docker run --rm -it lloesche/dnsload --domain example.com --max 100 --step 10
```
