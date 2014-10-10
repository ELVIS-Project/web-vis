Install the Host Operating System (CentOS 7)
============================================

For all Linux distributions, you'll need to make sure that the VM will have access to either its
own network adapter, for bridged networking, or to a virtual network that is accessible by
computers external to the host. Also, it's best to use the "virtio" network adapter, if the host
supports it

Our deployment server is a CentOS 7 virtual machine with lots of memory and some CPU space.

Configure the Firewall and Ensure SELinux Is Enabled
----------------------------------------------------

Do that. I know everyone wants to turn off SELinux, but really?

Add tmpfs for Runtime Files
---------------------------

I added an in-memory temporary directory for the Web app's temporary
files. This will give us mildly improved speed and security. The
directory will not mount properly until after you install the Web app.
Change the value of the "size" mount option according to how much memory
your server has. In ``/etc/fstab``, add:

::

    tmpfs   /usr/local/vis_counterpoint/runtime/outputs     tmpfs   size=8G,nodev,noexec,nosuid,uid=apache,gid=apache,mode=770     0 0

Configure the Network
---------------------

Do that.

Install the Web App and Dependencies
====================================

Install R
---------

Install R. Note there are many dependencies.

::

    $ sudo yum install R

Finally, use R to install the ggplot2 from CRAN.

::

    $ sudo R
    (R starts)
    > install.packages("ggplot2")
    > q()
    (do not save the workspace)

Install LilyPond
----------------

This is something you must do. Do not question The Force.

Install and Configure the Web Server
------------------------------------

NOTE: this section is still about the Ubuntu-provided HTTPD server.

We recommend you use the Apache HTTPD Web server, because we do. Refer
to the "HTTPD" chapter of the Ubuntu Server Guide at
`help.ubuntu.com/12.04/serverguide/httpd.html <https://help.ubuntu.com/12.04/serverguide/httpd.html>`__
for more information about the Apache Web server.

    **Note**

    If required, you must configure port forwarding and other router and
    hypervisor network settings before you start this procedure.

Install HTTPD.

::

    $ sudo apt-get install apache2

Edit ``/etc/apache2/sites-available/default`` to remove the
``/usr/share/doc/`` directory. We add the Counterpoint Web App later.

Edit ``/etc/apache2/apache2.conf`` to set the ``ServerName`` directive.
To test, we use `elvis-test-server <elvis-test-server>`__, and for
deployment we use
`counterpoint.elvisproject.ca <counterpoint.elvisproject.ca>`__:

::

    ServerName counterpoint.elvisproject.ca

Add the following lines to ``/etc/apache2/apache2.conf`` to improve
security:

::

    ServerSignature Off
    ServerTokens Prod

It looks like the Ubuntu-compiled version both ignores your settings and
the Apache-specified default settings, but maybe I just made a mistake.

Install VIS and the Counterpoint Web App (Virtualenv)
-----------------------------------------------------

Complete the following procedure to install the VIS Framework and the
Counterpoint Web App using the virtualenv package. We recommend this
installation method, but you may also use distribution packages (refer
to ? for more information).

Install git.

::

    $ sudo apt-get install git

Install virtualenv and other software required to build the VIS
Framework dependencies.

::

    $ sudo apt-get install python-virtualenv python-dev g++

Make the installation directory. We do not recommend you use
``/var/www``, which would allow access to the source code.

::

    $ sudo mkdir /usr/local/vis_counterpoint
    $ cd /usr/local/vis_counterpoint

Initialize then activate the CWA's virtualenv environment.

::

    $ sudo virtualenv cwa_virtualenv
    $ sudo -i
    $ source cwa_virtualenv/bin/activate

    **Note**

    Because virtualenv works by modifying environment variables, you
    must run all virtualenv-related commands in an interactive shell. If
    you ``source`` the virtual environment as a regular user, then use
    pip with ``sudo``, pip will install all packages to the system
    ``site-packages`` directory.

Update pip.

::

    $ pip install -U pip

Use pip to install the latest version of the VIS Framework and its
dependencies.

::

    pip install vis-framework

Optional. Install the VIS Framework's optional requirements. Note that,
for the Counterpoint Web App, the optional components should not be
considered optional since they greatly affect computational speed.

::

    $ pip install numexpr bottleneck

Ensure you read the output from pip, since an error may leave some
packages uninstalled.

If you wish to export "Excel"-format files from the Web App, you must
install openpyxl.

::

    $ pip install openpyxl

If you wish to export HDF5-format files from the Web App, you must
install PyTables.

::

    $ pip install cython tables

You may remove Cython after you install PyTables, since Cython is a
build requirement for PyTables, but not a runtime requirement.

Ensure you are still in the ``/usr/local/vis_counterpoint`` directory,
then clone the "web-vis" repository.

::

    $ git clone https://github.com/ELVIS-Project/web-vis.git

You may wish to checkout the tag of a specific release.

Install the "web-vis" requirements.

::

    $ pip install -r web-vis/requirements.txt

Install VIS and the Counterpoint Web App (Distribution Packages)
----------------------------------------------------------------

Complete the following procedure to install the VIS Framework and the
Counterpoint Web App using distribution-provided packages. If possible,
we suggest you use the virtualenv to install the Counterpoint Web App in
a way that does not interfere with operating system packages (refer to ?
for more information).

