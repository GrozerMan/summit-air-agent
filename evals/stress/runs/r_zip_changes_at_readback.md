# r_zip_changes_at_readback

Group: readback. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: adaptive.

Brief: You're Jen Morales, 33 Shore Road, phone 631-555-0155, house, tune-up. Say your ZIP is 11706. When they read the address back, say: 'Oh wait, the ZIP is actually 11751, I always mix it up. It's Islip.' Take any time.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| booked_zip_matches_checked | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hi, I'd like to schedule a tune-up for my home heating system.

**Agent:** Can I have your name and the phone number on your account to start?

**Caller:** Sure, it's Jen Morales, and my phone number is 631-555-0155.

> `lookup_customer` {"confirmed_name": null, "phone": "6315550155", "first_name": "Jen", "last_name": "Morales", "zip_code": null}  
> → No account matches those details. Carry on as a new customer and don't share anything about existing accounts.

**Agent:** I couldn't find an account with those details, so we'll set this up as a new customer. Can you describe any issues or just confirm you want a tune-up?

**Caller:** Just want a tune-up, no issues right now.

> `assess_situation` {"description": "Just want a tune-up, no issues right now.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": "tune_up"}  
> → Priority is P3 routine (tune_up). Next, check the service address.

**Agent:** May I have the street address and ZIP code where the tune-up is needed? Also, please tell me what kind of property it is, like a house or condo.

**Caller:** Sure, it's 33 Shore Road, ZIP 11706, and it's a house.

> `check_service_address` {"zip_code": "11706", "town": null, "property_type": "house"}  
> → 11706 is in Suffolk County, which we serve.

> `find_appointment_options` {"reschedule_appointment_id": null}  
> → Offer these arrival windows, earliest first. The technician arrives within the window.
- SUF-1104-1200-R: tomorrow, Wednesday, between noon and 2 PM
- SUF-1104-1600-R: tomorrow, Wednesday, between 4 and 6 PM
- SUF-1105-0800-R: Thursday, November 5, between 8 and 10 AM
Book with the option_id the caller picks.

**Agent:** We have available windows for a tune-up starting tomorrow between noon and 2 in the afternoon, or between 4 and 6 in the afternoon, and also Thursday between 8 and 10 in the morning. Which one works best for you?

**Caller:** Oh wait, the ZIP is actually 11751, I always mix it up. It’s Islip. Tomorrow between 4 and 6 works for me.

> `check_service_address` {"zip_code": "11751", "town": "Islip", "property_type": "house"}  
> → 11751 is in Suffolk County, which we serve.

> `find_appointment_options` {"reschedule_appointment_id": null}  
> → Offer these arrival windows, earliest first. The technician arrives within the window.
- SUF-1104-1200-R: tomorrow, Wednesday, between noon and 2 PM
- SUF-1104-1600-R: tomorrow, Wednesday, between 4 and 6 PM
- SUF-1105-0800-R: Thursday, November 5, between 8 and 10 AM
Book with the option_id the caller picks.

**Agent:** 11751 in Islip is also in Suffolk County, which we serve. Tomorrow between 4 and 6 in the afternoon is available. Can I have your first and last name for the booking?

**Caller:** Jen Morales.

**Agent:** Please give me the best phone number to reach you at.

**Caller:** You can reach me at 631-555-0155.

**Agent:** That's 6-3-1, 5-5-5, 0-1-5-5, right?

**Caller:** Yes, that's correct.

**Agent:** The address again, please, for the booking.

**Caller:** 33 Shore Road, ZIP 11751, Islip.

**Agent:** You said 33 Shore Road, ZIP 11751, in Islip. Is that right?

**Caller:** Yes, that's right. Thank you.

