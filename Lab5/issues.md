| Issue | Type | Original line(s) | Description | Fix approach |
|---|---|---|---|---|
| B201: Flask debug mode | Security — High | 80 | Debug mode exposes the interactive debugger if reachable. | Set debug=False. |
| B506: Unsafe YAML loading | Security — Medium | 21 | The loader can construct arbitrary Python objects. | Use yaml.safe_load(). |
| B612: Remote logging configuration | Security — Medium | 72 | Remote configuration introduces an unnecessary code-execution risk. | Replace the listener with local logging configuration. |
| B106: Hardcoded password | Security — Low | 66 | A password is stored directly in source code. | Read it from an environment variable and reject missing values. |
| B311: Predictable lottery randomness | Security — Low | 56 | Standard pseudo-random sampling is unsuitable when unpredictability matters. | Use secrets.SystemRandom().sample(). |