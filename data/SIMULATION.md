# Simulated congress file

`simulated_congresses.csv` is a pipeline fixture. Every attendance number in it was written for this repository. None of the rows are LASA’s historical results, and none should be quoted to LASA as an attendance estimate.

## Generation rules

- Eight congresses, one row each, for Boston, Lima, Barcelona, Guadalajara, and Montreal.
- Paid registrations are whole numbers between 1900 and 3400. That band is a stated demo range for a large scholarly meeting, not a fit to LASA’s books.
- Each row splits paid registrations into two origin segments, USA and Latin America & Others. The two segments add up to the paid total. The split is a fixture so the comparison view has both segments. It is not a measurement of LASA’s membership.
- `data_source` is `simulated` on every row.
- No field is left blank.

## Quality checks

`lasa_pilot.tools.validate_simulation` rejects the file when any of the following is true:

- a required column is missing or blank
- `data_source` is anything other than `simulated`
- `usa_registrations + latam_and_other_registrations` does not equal `paid_member_registrations`
- paid registrations fall outside 1900–3400

`python3 -m unittest discover -s tests -v` runs these checks. Replace this file only when LASA’s own congress file arrives, and keep real records out of public commits.
