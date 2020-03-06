# `robots.txt`

If you not familiar with a `robots.txt` - this is a file that site owners can place in the site root in order to control crawling and indexation by the search robots.
And it appears that `deadlinks` is also in some kind of a search robot. If you are a site owner it might be useful to learn about such a feature and how to use it.

We do respect `robots.txt` by default, however, there are always some edge cases when `deadlinks` users can find useful ignore robots.txt instructions. For this propose use can use a `--skip-robots-checks` option.


### Edge cases

1. `deadlinks` User-Agent isn't important enough to be included in github.com `robots.txt`, but checking a state of linked repositories or files is quite important. More of that - it was a reason why `deadlinks` was created in the first place.

2. You need to implement links checks as part of CI/CD procedure for the web site publicly not available.

3. Weird cases when sites are generating `robots.txt` on the fly, but forbid to direct access for humans (e.g. Amazon S3 Hosting).
