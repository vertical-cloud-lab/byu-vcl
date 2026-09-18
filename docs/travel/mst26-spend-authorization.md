# MS&T 2026 — Workday Spend Authorization worksheet

Prepared 2026-09-18 for a resubmission of a previously rejected spend authorization.
Everything below is ready to be typed into Workday; **no part of this was submitted for
you** (see "What still needs your hands").

## Trip at a glance

| Field | Value |
| --- | --- |
| Event | MS&T26 — Materials Science & Technology, ACerS 128th Annual Meeting |
| Venue | David L. Lawrence Convention Center, Pittsburgh, PA |
| Conference runs | Sun 4 Oct – Thu 8 Oct 2026 |
| **Your attendance** | **Mon 5 Oct – Wed 7 Oct 2026** |
| Travel dates (Workday Start/End) | **Sun 4 Oct 2026 → Wed 7 Oct 2026** |
| Business purpose | Conference / Professional Development |
| Destination | Pittsburgh, PA, USA (domestic — no International VP routing) |

Note the Workday Start/End dates are the **travel** dates, not the Mon–Wed attendance
window. Putting 5 Oct as the start would leave Sunday's airfare and first hotel night
outside the authorized window.

## Flight options (live fares, pulled 2026-09-18)

Retrieved from Google Flights via the CubXL Raspberry Pi's residential connection —
the GitHub runner's datacenter IP is blocked from those results. These are public
"from" fares; BYU's contracted fare through Simply Travel may differ.

| Option | Routing | Outbound Sun 4 Oct | Return Wed 7 Oct | RT total |
| --- | --- | --- | --- | --- |
| **Delta — nonstop (recommended)** | SLC↔PIT | 10:50 → 16:33 | 17:46 → 20:10 | **$937** |
| Southwest — 1 stop (DEN) | SLC↔PIT | 08:10 → 15:35 | 18:10 → 22:15 | $783 |
| Southwest — 1 stop (PHX) | SLC↔PIT | 12:15 → 23:15 | — | $667 |
| Southwest — 2 stops | SLC↔PIT | 13:05 → 22:40 | — | $634 |
| United — 1 stop (DEN) | SLC↔PIT | 07:00 → 14:42 | — | $1,144 |

**The Delta nonstop is the one that actually matches your constraints.** It arrives
16:33 Sunday (you said "a bit earlier in the evening, like 7:00 p.m.") and departs
17:46 Wednesday (you said "after 5:00 p.m."). The cheaper Southwest fares mostly land
between 22:40 and 00:45 Monday, which defeats the point of flying Sunday.

The $783 Southwest is the one real alternative: 15:35 Sunday arrival, 18:10 Wednesday
departure, two free checked bags, ~$154 cheaper — at the cost of a connection each way.

Delta includes 1 carry-on and **0 checked bags**; budget $70 round trip if you check one.

## Budget lines for the Spend Authorization

BYU follows federal GSA per diem as its guideline. These are the GSA FY2027 rates for
Pittsburgh (Allegheny County), effective 1 Oct 2026 — pulled from gsa.gov directly, so
they cover your travel dates:

- Lodging **$144/night** (excluding taxes)
- M&IE **$80/day**; first and last day of travel **$60.00**
- Breakdown: breakfast $20, lunch $22, dinner $33, incidentals $5

| Line | Basis | Amount |
| --- | --- | --- |
| Airfare | Delta nonstop RT, +buffer for fare drift | $950 |
| Lodging | 3 nights (4, 5, 6 Oct), conference-block rate ~$259 + ~14% Pittsburgh lodging tax | $890 |
| Meals & incidentals | $60 + $80 + $80 + $60 | $280 |
| Registration | MS&T full conference, member rate — **CONFIRM, see below** | $1,200 |
| Ground transport | Provo↔SLC airport + parking; PIT airport↔downtown | $220 |
| Baggage / incidentals | 1 checked bag round trip | $70 |
| **Total** | | **≈ $3,610** |

Round up to **$3,650–$3,700** when you enter it. A spend authorization is a ceiling;
coming in under is routine, going over is the thing that causes trouble.

### Two numbers to sanity-check before submitting

- **Registration — $1,200 is my estimate, not a sourced figure.** The entire
  matscitech.org / ceramics.org / tms.org web estate sits behind a Cloudflare bot
  challenge that blocks automated fetches (I tried from both the runner and the Pi's
  residential IP, and did not attempt to defeat the challenge). Pull the real number
  from the registration page while logged in and replace it.
- **Lodging $890 assumes the conference hotel**, benchmarked against downtown
  Pittsburgh convention-block rates, *not* against MS&T's published block — I could not
  reach it, same Cloudflare block. If you stay at GSA rate instead, the line is
  3 × $144 + tax ≈ **$493**, and the total drops to about **$3,210**.

### Per diem mechanics

- 12+ hours away from home is the eligibility threshold — you clear it comfortably.
- You must choose **per diem or actual expenses for the whole trip**; mixing the two is
  not permitted.
- Deduct any meals the conference provides. MS&T typically includes at least one
  reception; subtract the corresponding $20/$22/$33 for any meal you don't pay for.

## BYU process facts that bear on the resubmission

Sourced from purchasing.byu.edu:

- A Spend Authorization is **required** for university travel involving overnight stays
  or commercial transportation.
- **Full approval is required before booking travel or incurring any expense.** Nothing
  gets booked until this clears.
- Include expense lines for all reservations: airfare, lodging, car rentals.
- Risk Management joins the approval chain when personal vehicle mileage exceeds $200 —
  a Provo↔SLC airport round trip stays well under, so parking + mileage keeps you out of
  that routing.
- Booking goes through **Simply Travel**, BYU's self-booking tool, which carries
  university contracted pricing: <https://purchasing.byu.edu/simply-travel>
- Afterward: Expense Report within 30 days of trip completion. Receipts required for any
  travel expense over $50; receipts are *not* required for per diem or mileage.

### Timing

Guidance is to submit at least 10 days before travel. From 18 Sep to 4 Oct you have
16 days, so you are inside the window — but the margin is real, and this one has already
been rejected once. Approval also has to finish before anything can be booked, and the
$937 nonstop fare will not hold while that happens.

## What still needs your hands

- Entering and submitting the Spend Authorization in Workday.
- Confirming the registration fee and the hotel rate.
- Locating the "green form" approval (see the issue thread).
