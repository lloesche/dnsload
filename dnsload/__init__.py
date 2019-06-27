import socket
import time
import sys
import dnslib
import re
import random
import logging
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from multiprocessing.pool import ThreadPool
from typing import List, Union
from functools import partial
from pprint import pformat

logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')
logging.getLogger(__name__).setLevel(logging.INFO)
log = logging.getLogger(__name__)
start = time.time()


def main() -> None:
    args = get_args()
    if args.duration:
        log.info('Testing DNS resolution for at least {} seconds with {} concurrent lookups'.format(args.duration, args.max))
        stop = start + args.duration
        loops = 0
        while time.time() < stop:
            if not bench(args.max, args.domain, args.raw, args.ns):
                sys.exit(1)
            loops += 1
            time.sleep(args.wait)
        elapsed = time.time() - start
        log.info('DNS resolution happened {} times with {} concurrent lookups each in {:.2f} seconds'.format(loops, args.max, elapsed))
    else:
        log.info('Testing DNS resolution from {} to {} concurrent lookups in steps of {}'.format(args.step, args.max, args.step))
        for num_threads in range(args.step, args.max + 1, args.step):
            if not bench(num_threads, args.domain, args.raw, args.ns):
                sys.exit(1)
            time.sleep(args.wait)
        log.info('DNS resolution worked up to {} concurrent requests'.format(args.max))


def bench(num_threads: int, domain: str, raw: bool = False, ns: Union[str, None] = None) -> bool:
    if raw and not ns:
        ns = random.choice(get_resolvers())
    res = concurrent_nslookup(num_threads, domain, ns)
    for e in res:
        if isinstance(e, Exception):
            elapsed = time.time() - start
            log.error('DNS resolution failed at {} concurrent requests after {:.2f} seconds with {}'.format(num_threads, elapsed, e))
            return False
    return True


def concurrent_nslookup(num_threads: int, domain: str, ns: Union[str, None] = None) -> List:
    log.debug('Testing DNS resolution against {} with {} concurrent lookups'.format(ns, num_threads))
    p = ThreadPool(num_threads)
    try:
        func = partial(nslookup, ns)
        domains = [domain] * num_threads
        res = p.map(func, domains)
    finally:
        p.close()
        p.join()
    return res


def get_resolvers() -> List:
    resolvers = []
    with open('/etc/resolv.conf', 'r') as resolvconf:
        for line in resolvconf.readlines():
            line = line.rstrip()
            if line.startswith('nameserver'):
                line = re.sub('[ \t]+', ' ', line)
                resolvers.append(line.split(' ')[1])
    return resolvers


def nslookup(ns: Union[str, None], name: str) -> Union[str, Exception]:
    info = ''
    try:
        if not ns:
            log.debug('Querying the system for {}'.format(name))
            ret = socket.gethostbyname(name)
        else:
            log.debug('Querying {} for {}'.format(ns, name))
            q = dnslib.DNSRecord.question(name)
            socktype = socket.AF_INET6 if ':' in ns else socket.AF_INET
            c = socket.socket(socktype, socket.SOCK_DGRAM)
            c.settimeout(5)
            c.sendto(bytes(q.pack()), (ns, 53))
            packet, _ = c.recvfrom(1024)
            d = dnslib.DNSRecord.parse(packet)
            info = ' ' + pformat(d)
            if d.header.rcode > 0:
                rcode = dnslib.RCODE.get(d.header.rcode)
                raise RuntimeError('NS lookup failed: {}'.format(rcode))
            if len(d.rr) == 0:
                raise RuntimeError('NS lookup failed: NS returned no resource records')
            ret = str(d.rr[0].rdata)
    except Exception as e:
        log.exception('DNS lookup failed{}'.format(info))
        ret = e
    return ret


def positive_int(value) -> int:
    i = int(value)
    if i <= 0:
        raise ArgumentTypeError('{} is an invalid positive int value'.format(value))
    return i


def get_args() -> Namespace:
    p = ArgumentParser(description='DNS Load')
    p.add_argument('--domain', help='Domain to lookup', dest='domain', type=str, required=True)
    p.add_argument('--max', help='Max concurrent lookups (default: 100)', dest='max', default=100, type=positive_int)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--duration', help='For how long to load test', dest='duration', type=positive_int)
    g.add_argument('--step', help='Step size', dest='step', type=positive_int)
    p.add_argument('--wait', help='Time to wait between lookup rounds', dest='wait', type=float, default=0.0)
    p.add_argument('--raw', help='Perform RAW DNS lookups, bypass system libraries', dest='raw', action='store_true', default=False)
    p.add_argument('--ns', help='Nameserver to query when doing RAW lookup (default: resolv.conf)', dest='ns', type=str, default=None)
    p.add_argument('--verbose', help='Verbose logging', dest='verbose', action='store_true', default=False)
    args = p.parse_args()

    if args.step:
        if args.step > args.max:
            p.error('step {} is larger than max {}'.format(args.step, args.max))
        if args.max % args.step != 0:
            p.error('max {} must be divisible by step {}'.format(args.max, args.step))

    if args.ns and not args.raw:
        p.error('specifying NS only works in RAW mode')

    if args.verbose:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    return args


if __name__ == '__main__':
    main()
