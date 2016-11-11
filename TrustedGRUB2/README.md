# Introduction of installation of TrustedGRUB2

This is the instruction of how to setup TrustedGRUB2 in the NED. The original README with more details can be found in:

https://github.com/Sirrix-AG/TrustedGRUB2/blob/master/README.md

There is also a copy in the archive file. 

## How does it work:
A computer system equipped with a TPM offers certain new functionality to enhance the security of the system. The TPM itself is a small chip mounted on or integrated in the motherboard. It has internal memory to securely store cryptographic keys and integrity measurements of the underlying computing platform. It is equipped with a cryptographic enginge needed for encryption / decryption and for signing / verifying. Additionally, the TPM is equipped with a random number generator to create secure cryptographic keys.

The TPM itself is a passive chip, which can be compared to an integrated smartcard; the TPM alone is not able to enhance trust into an existing computer system. In order to actually build a trustworthy system and in order to use the functionality provided by the TPM, the system has to have a so-called "root of trust". The "root of trust" is the security anker, with which it is possible to build a so-called "chain of trust". Every link in the chain has been measured by the prior one. The anker itself is realised by enhancing the computer BIOS with a "Core Root of Trust for Measurement (CRTM)". This is the only instance, which - beneath the TPM - has to be trustworthy.

The CRTM will be the first instance of the boot process. Its task is to measure the BIOS and extend the integrity test into a so-called Platform Configuration Register (PCR) (The TPM offers at least 16 PCRs), which is located inside the TPM. Afterwards, the BIOS measures additional ROMs, configuration and data and also stores those information in specified PCRs.

Afterwards, the BIOS loads and measures the bootloader of the operating system (located in the Master Boot Record (MBR)) and transfers control to it. Up to this point, the system configuration has been measured and it is possible to verify the current system configuration by examining the content of the PCRs.

TrustedGRUB2 is measuring all critical components during the boot process, i.e. GRUB2 kernel, GRUB2 modules, the OS kernel or OS modules and so on, together with their parameters. Please note that the TrustedGRUB2 MBR bootcode has not to be checked here (it wouldn't even be possible). The MBR bootcode has already been measured by the TPM itself. Since the TPM is passive, it has no direct ability to check if the integrity of bootloader (and the OS kernel/modules and so on) actually is correct. This can only be done indirectly by using the seal/unseal functions of the TPM (for details on this topic, you should have a look at the TCG specifications or on other documents describing TCG/TPM abilities).


## Features:
- Based on GRUB2 Release 2.00
- TPM Support with TPM detection (only legacy/mbr mode, UEFI is not supported at the moment)
- Measurement of GRUB2 kernel
- Measurement of all loaded GRUB2 modules
- Measurement of all commands and their parameters entered in shell and scripts
- New SHA1-implementation in GRUB2 kernel (necessary for doing the GRUB2 modules measurement as the crypto module isn't loaded at this stage)
- Added LUKS keyfile support with additional parameter "-k KEYFILE" for cryptomount command
- Added supported for unsealing LUKS keyfile with additional "-s" parameter for cryptomount command


## Dependencies for CentOS7 minimal install:
```bash
	   #  yum install autogen autoconf bison flex automake gcc
```

Setup:

1. download source code of TrustedGRUB2 from github or this repository;
2. unzip the archive; 
3. go into the unzipped directory, and execute autogen.sh script;
```bash
	   # ./autogen.sh
```
4. configure the installation;
```bash
	   # ./configure --prefix=INSTALLDIR
```
5. make & make install 
6. install TrustedGRUB2 into the device (need to use standard partition mode when creating partitions)
```bash
   	   # ./INSTALLDIR/sbin/grub-install --directory=INSTALLDIR/lib/grub/i386-pc /dev/sda
```
7. copy the grub.cfg into /boot/GRUB, otherwise need to manually setup the kernel and initrd
