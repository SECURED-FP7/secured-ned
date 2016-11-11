#! /bin/bash

# File: 			ipsec_setup.sh
#
# Description:
#		This script is to setup the ipsec software strongswan used in the NED (Network Edge Device).
#		It initialises the trousers (tcsd) service, and install the strongswan with necessary patches.
#		Further it opens ports No. 500 and No. 4500 for IKE communication with user terminal.
#		Current issue is how to make system measure the certificate used in creating the ipsec tunnel.
#			The trick is to create a temp user and change the ownership of the certificate to this
#			user, and change the ima policy to measure all the files under the name of this temp
#			user. (No alternative solution exists at present)
#		Please remember to reboot after running the script.
#
# Params:
#	    	- $1 ipaddr_verifier of the third-party verifier
#		- $2 ipaddr_ned, the ip address of its own network interface
#		- $3 ned_id, which is used to generate the trusted channel certificate
# Authors:	Tao Su (tao.su@polito.it)
# Note:		currently only tested with CentOS7


[ $# -eq 0 ] && { echo "Usage: $0 ipaddr_verifier ipaddr_ned ned_id"; exit 1; }

ipaddr_verifier=$1
ipaddr_ned=$2
ned_id=$3
temp_user="temp_user"
BASEDIR=$(pwd)

# 1. write ip address of verifier to /etc/hosts
if grep -q 'verifier' '/etc/hosts';
    then
	sed -i "s/.*verifier/$ipaddr_verifier\tverifier/g" /etc/hosts
	echo -e "update ip address of verifier: $ipaddr_verifier"
    else
	echo -e "insert ip address of verifier: $ipaddr_verifier"
	echo -e "$ipaddr_verifier\tverifier" >> '/etc/hosts'
fi

if grep -q "$ned_id" '/etc/hosts';
    then
	sed -i "s/.*$ned_id/$ipaddr_ned\t$ned_id/g" /etc/hosts
	echo -e "update ip address of $ned_id: $ipaddr_ned"
    else
	echo -e "insert ip address of $ned_id: $ipaddr_ned"
	echo -e "$ipaddr_ned\t$ned_id" >> '/etc/hosts'
fi

sleep 1

# 2. start tcsd service and enable it at boot time
systemctl start tcsd
systemctl enable tcsd
echo "trousers service started and enabled."



# 3. download the ClientInstallForLinux.zip to register the machine to the verifier
# need to have OpenAttestation correctly configured and running in the verifier.
if [ -a ClientInstallForLinux.zip ]; then
    rm -f ClientInstallForLinux.zip
fi

if [ -d ClientInstallForLinux ]; then
    rm -fr ClientInstallForLinux
fi

wget http://verifier/ClientInstallForLinux.zip
unzip ClientInstallForLinux.zip
sleep 2
cd ClientInstallForLinux

sleep 1
sh general-install.sh
echo "OpenAttestation client installed successfully."
cd $BASEDIR
sleep 1

# 4. download and install strongswan from the source code;
cd $BASEDIR/strongswan-5.3.2
autoreconf -i
./configure --with-ipsecdir=/usr/libexec/strongswan --sysconfdir=/etc/strongswan --bindir=/usr/libexec/strongswan --enable-dhcp --enable-farp --enable-openssl --enable-eap-md5
make && make install

echo "strongswan installed."
sleep 1

# 5. open ports 4500 and 500 for IKE communication with user terminals
firewall-cmd --permanent --add-port=500/udp
firewall-cmd --permanent --add-port=4500/udp
firewall-cmd --add-port=4500/udp
firewall-cmd --add-port=500/udp
echo "IKE ports opened."

# 6. create certificate for strongswan CA, and itself
if [ -e caKey.der ] || [ -e caCert.der ] || [ -e peerKey.der ] || [ -e peerCert.der ]; then
    rm -f cakey.der caCert.der peerKey.der peerCert.der
fi

/usr/libexec/strongswan/pki --gen > caKey.der
/usr/libexec/strongswan/pki --self --in caKey.der --dn "C=CH, O=strongSwan, CN=strongSwan CA" --ca －－outform pem > caCert.crt
/usr/libexec/strongswan/pki --gen > peerKey.der
/usr/libexec/strongswan/pki --pub --in peerKey.der | /usr/libexec/strongswan/pki --issue --cacert caCert.crt --cakey caKey.der --dn "C=CH, O=strongSwan, CN=$ned_id" --san xxx.xxx.xxx.xxx > peerCert.der

# 7. copy certificate to corresponding directories
cp caCert.crt /etc/strongswan/ipsec.d/cacerts
cp peerKey.der /etc/strongswan/ipsec.d/private/
cp peerCert.der /etc/strongswan/ipsec.d/certs/

# 8. create a temp user, change the ownership of certificate to him
read tUID <<< $(id -u $temp_user)
if [ ! -z "$tUID" ]; then
    echo "$temp_user already exists, his UID is $tUID"
else
    echo "$temp_user does not exist, creating $temp_user..."
    adduser -s /bin/false $temp_user
    read tUID <<< $(id -u $temp_user)
    echo "$temp_user is created, his UID is $tUID"
fi

chown $temp_user /etc/strongswan/ipsec.d/certs/peerCert.der

# 9. create ima policy and configure it to measure the executables and the certificate
if [ -d "/etc/ima" ] && [ -e "/etc/ima/ima-policy" ] &&  grep -q "measure fowner=" "/etc/ima/ima-policy"; then
    sed -i "s/measure fowner.*/measure fowner=$tUID/g" /etc/ima/ima-policy
    echo -e "update $temp_user's UID to $tUID"
elif [ -d "/etc/ima" ] && [ -e "/etc/ima/ima-policy" ]; then
    echo -e "measure fowner=$tUID" >> '/etc/ima/ima-policy'
elif [ -d "/etc/ima" ]; then
    cp ima-policy /etc/ima
    echo -e "measure fowner=$tUID" >> '/etc/ima/ima-policy'
    echo -e "ima-policy loaded..."
else
    mkdir /etc/ima
    cp ima-policy /etc/ima
    echo -e "measure fowner=$tUID" >> '/etc/ima/ima-policy'
    echo -e "ima-policy loaded..."
fi


# 10. to correctly configure strongswan, some settings needs to be modified.
# directly copying the configuration files is more convenient
cp ipsec/ipsec.conf_example /etc/strongswan/
mv /etc/strongswan/ipsec.conf_example /etc/strongswan/ipsec.conf
sed -i -e "s/left=xxx.xxx.xxx.xxx/left=$ipaddr_ned/g" /etc/strongswan/ipsec.conf
sed -i -e "s/C=CH, O=strongSwan, CN=ned/C=CH, O=strongSwan, CN=$ned_id/g" /etc/strongswan/ipsec.conf
echo "ipsec.conf loaded..."

cp ipsec/ipsec.secrets_example /etc/strongswan/
mv /etc/strongswan/ipsec.secrets_example /etc/strongswan/ipsec.secrets
echo "ipsec.secrets loaded..."

cd /usr/libexec/strongswan
./starter --daemon charon
