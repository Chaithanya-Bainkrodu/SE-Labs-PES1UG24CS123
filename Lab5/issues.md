| Issue | Type | Original line(s) | Description | Fix approach |
|---|---|---|---|---|
| B201: Flask debug mode | Security — High | 80 | Debug mode exposes the interactive debugger if reachable. | Set debug=False. |
| B506: Unsafe YAML loading | Security — Medium | 21 | The loader can construct arbitrary Python objects. | Use yaml.safe_load(). |
| B612: Remote logging configuration | Security — Medium | 72 | Remote configuration introduces an unnecessary code-execution risk. | Replace the listener with local logging configuration. |
| B106: Hardcoded password | Security — Low | 66 | A password is stored directly in source code. | Read it from an environment variable and reject missing values. |
| B311: Predictable lottery randomness | Security — Low | 56 | Standard pseudo-random sampling is unsuitable when unpredictability matters. | Use secrets.SystemRandom().sample(). |
| W0102: Mutable default argument | Code quality | 29 | A default list is shared across calls and can cause bugs if modified. | Use None and initialize a list inside the function. |
| C0123: Type checking | Code quality | 30 | Direct type comparison is unidiomatic. | Use isinstance() and reject boolean year values. |
| W0613: Unused gender argument | Logic / code quality | 29–38 | Allocation ignores room gender compatibility. | Check room gender before allocating. |
| Room capacity check | Logic | 34 | A full room is not skipped because the check uses >. | Use >= to prevent over-allocation. |
| Duplicate allocation | Logic | 29–39 | Repeated allocation can add the same student more than once. | Return the existing allocation before assigning a bed. |
| Incomplete vacation | Logic | 41–45 | Deleting an allocation does not remove the room occupant. | Remove both the allocation and the occupant entry. |
| Incorrect seniority ordering | Logic | 52–53 | Ascending year order puts juniors first. | Sort by year with reverse=True. |
| C0206: Dictionary iteration and vacant beds | Code quality / logic | 58–63 | Partially occupied rooms are excluded from the vacant-bed count. | Iterate over room values and sum capacity minus occupancy. |
| C0103 / C0114 / C0116: Naming and documentation | Maintainability | Throughout | Function names and documentation do not follow conventions. | Use snake_case and add module and function docstrings. |
| W0611 / C0301: Unused import and long line | Code quality | 2, 95 | An unused import and an overly long expression reduce clarity. | Remove sys and split the expression into readable steps. |