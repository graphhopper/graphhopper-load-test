# Load testing

This tool will allow you to load test the GraphHopper API. It uses [Locust](https://locust.io) to
run a swarm of users on the infrastructure.
The business logic of what endpoints to hit and with what parameters is saved in `personas/`.

## Build

If you have admin permissions to `graphhopper/load-testing`, you can run `make push` to build and
push the Docker image to Docker Hub.

Otherwise you can run `make build` to build the Docker image without pushing it.

## Run

### Docker or no Docker?

This application is mainly written in Python. If you don't want to deal with Python's packaging,
you can use Docker. In this case prepend all the commands that you see below with 
`docker run graphhopper/load-testing`. So if you see `./run -h`, you can use
`docker run graphhopper/load-testing ./run -h` to run the command.

If, on the other hand, you're familiar with Python and its packaging system, you can first set up
your environment as you see fit (e.g. using virtual environment). The only thing that is required
is to install the packages in `requirements.txt`, usually done with `pip install -r requirements.txt`.

### Get current version

To print the current version of the app, run:

    ./run --version

### Get help

Run the following to see the help page on how to run this tool.

    ./run -h

### Basic usage

    ./run -p vrp -d 10s -u 10 <example.com>

In its most basic form, all you need to do to start a load testing session, is to configure:
* Persona used with `-p`. E.g. for VRP, use `vrp`. Check the help (`./run -h`) to see all the
  available personas.
* Duration with `-d`, e.g. `300s` for 300 seconds or `20m` for 20 minutes.
* The number of users with `-u`. In general, each user will run the associated task every second or
  so. Technically, the wait time is [`random.expovariate`](https://docs.python.org/3.7/library/random.html#random.expovariate)(1),
  meaning an average of 1 second. Though VRP is more complex as it does an optimize and then
  solutions. The ramp-up of users will be instantaneous as the ramp-up is set to the number of
  users.
* The base URL. This is where the base of the service is deployed. A few examples:
  * If you're testing the matrix service at `/matrix` on HTTPS, then the base URL would be
    `https://example.com/`.
  * If you're testing the VRP service at `/api/1/vrp` on port 8080, then the base URL would be
    `http://example.com:8080/api/1`.
* [optional] set the API key using `--api-key [key]`

### Three ways of running

There are currently three ways of running a load test. This is not ideal, the reasons are purely
technical and it would be best to have just one, but here we are.

* Using `./run`. This is mostly the best way. It is a wrapper around Locust. In this variation, it
  runs the `locust` CLI command, setting the needed parameters and environment variables for us.
* Using `./run --custom-output`. This one uses the Python programmatic API to the Locust library,
  so it's the most extensible option. Currently we have our own custom output, for times when you
  don't want to get all the output of intermediate results.
* Using `locust` (`docker run graphhopper/load-testing locust`). This is for times when you want to
  use some Locust functionality that is not yet included in `./run`. If this happens, we should
  probably add support for the missing feature in the `./run` command.

### Debugging errors

If you want more information about failed requests, use the `--debug` switch and it will display the
actual error for every error that happens in real time.

### Configuring VRP

VRP has some additional configurations that we can use when running a load test. You can set the
likelyhood of using TomTom data with `--vrp-tomtom-probability`,
set VRP profiles with `--vrp-profiles`, set the max VRP vehicle profiles with `--vrp-max-profiles`
and set the max locations with `--vrp-max-locations`.

Read more about it on the `./run -h` help page.

### Running in master/worker mode

Most of the times, running one instance of the load test is not enough. I can reliable use around
300 users per running instance, it seems to not handle more. So in order to run with more users, we
need to run Locust in a master/worker configuration.

You run the master once and then the workers how many times you want, I go for `users/300`. For
example, if I want to do 1800 users, I will run 6 workers (6 * 300 = 1800).

    # master
    ./run --debug -p vrp -d 600s -u 600 --master --expect-workers=2 <example.com>

    # worker
    ./run --debug -p vrp --vrp-max-locations 5 --worker --master-host=<master-ip> <example.com>

The `<master-ip>` can be `127.0.0.1`, if you're running other instances on the same machine, which
we do a lot.
