def test_addr(addr1):
    _addr, _city, _country = addr1
    assert _country.country == 'US'
    assert _city.city == 'NYC'
    assert _addr.state == 'New York'
    assert isinstance(_addr.to_dict(), dict)