Install git.

::

    $ sudo apt-get install git

Install pip and other software required to build the VIS Framework
dependencies.

::

    $ sudo apt-get install python-pip python-dev g++

Use pip to install the latest version of the VIS Framework and its
dependencies.

::

    sudo pip install vis-framework

Optional. Install the VIS Framework's optional requirements. Note that,
for the Counterpoint Web App, the optional components should not be
considered optional since they greatly affect computational speed.

::

    $ sudo pip install numexpr bottleneck

Ensure you read the output from pip, since an error may leave some
packages uninstalled.

If you wish to export "Excel"-format files from the Web App, you must
install openpyxl:

::

    $ sudo pip install openpyxl

If you wish to export HDF5-format files from the Web App, you must
install PyTables:

::

    $ sudo pip install cython tables

You may remove Cython after you install PyTables, since Cython is a
build requirement for PyTables, but not a runtime requirement.

Make the installation directory. We do not recommend you use
``/var/www``, which would allow access to the source code.

::

    $ sudo mkdir /usr/local/vis_counterpoint
    $ cd /usr/local/vis_counterpoint

Ensure you are in the ``/usr/local/vis_counterpoint`` directory, then
clone the "web-vis" repository.

::

    $ sudo git clone https://github.com/ELVIS-Project/web-vis.git

You may wish to checkout the tag of a specific release.

Install the "web-vis" requirements.

::

    $ sudo pip install -r web-vis/requirements.txt

Configure the Web App
=====================

Configure the Counterpoint Web App with Apache
----------------------------------------------

Install mod\_wsgi for apache2:
``$ sudo apt-get install libapache2-mod-wsgi``

The LoadModule part is automatically added, and apache2 is restarted.

Rewrite the VirtualHost block in
``/etc/apache2/sites-available/default``:

WSGIScriptAlias first\_thing second\_thing.

The first\_thing is the URL path; use ``/`` for the root. This must not
end with a trailing slash.

The second\_thing is the path to the django\_vis directory. It must be
the full pathname, not the python module.

Add Directory to allow apache to access the vis source code.

Because I'm using the URL root, I have to add "Alias" directives for
favicon, robots, and humans.

You get something like this:

::

    <VirtualHost _default_:80>
        ServerName counterpoint.elvisproject.ca
        ServerAdmin webmaster@elvisproject.ca
        WSGIScriptAlias / /usr/local/vis_counterpoint/web-vis/django_vis/wsgi.py
        WSGIDaemonProcess counterpoint.elvisproject.ca processes=4 threads=15 display-name=%{GROUP}
        WSGIProcessGroup counterpoint.elvisproject.ca
        <Directory /usr/local/vis_counterpoint>
            # this is for Apache 2.4; version 2.2 is different
            Require all granted
        </Directory>

        DocumentRoot /var/www

        Alias /robots.txt /usr/local/vis_counterpoint/web-vis/robots.txt
        Alias /humans.txt /usr/local/vis_counterpoint/web-vis/humans.txt
        Alias /favicon.ico /usr/local/vis_counterpoint/web-vis/favicon.ico
        Alias /static /usr/local/vis_counterpoint/web-vis/django_vis/static

        ErrorLog /var/log/httpd/cwa_error.log
        CustomLog /var/log/httpd/cwa_access.log common
    </VirtualHost>

Restart apache2: ``$ sudo service apache2 restart``

Configure the Web App
---------------------

For final deployment, adjust the following settings.

In ``settings.py``.

::

    ...
    MEDIA_ROOT = '/usr/local/vis_counterpoint/runtime/outputs/'
    ...
    ALLOWED_HOSTS = ['counterpoint.elvisproject.ca']
    ...
    DEBUG = False
    ...
    SECRET_KEY = ''  # 40 pseudo-random characters

Uncomment the following lines in ``wsgi.py``.

::

    import imp
    try:
        imp.find_module('django_vis')
    except ImportError:
        import sys
        sys.path.insert(0, '/usr/local/vis_counterpoint/web-vis')

If you installed VIS and the CWA with virtualenv, uncomment the
following lines from ``wsgi.py``.

::

    activate_this = '/usr/local/vis_counterpoint/cwa_virtualenv/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))

Other Things
------------

Make sure ``/tmp/music21`` is owned by apache:apache with read/write
744 permissions. (NB: probably unnecessary, since systemd takes care of this)

TODO: figure out how to change the "scratch files" directory without
using the ``~/.music21rc`` file.

Prepare the VIS runtime directories and the database. It's a terrible hack.

::
    $ sudo mkdir /usr/local/vis_counterpoint/web-vis/runtime
    $ sudo chown apache:apache /usr/local/vis_counterpoint/runtime
    $ sudo semanage fcontext -a -t httpd_sys_rw_content_t "/usr/local/vis_counterpoint/runtime(/.*)?"
    $ sudo restorecon -v /usr/local/vis_counterpoint/runtime/*

    $ sudo passwd apache
    ... to something easy
    $ su apache
    $ source /usr/local/vis_counterpoint/cwa_virtualenv/bin/activate
    $ python manage.py syncdb
    ... choose "no" when asked about a superuser account
    $ exit
    $ sudo passwd apache
    ... to something incredibly difficult

    $ sudo systemctl restart httpd
