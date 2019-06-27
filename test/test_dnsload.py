from dnsload import concurrent_nslookup, nslookup, bench

domain = 'example.com'
err_domain = 'qwerty12345'
ns = '8.8.8.8'
err_ns = '999.999.999.999'


def test_nslookup():
    assert isinstance(nslookup(None, domain), str)
    assert isinstance(nslookup(ns, domain), str)
    assert isinstance(nslookup(None, err_domain), Exception)
    assert isinstance(nslookup(ns, err_domain), Exception)


def test_concurrent_nslookup():
    res = concurrent_nslookup(2, domain)
    res.extend(concurrent_nslookup(2, domain, ns))
    assert all(isinstance(r, (str, Exception)) for r in res)


def test_bench():
    assert bench(2, domain)
    assert bench(2, domain, True)
    assert bench(2, domain, True, ns)
    assert bench(2, domain, True, err_ns) is False
