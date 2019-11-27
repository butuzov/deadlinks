# Filtering Results

You can choose what to see in results: `succeed`, `failed` or `ignored` urls. Or `all`, or `none`.

```bash
# Crawling Documentation served by mkdocs and show all results (failed, ignored and succeed)
deadlinks http://127.0.0.1:8000/ -n 10 -e -p edit/master -s all

# You can save output (and see it same time) using tee command
deadlinks http://127.0.0.1:8000/ -n 10 -e -p edit/master -s all | tee results.txt

# Using saved output you can filter results by your needs, like to show failed and
# ignored URLs only.
awk 'NR > 3' results.txt | grep -E "ignored|failed" | less

# Or, failed local URLs
awk 'NR > 3' results.txt | grep "failed" | grep "127.0.0.1:8000" | less
```
