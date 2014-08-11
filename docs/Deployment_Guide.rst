Install the Host Operating System (Ubuntu 12.04)
================================================

For all Linux distributions, you'll need to make sure that the VM will
have access to either its own network adapter, for bridged networking,
or to a virtual network that is accessible by computers external to the
host. Also, it's best to use the "virtio" network adapter, if the host
supports it

Our deployment server is Ubuntu 12.04 virtual machine with lots of
memory and some CPU space. When asked to install additional (server)
packages, I didn't select any, because we'd probably have installed more
software than needed, which is an unnecessary burden for many reasons.

Minor Customization and Install Updates
---------------------------------------

Some things that I like to do, but that are entirely optional:

I added "NOPASSWD" to the relevant place in ``/etc/sudoers``, because
there's a lot of ``sudo`` and I don't like putting in my password all
the time.

I added the following lines to ``/etc/apt/sources.list``, commented the
pre-existing lines they replace, and also commented out the "backports"
repositories.

::

    deb http://mirror.ncs.mcgill.ca/ubuntu/ oneiric main restricted
        deb http://mirror.ncs.mcgill.ca/ubuntu/ oneiric-updates main restricted
                        

I installed the VirtualBox guest additions, which you should not do
unless you're running VirtualBox, which you shouldn't do unless you're
just testing the Web app.

Run ``$ sudo apt-get install virtualbox-guest-x11``.

I updated then restarted system.

Run ``$ sudo apt-get update``.

Run ``$ sudo apt-get upgrade``.

Run ``$ sudo init 6``.

Enable the Firewall and AppArmor
--------------------------------

I enabled the firewall, closing all ports but 22 and 80, which are
required for SSH login and HTTP access respectively.

    **Note**

    Refer to the "Firewall" chapter of the Ubuntu Server Guide at
    `help.ubuntu.com/12.04/serverguide/firewall.html <https://help.ubuntu.com/12.04/serverguide/firewall.html>`__
    for more information.

Run ``$ sudo ufw allow 22``.

Run ``$ sudo ufw allow 80``.

Run ``$ sudo ufw enable``.

I ensured there were no "unconfined" processes that AppArmor should be
confining. We recommend you confine apache2, but we do not provide
instructions at this time.

    **Note**

    Refer to the "AppArmor" chapter of the Ubuntu Server Guide at
    `help.ubuntu.com/12.04/serverguide/apparmor.html <https://help.ubuntu.com/12.04/serverguide/apparmor.html>`__
    for more information.

Run ``$ sudo apparmor_status``.

Add tmpfs for Runtime Files
---------------------------

I added an in-memory temporary directory for the Web app's temporary
files. This will give us mildly improved speed and security. The
directory will not mount properly until after you install the Web app.
Change the value of the "size" mount option according to how much memory
your server has. In ``/etc/fstab``, add:

::

    tmpfs   /usr/local/vis_counterpoint/runtime/outputs     tmpfs   size=8G,nodev,noexec,nosuid,uid=www-data,gid=www-data,mode=770     0 0

Configure the Network
---------------------

Finally, just a note about network configuration, since it was
unexpectedly retro for me. You need to edit ``/etc/network/interfaces``
so it looks something like this:

::

    iface eth0 inet static
        address 172.16.1.55
        gateway 172.16.1.1
        network 172.16.1.0
        netmask 255.255.255.0

Install the Web App and Dependencies
====================================

Install R
---------

Since the version of R included with Ubuntu 13.04 is too old, we
recommend you install R from CRAN (the Comprehensive R Archive
Network—refer to `cran.r-project.org <http://cran.r-project.org>`__ for
more information).

Add the CRAN repository mirror to ``/etc/apt/sources.list``:

::

    deb http://cran.skazkaforyou.com/bin/linux/ubuntu precise/

The `skazkaforyou.com <http://skazkaforyou.com>`__ mirror is run by iWeb
in Montréal, Canada. We recommend you choose a mirror near your server
from the list of CRAN mirrors at http://cran.r-project.org/mirrors.html.

Add the CRAN package-signing key. Run

::

    $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9

Run the following commands to install R. Note there are many
dependencies.

::

    $ sudo apt-get update
    $ sudo apt-get upgrade
    $ sudo apt-get install r-base

Finally, use R to install the ggplot2 from CRAN.

::

    $ sudo R
    (R starts)
    > install.packages("ggplot2")
    > q()
    (do not save the workspace)

Install and Configure the Web Server
------------------------------------

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

    <VirtualHost *:80>
        ServerName counterpoint.elvisproject.ca
        ServerAdmin webmaster@elvisproject.ca
        WSGIScriptAlias / /usr/local/vis_counterpoint/web-vis/django_vis/wsgi.py
        WSGIDaemonProcess counterpoint.elvisproject.ca processes=2 threads=15 display-name=%{GROUP}
        WSGIProcessGroup counterpoint.elvisproject.ca
        <Directory /usr/local/vis_counterpoint>
            Order allow,deny
            Allow from all
        </Directory>

        DocumentRoot /var/www

        Alias /robots.txt /usr/local/vis_counterpoint/web-vis/robots.txt
        Alias /humans.txt /usr/local/vis_counterpoint/web-vis/humans.txt
        Alias /favicon.ico /usr/local/vis_counterpoint/web-vis/favicon.ico
        Alias /static /usr/local/vis_counterpoint/web-vis/django_vis/static

        ErrorLog ${APACHE_LOG_DIR}/vis_error.log
        CustomLog ${APACHE_LOG_DIR}/vis_access.log common
    </VirtualHost>

Restart apache2: ``$ sudo service apache2 restart``

Configure the Web App
---------------------

For final deployment, adjust the following settings.

In ``settings.py``.

::

    'NAME': '/usr/local/vis_counterpoint/runtime/database.sqlite3',
    ...
    MEDIA_ROOT = '/usr/local/vis_counterpoint/runtime/outputs/'
    ...
    MEDIA_URL = 'http://counterpoint.elvisproject.ca/media/'
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

Set the timezone.

Make sure ``/tmp/music21`` is owned by www-data:www-data with read/write
744 permissions.

TODO: figure out how to change the "scratch files" directory without
using the ``~/.music21rc`` file.

Make the VIS temp directories:

``$ sudo mkdir /usr/local/vis_counterpoint``

``$ sudo mkdir /usr/local/vis_counterpoint/outputs``

``$ sudo chown -R www-data:www-data /usr/local/vis_counterpoint``

Use this terribly hacky way to create the sqlite3 database file:

``$ sudo passwd www-data`` (to something easy)

``$ su www-data``

``$ python manage.py syncdb`` (choose "no" when asked about
"superusers")

``$ exit``

``$ sudo service apache2 restart``

``$ sudo passwd www-data`` (to something incredibly difficult)
