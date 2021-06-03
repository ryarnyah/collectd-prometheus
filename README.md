# collectd-prometheus

A collectd Python plugin to read Prometheus metrics endpoints

## Installation

1. Find out which version of Python your collectd is built against to know
   which python/pip binary to use. So e.g. with Debian:
   ```terminal
   $ dpkg -S python.so | grep collectd
   collectd-core: /usr/lib/collectd/python.so
   $ ldd /usr/lib/collectd/python.so | grep python
   libpython2.7.so.1.0 => /usr/lib/x86_64-linux-gnu/libpython2.7.so.1.0 (0x00007f953a5c2000)
   $
   ```
   which uses Python 2.7 still so I need to use `pip2` when installing the
   dependencies.
1. Install `collectd-prometheus`:
   ```terminal
   # pip2 install collectd-prometheus
   ```

## Usage
1. Create a collectd configuration e.g.
   `/etc/collectd/collectd.conf.d/prom-service.conf`
```apache
LoadPlugin python
<Plugin python>
    Import "collectd_prometheus"
    <Module "collectd_prometheus">
       Interval 30 # How often to scrape metrics. This is the default, can be omitted
       <Process>
           Process "mycoolservice" # Name this instance, e.g. after what service you're scraping
           Protocol "http" # This is default, can be omitted
           Host "127.0.0.1" # This is default, can be omitted
           Port "8080" # This is default, can be omitted
           Filter "only|these" # A regex which matches the names of the metrics you only want to include
           Filter "metrics" # You can even specify multiple regexes
       </Process>
       # Scrape another another service as well, e.g.
       <Process>
           Process "anothercoolservice"
           # This time we use the defaults, except Port
           Port "8081"
       </Process>
    </Module>
</Plugin>
```

## Using a virtualenv
In Python, using a virtual environment [is the
recommended](https://docs.python.org/3/tutorial/venv.html) way to isolate your
applications dependencies from other applications. To use a virtualenv with
collectd we have to create one, activate it, install the dependencies into it
and then copy the `collectd-prometheus.py` module into it.

1. Using the steps listed [Installation](#installation) figure out which Python version
   collectd uses.
1. If python3 use `venv` which is included in Python 3. When using Python 2.7,
   we have to [install
   virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) which
   can be packaged in your OS/distribution (`python-virtualenv` in Debian) or
   you install it manually, see the linked documentation.
1. Create your virtualenv where you want to store it, e.g:
   ```terminal
   # python -m virtualenv /usr/lib/collectd/prom
   ```
1. Activate it and install dependencies, e.g.:
   ```terminal
   # source /usr/lib/collectd/prom/bin/activate
   (prom) # pip install -r requirements.txt
   ```
1. Find your virtualenvs site-packages folder, e.g:
   ```terminal
   # find /usr/lib/collectd/prom/ -type d -iname "site-packages"
   /usr/lib/collectd/prom/lib/python2.7/site-packages
   ```
1. Copy in `collectd-prometheus.py` to the directory we found, e.g:
   directory, e.g:
   ```terminal
   # cp collectd-prometheus.py /usr/lib/collectd/prom/lib/python2.7/site-packages
   ```
1. Configure collectd to look for `collectd-prometheus.py` and it's
   dependencies in the directory that you found in step 5. E.g:

   ```apache
   LoadPlugin python
   <Plugin python>
       ModulePath "/usr/lib/collectd/prom/lib/python2.7/site-packages" # Right here
       Import "collectd-prometheus"
   […]
   ```
