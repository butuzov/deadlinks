# Docker Images

You can use `deadlinks` as a dockerized application, this approach is highly desirable if you not willing to install python package or you want to use it in continues integration pipeline.

Please visit our [Docker Hub](https://hub.docker.com/r/butuzov/deadlinks) and pick version you like to use (`dev` - bugs bleeding edge, `latest` - most resent release, `a.b.c` - version release).


```bash
# you can run it as container
docker run --rm -it --network=host docker.io/butuzov/deadlinks:0.1.0 --version
> deadlinks: v0.1.0

# or create an alias dor deadlinks in your .bash_profile or .bashrc
alias deadlinks='docker run --rm -it --network=host docker.io/butuzov/deadlinks:0.1.0 $@'
deadlinks --version
> deadlinks: v0.1.0
```

