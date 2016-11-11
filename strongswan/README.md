## Description
    This README is about how to set up strongswan in the ned side.
    It requires to configure OpenAttestation v1.7 to work with the verifier
    and strongswan to work with the userterminal.

    A script ipsec.sh execute all the installation steps.

    It is recommended to factory reset the TPM before installation.

## Dependencies
    yum install bzip2 wget gcc gmp-devel unzip trousers \
    automake autoconf libtool pkg-config gettext perl python \
    flex bison gperf trousers-devel java-1.7.0-openjdk \
    java-1.7.0-openjdk-devel


## Installation steps
Step 1, 2, 3, 8, 9 are for remote attestation feature, they work with the verifier. Step 4, 5, 6, 7 are for installing and configuring strongswan ipsec connection.

Found compiled strongswan installation package satisfies our requirements. Please install it directly and skip step 4.

1. map the host names with the hardcoded IP addresses;
2. activate TPM from BIOS and start the tcsd service;

	```bash
	root@ned: # systemctl start tcsd
	root@ned: # systemctl enable tcsd
	```
3. download the ClientInstallForLinux.zip to register the machine to the verifier;

    ```bash
    root@ned: # wget http://verifier/ClientInstallForLinux.zip

    root@ned: # unzip ClientInstallForLinux.zip

    root@ned: # cd ClientInstallForLinux

    root@ned: # sh genera-install.sh
    ```

4. install strongswan from source (or install the compiled strongswan package);

    ```bash
    root@ned: # cd strongswan-5.3.2

    root@ned: # autoreconf -i

    root@ned: # ./configure --with-ipsecdir=/usr/libexec/strongswan --bindir=/usr/libexec/strongswan --sysconfdir=/etc/strongswan \
		    --enable-dhcp --enable-farp --enable-openssl --enable-eap-md5

    root@ned: # make && make install
    ```


5. open port for ipsec to communicate with userterminal;

    ```bash
    root@ned: # firewall-cmd --permanent --add-port=500/udp

    root@ned: # firewall-cmd --permanent --add-port=4500/udp

    root@ned: # firewall-cmd --add-port=4500/udp

    root@ned: # firewall-cmd --add-port=500/udp
    ```
6. generate certificates for CA, peer, and client;

    ```bash
    root@ned: # /usr/libexec/strongswan/pki --gen > caKey.der

    root@ned: # /usr/libexec/strongswan/pki  --self --in caKey.der --dn "C=CH, O=strongSwan, CN=strongSwan CA" --ca --outform pem > caCert.crt

    root@ned: # /usr/libexec/strongswan/pki  --gen > peerKey.der

    root@ned: # /usr/libexec/strongswan/pki --pub --in peerKey.der | /usr/libexec/strongswan/pki --issue --cacert caCert.crt --cakey caKey.der --dn "C=CH, O=strongSwan, CN=ned" --san xxx.xxx.xxx.xxx > peerCert.der
    ```
    xxx.xxx.xxx.xxx is the ip of the ned, which is needed for the Android strongswan application.

7. copy each certificate to the corresponding folders in both ned and userterminal;

    ```bash
    root@ned: # cp caCert.crt /etc/strongswan/ipsec.d/cacerts

    root@ned: # cp peerCert.der /etc/strongswan/ipsec.d/certs/

    root@ned: # cp peerKey.der /etc/strongswan/ipsec.d/private/

    root@ned: # scp caCert.crt root@userterminal:/etc/strongswan/ipsec.d/cacerts
    ```

8. read PCR0 from the TPM and register it with the configure script to the verifier;

	the file storing the PCR values is called 'pcrs', it is stored in `/sys/class/misc/tpm0/device/pcrs`.

	```bash

	root@ned: # cat /sys/class/misc/tpm0/device/pcrs | sed "s/ //g"
	```
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

9. to attest the certificate, a trick is needed, to create a temp user, and assign the certificate with him, then set the ima policy to attest the files belonging to this user;

	read the temp user's uid using "id -u temp" as tUID.

	```bash
	root@ned: # adduser -s /bin/false temp
	root@ned: # chown temp /etc/strongswan/ipsec.d/certs/peerCert.der
	root@ned: # mkdir /etc/ima
	root@ned: # cp BASE_DIR/strongswan/ima-policy /etc/ima
	root@ned: # echo -e "measure fowner=$tUID" >> /etc/ima/ima-policy
	```

10. copy the ipsec configuration files in the ipsec directory to /etc/strongswan/

	ipsec.secrests is ready for use, you can change the password inside if you want. ipsec.conf needs to be modified based on specific settings, especially the ip addresses.

	you can follow the descriptions in [strongswan ipsec.conf](https://wiki.strongswan.org/projects/strongswan/wiki/ConnSection) to customise your ipsec configurations.

11. run strongswan;

	```bash
	root@ned: # systemctl start strongswan

	root@ned: # systemctl enable strongswan

	root@ned: # reboot
	```
