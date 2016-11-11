# Uses libguestfs - Installation guide: http://www.libguestfs.org/
# 
# Run this as sudo and run this file from the folder that contains PSC folder. 
# 
# Make sure that:
# 1) SW_PATH directory exists in the target IMG.
# 2) Make sure that intefaces and boot_script_psc have executable permission (+x). 
# 
# WARNING: Using this on live virtual machines can be dangerous, potentially causing disk corruption! The virtual machine must be shut down before using this script!

IMG="/var/lib/libvirt/images/debianPSC.img"
SW_PATH="/home/nedpsc/pythonScript/"

# Copy python files
echo -n "copy PSC SW... "
virt-copy-in -a $IMG PSC/* $SW_PATH
echo "done."

# Copy interfaces file
echo -n "copy interfaces... "
virt-copy-in -a $IMG PSC/interfaces /etc/network/
echo "done."

# Copy boot script that is executed when interfaces are up
echo -n "copy boot_script_psc... "
virt-copy-in -a $IMG PSC/boot_script_psc /etc/network/if-up.d/
echo "done."
