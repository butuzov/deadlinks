# Performing Local Checks

If your static site generator doesn't have a feature of serving files, you can ask `deadlinks` to check directory with files instead.

```bash
# to trigger local checks ask to check internal website and provide --root parameter
deadlinks internal --root /path/doc/document-root/

# you can emulate that files are served from the directory by adding directory name.
# please keep in mind to add trailing slash in this case.
deadlinks internal/docs/ --root /path/doc/document-root/
```