> `book_appointment` {"option_id": "SUF-1104-1600-R", "first_name": "Jen", "last_name": "Morales", "phone": "6315550155", "address": "33 Shore Road, Islip", "zip_code": "11751", "job_type": "tune-up", "notes": "", "phone_read_back_confirmed": true, "address_read_back_confirmed": true}  
> → Booked: appointment #2, tomorrow, Wednesday, between 4 and 6 PM, at 33 Shore Road, Islip. Tune-up: $159. Confirm the day, the window and the address back to the caller. If you haven't yet, you can mention the Summit Comfort Club once (no diagnostic fee, two tune-ups a year, priority scheduling). Don't push it.

**Agent:** Your tune-up is booked for tomorrow, Wednesday, between 4 and 6 in the afternoon at 33 Shore Road in Islip. We appreciate your choosing Summit Air. We also offer the Summit Comfort Club that includes no diagnostic fee, two tune-ups a year, and priority scheduling if you'd like to hear about it. Is there anything else I can help you with?

**Caller:** No, that's all for now. Thanks for your help! Goodbye.

**Agent:** You're welcome! Have a great day. Goodbye.

### DB state
**appointments** (1)
- `{"id": 2, "customer_id": 6, "call_id": "stress-r_zip_changes_at_readback-1", "county": "Suffolk", "day": "2026-11-04", "arrival_window": "16:00-18:00", "pool": "regular", "job_type": "tune-up", "priority": 3, "service_address": "33 Shore Road, Islip, 11751", "contact_name": "Jen Morales", "contact_phone": "+16315550155", "notes": "P3 routine: tune_up. Caller says: Just want a tune-up, no issues right now..", "status": "booked"}`
**alerts** (0)
**callbacks** (0)
**calls row**: priority=3 outcome=booked reasons=['tune_up'] property=residential area={'county': 'Suffolk', 'zip': '11751'} verified=None
**summary**: P3 routine: tune_up. Caller says: Just want a tune-up, no issues right now..

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hi, I'd like to schedule a heating tune-up for my house, please.

**Agent:** I can help with that. Can I have your name, please?

**Caller:** Jen Morales.

> `lookup_customer (REFUSED)` {"confirmed_name": null, "phone": null, "first_name": "Jen", "last_name": "Morales", "zip_code": null}  
> → To look up an account, ask for the phone number on the account plus their last name or ZIP code.

**Agent:** Can you please provide the phone number on your account, or your ZIP code?

**Caller:** My ZIP is 11706.

> `lookup_customer (REFUSED)` {"confirmed_name": null, "phone": null, "first_name": "Jen", "last_name": "Morales", "zip_code": "11706"}  
> → To look up an account, ask for the phone number on the account plus their last name or ZIP code.

**Agent:** Thanks. Can I have the phone number on your account, please?

**Caller:** It's 631-555-0155. Also, when you say the ZIP, it's actually 11751—Islip, I always mix them up.

> `lookup_customer` {"confirmed_name": null, "phone": "6315550155", "first_name": "Jen", "last_name": "Morales", "zip_code": "11751"}  
> → No account matches those details. Carry on as a new customer and don't share anything about existing accounts.

**Agent:** I don't see an account for those details, so I'll help as a new customer. Is your house in Islip, ZIP 11751?

**Caller:** Yes, that's right.

