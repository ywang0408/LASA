# Congress file quality checklist

Use this before replacing `data/simulated_congresses.csv` with a file from LASA.

- [ ] Each row is one congress: host city and year.
- [ ] Paid registrations use the counting rule LASA confirmed.
- [ ] Origin segments add up to the paid total, or the gap is explained.
- [ ] The file records which fields are LASA data, public data, or simulated data.
- [ ] Simulated rows are labeled `simulated` and are kept out of any sentence that sounds like a validated forecast.
- [ ] `validate_simulation` has been updated if the real file uses different columns, and the tests pass.
- [ ] The real file is not committed to a public repository.
