Introduction
============

This prototype demonstrates the basic building blocks of the NED.
Primary features of this prototype include (Fig. [fig:proto]):

-   remote attestation of NED using a remote verifier and
    attestation-enabled strongSwan client;

-   secure and trusted dataplane using strongSwan and Integrity
    Measurement Architecture (IMA);

-   web-based user authentication (username and password);

-   user service graph (SG) parsing and dataplane setup;

-   automated instantiation of a user’s Trusted Virtual Domain (TVD)

    -   Personal Security Controller (PSC) instantiation;

    -   instantiation of Personal Security Applications (PSAs) in the
        service graph;

    -   customised configurations for the IPtables PSA.

External services (the PSA repository, User Profile repository and the
Security Policy Manager) are not included as part of this prototype.
These are to be developed as part of the activities of Work Packages 4
and 5. In this prototype, PSA images, service graphs and policies are
all cached on the NED, some configuration files needs to be changed 
locally, since the current development situation.

TrustedGRUB2 now does not support EFI boot method, in this case, only old legacy/mbr booting mechanism is supported. Meanwhile, need to use standard partition mode when creating boot partition.

![Prototype instantiation of the NED architecture, hosting a simple TVD
[fig:proto]](images/figure.png)

The key NED components are described below (for full details, please
refer to the architecture document D2.3.1):

**Personal Security Controller Manager (PSCM)** is a web-based frontend to the NED and is responsible for
    authenticating the user. Upon successful user authentication, the
    PSCM sends a request to the Trusted Virtual Domain Manager (TVDM) to
    instantiate the user’s security. It is accessible from an ordinary
    client web browser. In the future, the user experience may be
    improved by using a captive portal.

**Trusted Virtual Domain Manager (TVDM)**   is a privileged component within the NED which is able to create and
    orchestrate trusted virtual domains (TVD). A TVD is a logical
    security domain given to an individual tenant, providing traffic
    isolation and application isolation. The TVDM enforces the isolation
    between TVDs by controlling the NED’s virtual switch. OpenvSwitch
    was used as the software switch in this prototype and is the
    keystone for providing multi-tenancy and isolation. Whilst TVD is a
    term which is agnostic to specific technologies, in this version of
    the prototype a user TVD consists of a set of small virtual
    machines. There are also parallel efforts within the project to use
    Docker (Linux) containers within a TVD, which provide less
    computational and space overheads.

**Personal Security Controller (PSC)**  is the first entity created in a user’s TVD. It is responsible for
    parsing the service graph **(SG)** and informing the TVD about which
    computational resources are required. Once the PSA environments are
    instantiated, the PSC controls the PSAs at runtime over a private
    control network within the TVD. It also provides a web-based user
    interface in the form of a dashboard that allows the user to control
    their PSAs and see their status.

**Personal Security Application (PSA)**   is an environment consisting of all the dependencies required to
    running a personalised security application. It includes a REST
    server which allows it to be configured and controlled. In this
    version of the prototype, a PSA is a virtual machine image (raw IMG
    file) which has two virtual network interface cards (vNICs) for the
    dataplane (ingress/egress) and a third vNIC for the control network
    (where the HTTP REST server listens on).

NED project structure
---------------------



---------------------------------------------------------------------
  
             **(PSA)**                    All software that is deployed in the PSA environment
             **(PSC)**                    All software that is deployed in the PSC environment
            **(PSCM)**                     The PSCM software required for user authentication
            **(TVDM)**                     The TVD Manager, which includes the service graphs
         **(strongswan)**          The IPsec service that provides secure and trusted network channels
        **(TrustedGRUB2)**                The required TCG bootloader to support Measured Boot
         **(dataSchema)**                 Various examples of service graph and profile formats
     copy\_psa\_sw\_to\_vm.sh            Utility to copy PSA software into a particular VM image
    copy\_psc\_sw\_from\_vm.sh          Debug utility to dump software from a particular VM image
    copy\_psa\_sw\_from\_vm.sh          Debug utility to dump software from a particular VM image
     copy\_psc\_sw\_to\_vm.sh            Utility to copy PSC software into a particular VM image
           default.conf                    Configuration file that specifies defaults for DHCP
             pscm.conf                               Configuration file for the PSCM
             setup.sh                       Main executable that starts all the NED services
             test.bats                 System-wide tests to check correctly working functionality
             tvdm.conf                               Configuration file for the TVDM
           userNet.conf               Configuration file for defining IP ranges for user dataplanes
------------------------------------

Usage scenario
--------------

The supported topology for the basic NED is illustrated in Figure
[fig:topology], where a commodity PC running the NED software can be
used in conjunction with multiple access points.

The usage scenario workflow for this prototype version is as follows:

