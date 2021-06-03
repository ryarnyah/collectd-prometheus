# collectd-prometheus

A collectd Python plugin to read Prometheus metrics endpoints

## Installation

1. Download `collectd-prometheus.py` into a folder, e.g.
   `/usr/lib/collectd/python`
1. Download `requirements.txt` and install the dependencies required:
   ```terminal
   # pip install -r requirements.txt
   ```
   You need to check which Python version your collectd is built against to
   know which python/pip binary to use. So e.g. with Debian:
   ```terminal
   $ dpkg -S python.so | grep collectd
   collectd-core: /usr/lib/collectd/python.so
   $ ldd /usr/lib/collectd/python.so | grep python
   libpython2.7.so.1.0 => /usr/lib/x86_64-linux-gnu/libpython2.7.so.1.0 (0x00007f953a5c2000)
   $
   ```
   which uses Python 2.7 still so I need to use `pip2` when installing the
   dependencies.

## Usage
1. Create a collectd configuration e.g.
   `/etc/collectd/collectd.conf.d/prom-service.conf`
```apache
LoadPlugin python
<Plugin python>
    ModulePath "/usr/lib/collectd/python" # This is the folder we downloaded collectd-prometheus.py into before
    Import "collectd-prometheus"
    <Module "collectd-prometheus">
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
