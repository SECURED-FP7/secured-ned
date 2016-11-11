# Software for the PSC execution environment

These files or functionality need to be part of the PSC execution environment and always running

# Notes about mobility Configuration
This document describes the necessary steps to configure the mobile environment. We assume the NED is running and properly configured, but we will update the IPSec tunnel configuration though.

The aim of the experiment is to make handover by building a tunnel between the Mobile client and the NED using a wireless link, at a given point in time, the mobile node will move to a different location, thus forcing the handover to another secured access point. Once in associated to the other access point, belonging to a different IP subnetwork, the enduser will not experience any connection disruptions.

For this to work, the mobile node will periodically check the wireless signal power of secured compliant access points. Handover will be enforced when the PSC deems it appropriate, pointing out the best alternative among all the present options. Currently the criteria is solely  based on the signal level.

Then the tasks performed by the Mobile Node are:

1. Tear down the IPSec tunnel
2. Start the handover process
3. Establish the new tunnel
4. Continue the signal power reporting

For testing purposes, we added a REST method in the PSC by which we are able to force the handover. Particularly, it can be invoked by sending a GET request to:
```
http://10.2.2.251:8080/forceHandOver
```

## Scenario
It is necessary to have two access points with DHCP and a mobile node using NetworManager. We assume that the Access Points are located in different subnetworks, but both have connection visibility to the NED. Particularly, both access points need to be connected to the NED NAT interface.

### Configuration of strongswan in the NED
We assume that you followed the installation process is specified in [README.md](/secured/app/blob/master/README.md) in strongswan’s directory of NED repository.

In NED add the following lines in ```/etc/strongswan/ipsec.conf``` 
```
conn secured
     left=172.18.0.10 #IP of the NED
     leftid="C=CH, O=strongSwan, CN=ned-1" #the DN that you use to generate the certificate
     leftsubnet=0.0.0.0/0
     leftfirewall=yes
     leftauth=pubkey
     leftcert=peerCert.der #the name of the generated certificate on the ipsec.d/certs dir
     right=%any
     rightsourceip=10.2.2.2/24
     rightdns=8.8.8.8
     rightauth=eap-md5
     rightsendcert=never
     auto=add
```

In client add the following lines in ```/etc/strongswan/ipsec.conf```
```
conn secured1 #connection of AP1 
        ikelifetime=1200s
        margintime=1100s
        left=192.168.150.10  # IP of the client, be careful because DHCP assigned dynamic IP
        leftid=user1         # user to use on the eap authentication (the one configured on both ipsec.secrets files)
        leftfirewall=yes
        leftfirewall=yes
        leftauth=eap-md5
        leftsourceip=10.2.2.2
        right=172.18.0.10  #IP of the NED
        rightid="C=CH, O=strongSwan, CN=ned-1"#the DN that you use to generate the certificate 
        rightauth=pubkey
        rightsubnet=0.0.0.0/0
        auto=add

conn secured2 #connection of AP2
        ikelifetime=1200s
        margintime=1100s
        left=192.168.200.10  #IP of the client, be careful because DHCP assigned dynamic IP
        leftid=user1  #the one configured on both ipsec.secrets files
        leftfirewall=yes
        leftauth=eap-md5
        leftsourceip=10.2.2.2
        right=172.18.0.10  #IP of the NED
        rightid="C=CH, O=strongSwan, CN=ned-1"#the DN that you use to generate the certificate 
        rightauth=pubkey
        rightsubnet=0.0.0.0/0
        auto=add
```

```/etc/strongswan/ipsec.secrets``` has to be modified in both NED and mobile client
```
# /etc/ipsec.secrets - strongSwan IPsec secrets file

: RSA peerKey.der "172.18.0.10"

user1 : EAP "abcd1234"
```

Only the NED needs to generates the certificate. You need to put the
certificate of the NED inside the ```ipsec.d/certs``` directory, the private
key on the ipsec.d/private directory and the ca certificate on the ```ipsec.d/cacerts```.

And then we need to execute
```bash
/usr/libexec/strongswan/pki  --gen > caKey.der
/usr/libexec/strongswan/pki  --self --in caKey.der --dn "C=CH, O=strongSwan, CN=strongSwan CA" --ca --outform pem > caCert.crt
/usr/libexec/strongswan/pki  --gen > peerKey.der
/usr/libexec/strongswan/pki --pub --in peerKey.der | /usr/libexec/strongswan/pki --issue --cacert caCert.crt --cakey caKey.der \
   --dn "C=CH, O=strongSwan, CN=ned-1" --san 172.18.0.10 > peerCert.der
cp caCert.crt  /etc/strongswan/ipsec.d/cacerts
cp peerCert.der /etc/strongswan/ipsec.d/certs/
cp peerKey.der /etc/strongswan/ipsec.d/private/
```

On the client side you need only to put the ca certificate on the directory ```ipsec.d/cacerts```.

When the client starts the connection with IPSEC will get the IP ```10.2.12.2```.
For the NED you should configure on interface with the IP ```10.2.2.1``` and
configuring the proper route to forward the packets through that network.

## Updating the legacy PSC VM

First we need to clone the mobility branch of the NED repository where are the
python scripts that have to be integrated to PSC, we execute the following
command-lines:

```bash
git clone  –b  mobility  git@gitlab.secured-fp7.eu:secured/ned.git
```
When this is done, python files which are in PSC directory will have to be
copied into debianPSC.img.

```bash
virt-copy-in -a /var/lib/libvirt/images/debianPSC.img * /home/nedpsc/pythonScript/  
```

## Setting up the Mobile Client
In the client we need to clone the master branch of the mobilityclient repository:

```bash
git clone git@gitlab.secured-fp7.eu:secured/mobilityclient.git
```

Installing the dependencies to run the Client node
```bash
apt-get install python-networkmanager python-gi python-dbus
```

Finally, before starting the experiment we have to run the application by executing:
```bash
# ./list_signals.py
```
Don't forget to run this as ```root```. For more information regarding
MobileClient please refer to its [README.md](/secured/mobilityclient/blob/master/README.md)