1.  User is connected to the NED using either:

    -   A secure and trusted channel (using the strongSwan IPsec Linux
        client provided by SECURED)

    -   Over an insecure and untrusted channel (assumes a direct
        physical and secure connection)

2.  User accesses the PSCM of the NED using a web browser

3.  User authenticates with an existing profile using a username and
    password. These profiles are described in Section  [userprofiles]

4.  On successful authentication, the NED displays an authorisation
    confirmation

5.  Once the user’s Personal Security Controller (PSC) is ready, the
    PSCM of the NED redirects the user’s browser to the dashboard of
    their own personal PSC

6.  When the user’s PSAs have started, the PSC returns a confirmation to
    the user about the status of the service graph

7.  The user can press a number of buttons, such as **start**, **stop**,
    **get logs**, which provides some basic control of the PSAs. Figure
    [fig:pscgui] shows a screenshot of this page.

[fig:topology] ![Supported and tested topology for the basic
NED.](images/topology.png "fig:")

[fig:pscm] ![Password-based authentication at the NED using an ordinary
web browser](images/pscm.png "fig:")

[fig:pscm2] ![Successful authentication with the
NED](images/pscm2.png "fig:")

[fig:pscgui] ![PSC dashboard for viewing and controlling PSAs
](images/pscgui.png "fig:")

User sessions at present development do not expire. This will be
implemented in the future, based on either network inactivity, or
through the means of a user interface button that stops the session.

Setup guide and package dependencies
====================================

CentOS is the fully supported GNU/Linux distribution for [^1], although
some parts can work on other distributions with the same packages.

Install package dependencies
----------------------------

**Install the packages for CentOS (tested 22.9.2015 with CentOS 7 gnome desktop version):**

    # yum install python-pip python-gunicorn curl unzip virt-manager wget rsync qemu-kvm gcc gmp-devel unzip trousers trousers-devel java-1.7.0-openjdk java-1.7.0-openjdk-devel python-devel libguestfs-tools libvirt virt-install net-tools bzip2 
      
Install openvswitch for CentOS with this guide: https://n40lab.wordpress.com/2015/01/25/centos-7-installing-openvswitch-2-3-1-lts/

Install openvswitch for CentOS from openvswitch direcotry

	# cd BASE_DIR/ned/openvswitch
	# yum localinstall openvswitch-2.3.1-1.x86_64.rpm

Then use pip to get the latest Python modules:

     # pip install falcon requests trollius lxml futures python-keystoneclient

**Install the packages for Ubuntu (tested 21.9.2015 with Ubuntu 14.04 LTS):**

    # apt-get install python-pip curl unzip virt-manager wget openvswitch-switch python-futures rsync qemu gcc unzip trousers openjdk-7-jdk libguestfs0 libguestfs-tools python-keystoneclient

Then use pip to get the latest Python modules:

     # pip install falcon requests gunicorn trollius lxml json2xml dicttoxml termcolor

Download and setup PSC and PSAs
--------------------------------

Download PSC and PSAs to /var/lib/libvirt/images manually from https://vm-images.secured-fp7.eu/images/ or from PSAR (not available at the moment)

(vm-images.secured-fp7.eu is not registered, need to put `130.192.56.44 vm-images.secured-fp7.eu` into `/etc/hosts/`, then open the mentioned url address)

Currently, no psa/psc image is in the repository, need to download them from the other ned.

Run following commands to set up PSAs and PSC in ned folder

    # systemctl start libvirtd
    # bash copy_psa_sw_to_vm.sh
    # bash copy_psc_sw_to_vm.sh

Finally, you must decide how the users will connect to the NED. You have
two options: only or without . Note that the prototype does not allow
mixed access connections (this is an improvement planned for T3.3).

IPsec-only connections (remote NED scenario)
=======================================

If you want all users to connect to the NED over , then you can just
execute the following script on the NED (as root user):

    # /usr/share/openvswitch/scripts/ovs-ctl start 
    # bash setupIPSEC.sh **your_internet_facing_interface**

Where **your_internet_facing_interface** could have been an appropriate internet connected interface, such as `eth0`,
for example.

IPsec-less connections (home/IoT scenarios)
======================================

Alternatively, if the user is in a private closed (and trusted)
environment (home scenario, IoT, etc) and the NED is the immediate
gateway, then the user will need a DHCP service to provide an IP on the
dataplane. In the current version of the prototype, this is done by the
NED itself, but in future it could support an external DHCP server. To
allow access to the NED without using you will need to specify the
user-facing Ethernet port as well:

     user@ned:~$ sudo ./setup.sh <your_internet_facing_interface> <user_facing_port>

Example: `sudo ./setup.sh eth0 eth1`

