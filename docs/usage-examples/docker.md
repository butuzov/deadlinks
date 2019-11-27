# Docker Images

You can use `deadlinks` as a dockerized application, this approach is highly desirable if you not willing to install python package or you want to use it in continues integration pipeline.

Please visit our [Docker Hub](https://hub.docker.com/r/butuzov/deadlinks) and pick version you like to use:
* `dev` - bugs bleeding edge,
* `latest` - most resent release
* `a.b.c` - version release

## Running Container

You can run deadlinks container in your shell

```bash
docker run --rm -it --network=host docker.io/butuzov/deadlinks:0.1.0 --version
> deadlinks: v0.1.0
```

Or you can create alias and add it to your `.bashrc`

```
# or create an alias dor deadlinks in your .bash_profile or .bashrc
alias deadlinks='docker run --rm -it --network=host docker.io/butuzov/deadlinks:0.1.0 $@'
deadlinks --version
> deadlinks: v0.1.0
```

## Local Checks

Since version `0.2.0`  (`FIXME: Unreleased at the moment`) you can specify document root with `--root` option and ask for internal checks, in case if you going to use docker image, you need to share volumes with container.

```bash
# An example of the local checks running.
docker run --rm -it --network=host -v "/projects/gobyexample/public:/docs" \
  docker.io/butuzov/deadlinks:dev internal --root /docs
```
