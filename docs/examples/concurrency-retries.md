# Concurrency and Retries

You can run crawler concurrently (up to 10 threds), which is good thing if you checking documentation locally.

```bash
# Running deadlinks in 10 threads agains the local URL.
deadlinks http://127.0.0.1:8000/ -n 10
```

You also can enable retries (it's disabled by default), it means that urls that failed with response code 502-504, can be checked again N attempts, but beware - every next retry will take twice more time!

```bash
# Checking retry options.
time deadlinks http://nosuchdomain/ -r 2  >> /dev/null 2>&1
> real    0m2.408s
time deadlinks http://nosuchdomain/ -r 3  >> /dev/null 2>&1
> real    0m6.421s
time deadlinks http://nosuchdomain/ -r 4  >> /dev/null 2>&1
> real    0m14.427s

# Maximum possible retries.
time deadlinks http://nosuchdomain/ -r 10  >> /dev/null 2>&1
> real    8m6.451s
```
