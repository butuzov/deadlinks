# Usage

## Arguments

| Short            | Full                     | Description                                                                      |
|------------------|--------------------------|----------------------------------------------------------------------------------|
| `-e`             | `--external`             | Check, also external links.                                                      |
| `-n <1...10>`    | `--threads  <1...10>`    | Run crawlers concurrently.                                                       |
| `-d <domain>`    | `--domain   <domain>`    | Filter out links with this domain.                                               |
| `-p <path>`      | `--path     <path>`      | Filter out links that contain path.                                              |
| `-s <show>`      | `--show     <show>`      | Select what results to show.                                                     |
| `-r <0...10>`    | `--retry    <path>`      | Number of retries performed if response has 502, 503 or 504<br/> response code.  |
|                  | `--full-site-check`      | Enables domain wide links check.                                                 |
|                  | `--version`              | Outputs command version.                                                         |
|                  | `--no-colors`            | Do not colorize output.                                                          |

## Examples

### Ignoring URLs

You can provide an options to ignore one or more domain/path. You can do that witha help of `-d` and `-p` options. Both options, are not required. Links that are match domain or path can be found in "ignored" results.

Both - domains and pathes compared with simple string comparison. Regular expressions or glob masks wouldn't work.

```bash
# Setup used to check "opsdroid" project documentation
#
# `deadlinks` will check URL <https://docs.opsdroid.dev/en/latest/> and all pages
# found on it (including external URLs), but not ones with domains that match
# "redis.io" or "opencollective.com" or path matching "edit/master", after
# finish it will show a list of ignored URLs.

URL=https://docs.opsdroid.dev/en/latest/
deadlinks ${URL} -n 4 -e -d redis.io -d opencollective.com  -p edit/master -s ignored
```

### Getting and Filtering Results

You can choose what to see in results: `succeed`, `failed` or `ignored` urls. Or `all`, or `none`.

```bash
# Crawling Documentation served by mkdocs and show all results (failed, ignored and succeed)
deadlinks http://127.0.0.1:8000/ -n 10 -e -p edit/master -s all

# You can save output (and see it same time) using tee command
deadlinks http://127.0.0.1:8000/ -n 10 -e -p edit/master -s all | tee results.txt

# Using saved output you can filter results by your needs, like to show failed and ignored URLs only.
awk 'NR > 3' results.txt | grep -E "ignored|failed" | less

# Or, failed local URLs
awk 'NR > 3' results.txt | grep "failed" | grep "127.0.0.1:8000" | less
```

### Concurrency and Retries

You can run crawlers concurrently (up to 10 threds), which is good thing if you checking documentation locally. You also can enable retries (its disabled by default), it means that urls failed with response code 502-504 can be checked again N times, but beware - every next retry will take twice more time!

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
