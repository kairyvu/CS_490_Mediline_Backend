def test_appt(appt1):
    _, _, appt, _ = appt1
    assert appt.appointment_id == 1

def test_appt_detail(appt1):
    _, _, appt, ad = appt1
    assert {'treatment', 'start_date', 'end_date'} <= set(vars(ad))
    assert appt.appointment_id == ad.appointment_details_id
    assert ad.status.value == 'pending'