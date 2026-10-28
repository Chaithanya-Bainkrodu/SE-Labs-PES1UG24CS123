# Reflection

*Sample reflection questions*

## 1. Which issue would I prioritise, and why?

I would prioritise Flask debug mode because Bandit classified it as a high-severity finding. If the development debugger is exposed, it can create a serious code-execution risk. Setting `debug=False` removes that specific unsafe setting. I would then address unsafe YAML loading and the remote logging configuration listener, both reported as medium severity. This exercise showed me why findings should be prioritised by their potential impact rather than fixed only in the order they appear. Style improvements are useful, but they should not distract from security-sensitive behaviour.

## 2. What did reviewing the allocation logic reveal that the tool reports alone could not establish?

The hostel rules required more than clean formatting or a high quality score. A room at capacity must not receive another occupant, the selected room must match the student's gender, and requesting an allocation twice must not consume two beds. Vacating must also update both the allocation record and the occupant list. I addressed these cases through a capacity check using `>=`, a compatibility check, an early return for existing allocations and removal of the occupant when vacating. The unused gender argument was a useful warning, but understanding its effect required reviewing the intended allocation rules.

## 3. How would I check that the fixes preserve the intended behaviour?

I would use small, repeatable tests with a known room configuration. For capacity, I would fill a room and verify that the next request does not increase its occupancy. For duplicate requests, I would allocate the same student twice and check that only one bed is occupied. I would verify that a student receives a compatible room, that vacating increases the vacant-bed count by one, and that higher-year students appear first in priority ordering. I would also check that boolean and non-integer year values are rejected. These are proposed verification steps; automated regression-test results are not included in this report.

## 4. What do the final tool results tell me about the quality of the program?

The recorded results show that the documented changes resolved the reported findings under the scan settings used. Pylint improved from 5.84/10 to 10.00/10, Bandit went from five findings to no issues identified, and the final Flake8 report contains no diagnostic text. These results are useful evidence of improved code quality, but they are not a certificate of complete correctness or security. For example, the monthly-fee function still needs its completed-30-day-period rule checked against the actual billing requirements. I would combine static analysis with runtime tests and manual review before relying on the system in practice.