The user will then be able to access the PSCM from outside the NED at
the following default location: <http://10.2.2.253:8080/login>. 
At the moment, this cannot be configured to a different address, 
but will enabled as a configuration file option in the future.

There may be a captive portal in future to redirect to
automatically bring new users to this page. 

IPsec with IMA, remote verifier and the NED RA agent
====================================================

The following instruction is based on CentOS7 minimal installation. Make
sure the TPM is enabled in the BIOS of the NED. Clone and set up the
verifier on a machine which is accessible by both the user terminal and
the NED.

Project available here:

<https://gitlab.secured-fp7.eu/secured/verifier>

The code is used to create a Third-Party Verifier with OpenAttestation
v1.7 and remote attestation tools developed by TorSec Group in
Politecnico di Torino.

![Overview of trusted channel support (full details in
D3.2.1).](images/trusted_channel.png)

Verifier setup
--------------
Please check the [README.md](https://gitlab.secured-fp7.eu/secured/verifier) in the SECURED/Verifier repository.

Building remote attestation client for end users
----------------------------------------------------

Please check the [README.md](https://gitlab.secured-fp7.eu/secured/app/) in the SECURED/App repository.

NED setup
---------

The script `ipsec.sh` contains all the commands to create a
SECURED-compliant virtual NED. It is supposed to put the configuration
file (i.e., `ima-policy`) and the `ipsec` directory in the `BASE_DIR`
directory. The `ipsec` directory contains the configuration files used
to create an tunnel with the users.

Now perform the following steps:

-   go back to the NED, enter the strongSwan directory and run the
    following as root

          root@ned# bash /BASE_DIR/ned/strongswan/ipsec.sh $verifierIP $nedIP $nedHostName

-   reboot;

Or configure the ned step by step:

-	download the ClientInstallForLinux.zip to register the machine to the verifier;
    
    	 # wget http://verifier/ClientInstallForLinux.zip
    	 # unzip ClientInstallForLinux.zip
    	 # cd ClientInstallForLinux
    	 # sh genera-install.sh
    	 
-   install the compiled strongswan package

		# yum localinstall /BASE_DIR/ned/strongswan/strongswan-5.3.2-1.el7.x86_64.rpm
	
-	open port for ipsec to communicate with userterminal

		# firewall-cmd --permanent --add-port=500/udp
    	# firewall-cmd --permanent --add-port=4500/udp
		# firewall-cmd --add-port=4500/udp
		# firewall-cmd --add-port=500/udp
		
- generate certificates for CA, peer, and client;

		# /usr/libexec/strongswan/pki --gen > caKey.der
		# /usr/libexec/strongswan/pki  --self --in caKey.der --dn "C=CH, O=strongSwan, CN=strongSwan CA" --ca --outform pem > caCert.crt
		# /usr/libexec/strongswan/pki  --gen > peerKey.der
		# /usr/libexec/strongswan/pki --pub --in peerKey.der | /usr/libexec/strongswan/pki --issue --cacert caCert.crt --cakey caKey.der --dn "C=CH, O=strongSwan, CN=ned" --san xxx.xxx.xxx.xxx > peerCert.der
    
    xxx.xxx.xxx.xxx is the ip of the ned, which is needed for the Android strongswan application.

-	copy each certificate to the corresponding folders in both ned and userterminal;

		# cp caCert.crt /etc/strongswan/ipsec.d/cacerts
		# cp peerCert.der /etc/strongswan/ipsec.d/certs/
		# cp peerKey.der /etc/strongswan/ipsec.d/private/
		# scp caCert.crt root@userterminal:/etc/strongswan/ipsec.d/cacerts

- 	read PCR0 from the TPM and register it with the configure script to the verifier;

	the file storing the PCR values is called 'pcrs', it is stored in `/sys/class/misc/tpm0/device/pcrs`.

		# cat /sys/class/misc/tpm0/device/pcrs | sed "s/ //g"

	you should see the output as:
	
	```bash
	PCR-00:062AC3E7639E58B5F8919743C9AD1172A6A0CE2C
	PCR-01:B2A83B0EBF2F8374299A5B2BDFC31EA955AD7236
	PCR-02:B2A83B0EBF2F8374299A5B2BDFC31EA955AD7236
	PCR-03:B2A83B0EBF2F8374299A5B2BDFC31EA955AD7236
	PCR-04:B35D3B46BB9C22038A8C6C5CF695690F5AAF0E38
	PCR-05:239443EC48A427DDE7CDED2A21CBDB45EC327BDD
	PCR-06:B2A83B0EBF2F8374299A5B2BDFC31EA955AD7236
	PCR-07:B2A83B0EBF2F8374299A5B2BDFC31EA955AD7236
	PCR-08:0000000000000000000000000000000000000000
	PCR-09:0000000000000000000000000000000000000000
	PCR-10:CFB2CCC82A6779E608CBF578AB803251C49DF047
	PCR-11:0000000000000000000000000000000000000000
	PCR-12:0000000000000000000000000000000000000000
	PCR-13:0000000000000000000000000000000000000000
	PCR-14:0000000000000000000000000000000000000000
	PCR-15:0000000000000000000000000000000000000000
	PCR-16:0000000000000000000000000000000000000000
	PCR-17:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
	PCR-18:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
	PCR-19:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
	PCR-20:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
	PCR-21:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
	PCR-22:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
	PCR-23:0000000000000000000000000000000000000000
	```
	afterwards, need to input the PCR0 value to the verifier as shown in [verifier README step 7](https://gitlab.secured-fp7.eu/secured/verifier/blob/devel/README.md "verifier").

-	to attest the certificate, a trick is needed, to create a temp user, and assign the certificate with him, then set the ima policy to attest the files belonging to this user;

	read the temp user's uid using "id -u temp" as tUID.

		# adduser -s /bin/false temp
		# chown temp /etc/strongswan/ipsec.d/certs/peerCert.der
		# mkdir /etc/ima
		# cp BASE_DIR/strongswan/ima-policy /etc/ima
		# echo -e "measure fowner=$tUID" >> /etc/ima/ima-policy

- 	copy the ipsec configuration files in the ipsec directory to `/etc/strongswan/`

	ipsec.secrests is ready for use, you can change the password inside if you want. ipsec.conf needs to be modified based on specific settings, especially the ip addresses.
	
		# cp /BASE_DIR/ned/strongswan/ipsec/ipsec.conf_example /etc/strongswan/ipsec.conf
		# cp /BASE_DIR/ned/strongswan/ipsec/ipsec.secrets_example /etc/strongswan/ipsec.secrets
		# cp /BASE_DIR/ned/strongswan/ipsec/oat-attest.conf /etc/strongswan/strongswan.d/charon/oat-attest.conf

	you can follow the descriptions in [strongswan ipsec.conf](https://wiki.strongswan.org/projects/strongswan/wiki/ConnSection) to customise your ipsec configurations.

-	run strongswan;
		
		# systemctl start strongswan
		# systemctl enable strongswan
		# reboot

TrustedGRUB2
=============
-	download `TrustedGRUB2-master.zip` and unzip the archive; 
-	go into the unzipped directory, and execute _autogen.sh_ script;
		
		# ./autogen.sh
		
- 	configure the installation;

		# cd /BASE_DIR/ned/TrustedGRUB2-master/
		# ./configure --prefix=INSTALLDIR
		# make  
		# make install 
		
- 	install TrustedGRUB2 into the device 

		# ./INSTALLDIR/sbin/grub-install --directory=INSTALLDIR/lib/grub/i386-pc /dev/sda
   	   
-	copy the `grub.cfg` from `/boot/grub2` into `/boot/grub`, otherwise need to manually setup the kernel and initrd when booting.


User profiles
=============

Once at the login page, you can login with one of the following test
profiles:

-   **user1:** when logging in will start a PSA which should block all
    traffic to [www.polito.it](www.polito.it)

-   **user2:** when logging in will start a PSA which should block all
    traffic to [www.upc.edu](www.upc.edu)

Both accounts have the following password: **secuser**

Tests
=====

If a problem occurs, unit tests can be applied to all the major
components. For functional testing the BATS (Bash Automated Testing
System) framework is needed. To install it:

    user@ned:$ git clone https://github.com/sstephenson/bats.git
    user@ned:$ cd bats
    user@ned:# sudo ./install.sh /usr/local
    user@ned$ cd ..

Then to perform the tests (must be root or else it will fail):

    root@ned:# bats ./test.bats

You should then get an output for tests against each component, such as:

    - Test PSCM reachability
    - Test TVDM reachability
    - Test PSCM authentication
    - Test PSC's VM reachability

If you wish to test the browser interface from inside the NED you can
use the following command (replace firefox with your favourite browser,
e.g. lynx):

    root@ned:# ip netns exec pscmNs firefox 10.2.2.253:8080/login		
Credits
=======

Lead developers:

-   Francesco Ciaccia (BSC)

-   Roberto Bonafiglia (POLITO)

Remote Attestation and developers:

-   Roberto Sassu (POLITO)

-   Tao Su (POLITO)

Documentation, testing and validation:

-   Adrian L. Shaw (HPLB)

-   Jarkko Kuusijarvi (VTT)

[^1]: This platform has been selected because it includes an up-to-date
    database with the signatures of all the supported software, which is
    a prerequisite for the remote attestation feature.
