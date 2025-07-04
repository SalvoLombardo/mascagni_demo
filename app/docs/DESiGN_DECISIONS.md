# design-decision.md

## Context

The app was born for a small **musical association** that runs a yearly subscription campaign.  
Each subscriber can hold one subscription per year, but may be subscribed in different years (e.g. 2020, 2022, 2025).

There are two user roles:

| Role     | Description                                                                  |
|----------|------------------------------------------------------------------------------|
| Operator | receives a batch of physical tickets (numbered) and try sells them to people |
| Admin    | manages campaigns, tickets, and overall data |

Operators need real-time info such as:  
. Has this subscriber already paid and received his ticket?
. Which past subscribers could we contact for the new campaign?

After the campaign the association exports the full list to Excel / XML for a broadcast newsletter, in a specif format.

---

## Key Decisions

1. **No unique phone/email**  
   I've tried to adapt on thei necessity, they work in a small place and won't change too much in the way are used to make subscriptions to subscribers.
   The association didn’t want to force unique fields. There may be homonyms.  
   I added a `subscriber_note` column so operators can disambiguate manually. Not ideal, but it mirrors their pen-and-paper workflow. Also be in a small city in italy means everybody knows everybody, it's usal in homonyms situation to say 'He's the barber and the other one is the doctor'.

2. **Campaign workflow**  
   - Operators can sell tickets *only* after an Admin creates a campaign *and* assigns the physical ticket range.  
   - An Operator may edit **only** the subscribers he inserted.  
   - Only Admin can delete a subscriber (to fix major mistakes) or create / delete campaigns.

3. **Safety**  
   - CSRF protection everywhere.  
   - Passwords hashed with `bcrypt`.  
   - Simple server-side validation: if an Operator sets “cash” as payment method but leaves “paid” unchecked, the record is stored as *not paid*, *payment_method = not_yet_paid*.

---

## Why not XYZ?

- **Django** feels heavy for this scope; Flask gave me full control while I’m still learning.
- **Unique constraint on names**: rejected by stakeholders (see point 1).

⸻

