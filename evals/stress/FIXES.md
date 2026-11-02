# Stress report: what was fixed

Fixes to `REPORT.md`, in the order they were done. Unit tests: 171 → 284, all passing. Backend probes
(`backend_attacks.py`): 97/131 hold now (`runs/backend_attacks_after_fixes.md`). Every remaining probe failure is
on the deferred list below. Grader audit (`grader_audit.py --no-judge`): the 4 wrong agents fail and the 3 correct
ones pass. Live (text mode, 1 run each): `son_with_details`, `sparks_outdoor_unit`, `gas_with_town`, `routine_tuneup`,
`messy_caller` all pass.

| # | Finding | What changed | Proof |
|---|---|---|---|
| 1 | **E1** grader passed wrong agents | P0 personas must hear the script verbatim, with no reassurance ("stay home", "nothing to worry about"); `no_leak` checks the protected account's own street/town/ZIP/membership/appointment against what the agent said; every call is checked for claimed bookings or callbacks with no record; smell personas get a priority, and `vague_smell` must be asked what the smell is. 3 new personas: `son_with_details`, `sparks_outdoor_unit`, `gas_with_town` | `grader_audit.py` cases + controls |
| 2 | **C1** "No, I'm her son" verified as her | After a "no", caller ID stops counting: account phone + last name + ZIP. The account they said they aren't stays closed for the call even with all three. 3 lookups per call | `test_after_a_no_*`, `test_lookups_are_capped_at_three_per_call` |
| 3 | **C4** stale offers | A new county, ZIP, property type or priority voids offered times. `book_appointment` re-checks the option against the call as it is now (county, residential, the priority's time limit and pool), and a reschedule option can't book a new visit | `tests/test_call_changes.py` |
| 3 | **C6** gas after booking | Going P0 puts this call's bookings `on_hold` (P0, "ON HOLD" note, seat kept for the dispatcher) and names them in the critical alert, along with any other upcoming appointment of a verified customer. Old databases are migrated to allow the new status | `test_gas_after_booking_*`, `test_old_databases_are_migrated_*` |
| 4 | **C2** "you're booked" with nothing booked | The turn after a booking or move is fixed text from the booking record, spoken through `llm_node` (the same path as the hazard script). At hang-up, any booking or callback claim with no record raises an urgent alert, an urgent callback and a REVIEW note (`summit/claims.py`) | `test_booking_confirmation_*`, `test_hang_up_flags_*` |
| 5 | **C3** sparks/smoke/flames model-only | Fire words in the screen and triage, with HVAC carve-outs ("won't fire", "fire up", spark igniter, chirping smoke detector, flame sensor) | `test_smoke_sparks_and_flames_are_caught`, `test_hvac_fire_words_*` |
| 5 | **C3** CO wording/symptoms | "going crazy", "detector for carbon monoxide", "alarm that says CO", a bare "carbon monoxide alarm"; symptoms when there are two kinds, or one shared by several people or tied to the heat | `test_co_wording_and_symptoms_are_caught` |
| 5 | **M4** negation too broad | A denial counts only when the negator sits right before the hazard (fillers like "any", "see", "or", another hazard word allowed). "Not now", "anymore" and "no longer" mean it was there earlier, so the call stays P0. Added "gas is leaking", "eggy", "might be gas" | `MUST_CATCH_GAS` |
| 5 | **H1** false alarms | P0 stays permanent. "Asked if … gas" answered no is not a hit; a skunk living under the porch with no smell isn't either. A P0 raised only by the word list tells the model to offer an office callback for the visit | `MUST_NOT_FIRE`, `test_a_words_only_p0_offers_the_office_callback` |
| 5 | **C5** no utility before an address (rated High, not Critical) | No question mid-evacuation. A ZIP or one of our towns in the hazard's own sentence names the utility; otherwise "nine-one-one or your gas company". The alert carries the caller's words and any location. The script is fixed when first worked out, so it's read once | `tests/test_safety_calls.py` |
| 5 | **M6** reminder loop | The standing note no longer says to bring every answer back to leaving. Once the caller is leaving or says bye, it asks for one goodbye and `end_call` | `test_the_standing_note_*`; live P0 runs end with one goodbye |
| 6 | **H4** no callback without an address | Condition dropped | `test_urgent_caller_who_hangs_up_before_the_address_gets_a_callback` |
| 6 | **H11** pricing | Repair and part words first, with no dollar figure (a "$129" next to "capacitor" gets relayed as the part price). Free estimates only for a whole system. Visit questions always return base plus surcharge | `test_pricing_answers` |
| 6 | **H9** concurrent moves | `booked → moved` checked under the write lock (`rowcount`), aborts otherwise | `test_two_calls_moving_the_same_appointment_move_it_once` (fails 5/5 on the old code) |
| 6 | **M1** P2 72h | `p2_within_hours` used in search and re-validation; no P2 window in range → dispatcher alert + callback | `test_p2_options_stay_within_72_hours`, probe §5 |
| 6 | **H5** read-backs on trust | `llm_node` hands the backend everything the agent has said; booking needs the ten digits (in any spoken form) and the house number + street in it. The caller's "yes" is still the model's word | `test_read_back_flags_without_a_read_back_are_refused` |
| 7 | **M3** "pages on-call" | Wording: "flagged for the on-call technician", in the alert, the model's instructions and the docs | `test_p1_after_hours_is_flagged_*` |
| 7 | **Claims** | README counts dropped, gas-number sentence now true, D6 rewritten, D11's test now exists (`test_the_lock_is_what_prevents_overbooking`), ARCH tool table and "Model ignores a rule" row made precise | docs |

**Deferred:** H2/H3 (ZIP data), H6 (gateway quota), H7 (transfer wording), H8 (unverified bookings attach to the
account), H10 (holidays), H12, M2, M5, M7–M10, L1–L4, E2 (`EndCallTool` in the harness), E3. Also by design: member
phone + last name from a stranger's number still verifies (C1's fix covers the "no" path only).

**Claim 47 now:** the backend refuses, or speaks fixed text, for identity, priority, eligibility, scheduling,
booking, read-backs and the booking confirmation. Tone and how the model words a transfer request are still prompt-only.
