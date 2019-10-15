# Ignoring URLs

You can provide an options to ignore one or more domains or pathes, and you can do that with a help of the `-d` and `-p` options (`--domains` and `--pathes` if full version). Both options, are not required. Links that match domain or path are placed  into "ignored" results group.

Both - domains and pathes compared via simple string comparison, regular expressions or glob masks aren't  working.


```bash
# Setup used to check "opsdroid" project documentation
#
# `deadlinks` will check URL <https://docs.opsdroid.dev/en/latest/> and all pages
# found on it (including external URLs), but not ones with domains that match
# "redis.io" or "opencollective.com" or path matching "edit/master", after
# crawling - programm will show a list of ignored URLs.

URL=https://docs.opsdroid.dev/en/latest/
deadlinks ${URL} -n 4 -e -d redis.io -d opencollective.com  -p edit/master -s ignored

```
