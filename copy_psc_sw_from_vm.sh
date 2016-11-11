# Uses libguestfs - Installation guide: http://www.libguestfs.org/
# 
# Run this file from the root NED software folder that contains PSC folder.

IMG="/var/lib/libvirt/images/debianPSC.img"
SW_PATH="/home/nedpsc/pythonScript/"

if [ $# -ne 1 ] ; then
	echo "Usage: $0 [directory (that exists) where the files are copied]"
	exit 1
fi

# Copy python files
echo -n "copy PSC SW... "
virt-copy-out -a $IMG $SW_PATH $1
echo "done."

# Copy interfaces file
echo -n "copy interfaces... "
virt-copy-out -a $IMG /etc/network/interfaces $1
echo "done."

# Copy boot script that is executed when interfaces are up
echo -n "copy boot_script_psc... "
virt-copy-out -a $IMG /etc/network/if-up.d/boot_script_psc $1
echo "done."
