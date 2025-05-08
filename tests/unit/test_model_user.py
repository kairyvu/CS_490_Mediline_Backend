from flaskr.struct import AccountType

def test_user_patient(pt1):
    _u, _p, _ = pt1
    assert (isinstance(_u.account_type, AccountType) or isinstance(_u.account_type, str))
    assert (isinstance(_u.account_type, AccountType) 
            and _u.account_type.value == 'patient') \
            or _u.account_type == 'patient'
    assert _p.first_name == 'John'
    assert _p.last_name == 'Smith'
    assert isinstance(_u.to_dict(), dict)
    assert isinstance(_p.to_dict(), dict)

def test_user_doc(dr1):
    _u, _d, _ = dr1
    assert (isinstance(_u.account_type, AccountType) 
            or isinstance(_u.account_type, str))
    assert (isinstance(_u.account_type, AccountType) 
            and _u.account_type.value == 'doctor') \
            or _u.account_type == 'doctor'
    assert _d.first_name == 'Jack'
    assert _d.last_name == 'Daniels'
    assert _d.bio == 'Blah Blah Blah'
    assert isinstance(_u.to_dict(), dict)
    assert isinstance(_d.to_dict(), dict)

def test_user_pharm(pharm1):
    _u, _ph, _ = pharm1
    assert (isinstance(_u.account_type, AccountType) or isinstance(_u.account_type, str))
    assert (isinstance(_u.account_type, AccountType) 
            and _u.account_type.value == 'pharmacy') \
            or _u.account_type == 'pharmacy'
    assert _ph.pharmacy_name == 'Walgreens'
    assert _ph.hours == '10am-5pm'
    assert isinstance(_u.to_dict(), dict)
    assert isinstance(_ph.to_dict(), dict)