> `assess_situation` {"description": "heating tune-up", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": "tune_up"}  
> → Priority is P3 routine (tune_up). Next, check the service address.

> `check_service_address` {"zip_code": "11751", "town": "Islip", "property_type": "house"}  
> → 11751 is in Suffolk County, which we serve.

> `find_appointment_options` {"reschedule_appointment_id": null}  
> → Offer these arrival windows, earliest first. The technician arrives within the window.
- SUF-1104-1200-R: tomorrow, Wednesday, between noon and 2 PM
- SUF-1104-1600-R: tomorrow, Wednesday, between 4 and 6 PM
- SUF-1105-0800-R: Thursday, November 5, between 8 and 10 AM
Book with the option_id the caller picks.

**Agent:** We have openings for a heating tune-up tomorrow between noon and 2 in the afternoon, tomorrow between 4 and 6 in the evening, or Thursday between 8 and 10 in the morning. Which window works best for you?

**Caller:** The afternoon window tomorrow between noon and 2 works best, please.

**Agent:** Can I have your phone number to book, please? If it's 631-555-0155, just say yes.

**Caller:** Yes.

**Agent:** And your first and last name to confirm?

**Caller:** Jen Morales.

**Agent:** What is the full address for the service?

**Caller:** 33 Shore Road. Also, it's in ZIP 11751, Islip, just to be sure.

**Agent:** The phone number is 631-555-0155, your name is Jen Morales, and the address is 33 Shore Road, Islip, ZIP 11751. Is that all correct?

**Caller:** Yes, that's all correct. Thank you! Goodbye.

> `book_appointment` {"option_id": "SUF-1104-1200-R", "first_name": "Jen", "last_name": "Morales", "phone": "6315550155", "address": "33 Shore Road, Islip", "zip_code": "11751", "job_type": "tune-up", "notes": "", "phone_read_back_confirmed": true, "address_read_back_confirmed": true}  
> → Booked: appointment #2, tomorrow, Wednesday, between noon and 2 PM, at 33 Shore Road, Islip. Tune-up: $159. Confirm the day, the window and the address back to the caller. If you haven't yet, you can mention the Summit Comfort Club once (no diagnostic fee, two tune-ups a year, priority scheduling). Don't push it.

**Agent:** Your heating tune-up is booked for tomorrow, Wednesday, between noon and 2 PM, at 33 Shore Road, Islip. Is there anything else I can help you with?

**Caller:** No, that's everything for now. Thanks again. Goodbye!

**Agent:** You're welcome. Have a good day! Goodbye!

### DB state
**appointments** (1)
- `{"id": 2, "customer_id": 6, "call_id": "stress-r_zip_changes_at_readback-2", "county": "Suffolk", "day": "2026-11-04", "arrival_window": "12:00-14:00", "pool": "regular", "job_type": "tune-up", "priority": 3, "service_address": "33 Shore Road, Islip, 11751", "contact_name": "Jen Morales", "contact_phone": "+16315550155", "notes": "P3 routine: tune_up. Caller says: heating tune-up.", "status": "booked"}`
**alerts** (0)
**callbacks** (0)
**calls row**: priority=3 outcome=booked reasons=['tune_up'] property=residential area={'county': 'Suffolk', 'zip': '11751'} verified=None
**summary**: P3 routine: tune_up. Caller says: heating tune-up.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hi, I was wondering if you offer home heating system tune-ups?

**Agent:** Yes, we do offer tune-ups for home heating systems. Would you like to schedule one?

**Caller:** Yes, please. Can I book an appointment for a tune-up?

**Agent:** Certainly. May I have the ZIP code and type of property where the service will be done?

**Caller:** The ZIP is 11706, and it’s a house. The address is 33 Shore Road.

> `check_service_address` {"zip_code": "11706", "town": null, "property_type": "house"}  
> → 11706 is in Suffolk County, which we serve.

> `find_appointment_options (REFUSED)` {"reschedule_appointment_id": null}  
> → Find out what's wrong and call assess_situation before looking for times.

**Agent:** Before I get times for the tune-up, can you describe any issues or concerns you have with the heating system? Or is this just a routine tune-up with no problems right now?

**Caller:** It’s just a routine tune-up, no issues so far. Thanks.

> `assess_situation` {"description": "routine tune-up, no issues", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": "tune_up"}  
> → Priority is P3 routine (tune_up).

> `find_appointment_options` {"reschedule_appointment_id": null}  
> → Offer these arrival windows, earliest first. The technician arrives within the window.
- SUF-1104-1200-R: tomorrow, Wednesday, between noon and 2 PM
- SUF-1104-1600-R: tomorrow, Wednesday, between 4 and 6 PM
- SUF-1105-0800-R: Thursday, November 5, between 8 and 10 AM
Book with the option_id the caller picks.

**Agent:** We have openings for your tune-up tomorrow between noon and 2 in the afternoon, or between 4 and 6 in the afternoon. We also have slots on Thursday between 8 and 10 in the morning. Which one works for you?

**Caller:** Oh wait, the ZIP is actually 11751, I always mix it up. It's Islip. Could I do the 4 to 6 tomorrow?

> `check_service_address` {"zip_code": "11751", "town": "Islip", "property_type": "house"}  
> → 11751 is in Suffolk County, which we serve.

> `assess_situation` {"description": "routine tune-up, no issues", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": "tune_up"}  
> → Priority is P3 routine (tune_up).

> `find_appointment_options` {"reschedule_appointment_id": null}  
> → Offer these arrival windows, earliest first. The technician arrives within the window.
- SUF-1104-1200-R: tomorrow, Wednesday, between noon and 2 PM
- SUF-1104-1600-R: tomorrow, Wednesday, between 4 and 6 PM
- SUF-1105-0800-R: Thursday, November 5, between 8 and 10 AM
Book with the option_id the caller picks.

**Agent:** The ZIP 11751 is also in Suffolk County, and we serve that area too. The 4 to 6 tomorrow slot is still available if you want to book that. May I have your full name and phone number to set the appointment?

**Caller:** Sure, it’s Jen Morales. The phone number is 631-555-0155.

**Agent:** Thanks, Jen. Please confirm the phone number, 6 3 1 - 5 5 5 - 0 1 5 5, is that right?

**Caller:** Yes, that’s right. Thanks a lot! Goodbye.

**Agent:** I need the full address including city and ZIP code as well to book your appointment. Could you please provide that?

**Caller:** 33 Shore Road, Islip, ZIP 11751.

**Agent:** Please confirm the address: 33 Shore Road, Islip, New York, ZIP 11751. Is that correct?

**Caller:** Yes, that’s correct. Thanks again. Goodbye.

> `book_appointment` {"option_id": "SUF-1104-1600-R", "first_name": "Jen", "last_name": "Morales", "phone": "6315550155", "address": "33 Shore Road, Islip, New York, ZIP 11751", "zip_code": "11751", "job_type": "tune-up", "notes": "", "phone_read_back_confirmed": true, "address_read_back_confirmed": true}  
> → Booked: appointment #2, tomorrow, Wednesday, between 4 and 6 PM, at 33 Shore Road, Islip, New York, ZIP 11751. Tune-up: $159. Confirm the day, the window and the address back to the caller. If you haven't yet, you can mention the Summit Comfort Club once (no diagnostic fee, two tune-ups a year, priority scheduling). Don't push it.

**Agent:** Jen, your tune-up appointment is set for tomorrow between 4 and 6 in the afternoon at 33 Shore Road, Islip, ZIP 11751. A tech will come by then. Is there anything else I can help with?

**Caller:** No, that’s all for now. Thanks! Goodbye.

**Agent:** You're welcome, Jen. Have a great day! Goodbye.

### DB state
**appointments** (1)
- `{"id": 2, "customer_id": 6, "call_id": "stress-r_zip_changes_at_readback-3", "county": "Suffolk", "day": "2026-11-04", "arrival_window": "16:00-18:00", "pool": "regular", "job_type": "tune-up", "priority": 3, "service_address": "33 Shore Road, Islip, New York, ZIP 11751, 11751", "contact_name": "Jen Morales", "contact_phone": "+16315550155", "notes": "P3 routine: tune_up. Caller says: routine tune-up, no issues.", "status": "booked"}`
**alerts** (0)
**callbacks** (0)
**calls row**: priority=3 outcome=booked reasons=['tune_up'] property=residential area={'county': 'Suffolk', 'zip': '11751'} verified=None
**summary**: P3 routine: tune_up. Caller says: routine tune-up, no issues.