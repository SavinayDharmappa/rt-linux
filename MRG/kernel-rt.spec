Summary: The Linux RT kernel

# build parallelism:
%{!?_smp_mflags:%define _smp_mflags --jobs=16}

# realtime kernels are named "kernel-rt"
%define kernel kernel
%define realtime rt

%define iteration 25

%define rttag rt21

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.

%define buildrt 0
%define builddoc 0
%define builddebug 1
%define buildheaders 0
%define buildvanilla 0
%define buildtrace 0
%define buildkabi 0

%define _enable_debug_packages 1

# Versions of various parts

%define base_sublevel 29

# all of this is to handle the differences between building
# from a released kernel tarball and a release-candidate (rc)
# tarball
%define released_kernel 1

## If this is a released kernel ##
%if 0%{?released_kernel}
%define upstream_sublevel %{base_sublevel}
# Do we have a 2.6.21.y update to apply?
%define stable_update 5
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev .%{stable_update}
%endif
%define rpmversion 2.6.%{base_sublevel}%{?stablerev}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(expr %{base_sublevel} + 1)
# The rc snapshot level
%define rcrev 0
# Set rpm version accordingly
%define rpmversion 2.6.%{upstream_sublevel}
%endif

# pkg_release is what we'll fill in for the rpm Release field
%if 0%{?released_kernel}
%define pkg_release %{iteration}%{?buildid}%{?dist}
%else
%if 0%{?rcrev}
%define rctag rc%rcrev
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%if !0%{?rcrev}
%define rctag .rc0
%endif
%endif
### old naming convention
### %define pkg_release 0.%{iteration}%{?rctag}%{?gittag}%{?buildid}%{?dist}
%define pkg_release %{?rctag}%{?gittag}.%{iteration}%{?buildid}%{?dist}
%endif

# The kernel tarball/base version
%define kversion 2.6.%{base_sublevel}

%define signmodules 0
%define make_target bzImage
%define kernel_image x86

%define KVERREL %{PACKAGE_VERSION}-%{PACKAGE_RELEASE}
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

# groups of related archs
%define all_x86 i386 i686
# we differ here b/c of the reloc patches

# Override generic defaults with per-arch defaults

%ifarch noarch
%define builddoc 1
%define buildheaders 0
%define builddebug 0
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-*.config
%endif

# Second, per-architecture exclusions (ifarch)

%ifarch ppc64iseries i686 i586
%define buildheaders 0
%endif

%ifarch %{all_x86}
%define asmarch x86
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-i?86*.config
%define image_install_path boot
%define signmodules 0
%define hdrarch i386
%endif

%ifarch i686
%define buildrt 1
%define buildtrace 1
%define buildvanilla 1
%endif

%ifarch x86_64
%define asmarch x86
%define buildrt 1
%define buildtrace 1
%define buildvanilla 1
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-x86_64*.config
%define image_install_path boot
%define signmodules 0
%endif

%ifarch ppc64 ppc64iseries
%define asmarch powerpc
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-ppc64*.config
%define image_install_path boot
%define signmodules 0
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define hdrarch powerpc
%endif

%ifarch sparc
%define asmarch sparc
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-sparc.config
%define make_target image
%define kernel_image image
%endif

%ifarch sparc64
%define asmarch sparc
%define buildsmp 1
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-sparc64*.config
%define make_target image
%define kernel_image image
%endif

%ifarch ppc
%define asmarch powerpc
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-ppc{-,.}*config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define buildsmp 1
%define hdrarch powerpc
%endif

%if %{buildrt}
%ifarch x86_64
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-x86_64-rt*.config
%endif
%ifarch i686
%define all_arch_configs $RPM_SOURCE_DIR/kernel-%{rpmversion}-i?86-rt*.config
%endif
%endif

# To temporarily exclude an architecture from being built, add it to
# %nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We don't build a kernel on i386 or s390x -- we only do kernel-headers there.
%define nobuildarches i386 s390

%ifarch %nobuildarches
%define buildsmp 0
%define buildpae 0
#%define _enable_debug_packages 0
%endif

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, selinux-policy-targeted < 1.25.3-14

#
# The ld.so.conf.d file we install uses syntax older ldconfig's don't grok.
#
%define xen_conflicts glibc < 2.3.5-1, xen < 3.0.1

#
# Packages that need to be installed before the kernel is, because the %post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, mkinitrd >= 4.2.21-1

Name: %{kernel}-%{realtime}
Group: System Environment/Kernel
License: GPLv2
Version: %{rpmversion}
Release: %{pkg_release}
ExclusiveArch: noarch i686 x86_64
ExclusiveOS: Linux
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1}\
Provides: kernel-rt = %{rpmversion}
Provides: kernel-rt-drm = 4.3.0
Provides: kernel-rt-%{_target_cpu} = %{rpmversion}-%{pkg_release}
Prereq: %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}

#
# prevent the x86 kernel-rt package from being picked up by yum
# on an x86_64 box (this prevents multilib behavior, yum special-cases
# the "kernel" package-name, but not the kernel-rt package name):
#
%ifarch x86_64
Conflicts: kernel-i686
%endif

# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes


#
# List the packages used during the kernel build
#
BuildPreReq: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildPreReq: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils
%if %{signmodules}
BuildPreReq: gnupg
%endif
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
%if %{buildheaders}
BuildRequires: unifdef
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb

# Base kernel source
Source0: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/linux-%{kversion}.tar.bz2

%if 0%{?stable_update}
Source1: patch-%{rpmversion}.bz2
%endif

%if 0%{?rcrev}
Source2: patch-%{rpmversion}-%{rctag}.bz2
%endif

# current release candidate

Source3: Makefile.config

Source10: COPYING.modules
Source11: genkey
%if %{buildkabi}
Source12: kabitool
%endif
Source14: find-provides
Source15: merge.pl

Source20: config-debug
Source21: config-generic
Source22: config-i686-PAE
Source23: config-nodebug
Source24: config-rt
Source25: config-trace
Source26: config-vanilla
Source27: config-x86_64-generic
Source28: config-x86-generic
Source30: sanity_check.py

# START OF PATCH DEFINITIONS
%if 0%{?rcrev}
Patch2: patch-%{rpmversion}-%{rctag}-%{rttag}.bz2
%else
Patch2: patch-%{rpmversion}-%{rttag}.bz2
%endif
# Patch3: smi-detector.patch
Patch4: Allocate-RTSJ-memory-for-TCK-conformance-test.patch
Patch5: Add-dev-rmem-device-driver-for-real-time-JVM-testing.patch
Patch6: ibm-rmem-for-rtsj.patch
Patch7: linux-2.6-dynticks-off-by-default.patch
Patch8: linux-2.6-rt-oomkill.patch
Patch9: RT-die.patch
Patch10: pci-nommconf-noseg.patch

### 2.6.29.1-3
Patch11: linux-2.6-panic-on-oops.patch

### 2.6.29.1-4
# Only a config change

### 2.6.29.1-5
Patch12: RHEL-RT_AMD_TSC_sync_PN.patch
Patch13: bz465745-rtc-fix_kernel_panic_on_second_use_of_SIGIO_nofitication.patch
Patch14: bz465837-rtc-compat-rhel5.patch-ported-to-V2.patch
Patch15: bz467739-ibm-add-amd64_edac-driver.patch
Patch16: irq-tracer-fix.patch
Patch17: forward-port-of-limit-i386-ram-to-16gb.patch
Patch18: forward-port-of-quiet-plist-warning.patch

### 2.6.29.1-6
Patch19: bz460217-nagle-tunables.patch
Patch20: ibm-rtl-driver.patch
Patch21: ibm-hs21-tmid-fix.patch
Patch22: ibm-qla-disable-msi-on-rt.patch

### 2.6.29.1-7
Patch23: aic94xx-inline-fw-rt.patch
Patch24: qla2xxx-inline-fw-rt.patch
# Patch25: preempt-rt-implement-rt_downgrade_write.patch
Patch26: ntp-logarithmic.patch

### 2.6.29.1-8
# Patch27: lockdep-fix-debug-lock-counting.patch
Patch28: ibm-amd-edac-rh-v1-2.6.29_forward_port.patch
Patch29: bz448574-increase-max-stack-trace-entries.patch
# Patch30: net-link-workaround-silly-yield.patch

### 2.6.29.1-9
# Rebased to 2.6.29.1-rt8
# Removed redundant patches

### 2.6.29.1-10
# Rebased to 2.6.29.1-rt9

### 2.6.29.1-11
# rebased to 2.6.29.2
# rebased rt to 2.6.29.2-rt10
Patch30: forward-port-from-bz465862-ib-fix-locking-order.patch
Patch31: jstultz-ntp.patch

### 2.6.29.1-12
# rebased rt to 2.6.29.2-rt11

### 2.6.29.1-13
# ftrace function profiler
# Patch32: 0001-tracing-add-function-profiler.patch
# Patch33: 0002-tracing-move-function-profiler-data-out-of-function.patch
# Patch34: 0003-tracing-adding-function-timings-to-function-profile.patch
# Patch35: 0004-tracing-make-the-function-profiler-per-cpu.patch
# Patch36: 0005-function-graph-add-option-to-calculate-graph-time-o.patch
# Patch37: 0006-tracing-remove-on-the-fly-allocator-from-function-p.patch
# Patch38: 0007-tracing-add-average-time-in-function-to-function-pr.patch
# Patch39: 0008-backport-function-profiler-fixes.patch

### 2.6.29.3-14
# rebased to 2.6.29.3
# rebased rt to 2.6.29.3-rt12

### 2.6.29.3-15
# rebased rt to 2.6.29.3-rt13

### 2.6.29.3-16
# rebased rt to 2.6.29.3-rt14

### 2.6.29.4-17
# rebased rt to 2.6.29.4-rt15
# Patch40: ftrace-function_profiler-bandaid.patch
Patch41: net-avoid-extra-wakeups-in-wait_for_packet.patch

### 2.6.29.4-18
# rebased rt to 2.6.29.4-rt16

### 2.6.29.4-19
# Patch42: ftrace-fix-profile-race.patch

### 2.6.29.4-20
Patch43: bz503758-increase-hung_task_timeout_secs-on-rt.patch

### 2.6.29.4-21
# Rebased to 2.6.29.4-rt17
# The following mrg patches are no longer necessary.
# Patch32, Patch33, Patch34, Patch35, Patch36, Patch37, Patch38, Patch39
# Patch40, Patch42

### 2.6.29.4-22
# Rebased to 2.6.29.4-rt18
# The mrg patch smi-detector.patch is replaced by
# the 2.6.29.4-rt18 hwlat_detector-a-system-hardware-latency-detector.patch

### 2.6.29.4-23
# Rebased to 2.6.29.4-rt19

### 2.6.29.5-24
# Rebased to 2.6.29.5-rt20

### 2.6.29.5-25
# Rebased to 2.6.29.5-rt21

# END OF PATCH DEFINITIONS

Patch10000: linux-2.6-build-nonintconfig.patch

# empty final patch file to facilitate testing of kernel patches
Patch99999: linux-kernel-test.patch

BuildRoot: %{_tmppath}/%{name}-%{KVERREL}-root

# Override find_provides to use a script that provides "kernel(symbol) = hash".
# Pass path of the RPM temp dir containing kabideps to find-provides script.
%global _use_internal_dependency_generator 0
%define __find_provides %_sourcedir/find-provides %{_tmppath}
%define __find_requires /usr/lib/rpm/redhat/find-requires kernel

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

%package devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
AutoReqProv: no
Provides: kernel-rt-devel-%{_target_cpu} = %{rpmversion}-%{pkg_release}
Prereq: /usr/bin/find

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.


%package doc
Summary: Various documentation bits found in the kernel source.
Group: Documentation

%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.

%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders
Provides: glibc-kernheaders = 3.0-46

%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package vanilla
Summary: The vanilla upstream kernel the -rt kernel is based on

Group: System Environment/Kernel
Provides: kernel = %{rpmversion}
Provides: kernel-drm = 4.3.0
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}vanilla
Prereq: %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description vanilla
This package includes a vanilla version of the Linux kernel. It is
useful for those who dont want a real-time kernel, or who'd like to
quickly check whether a problem seen on -rt is also present in the
vanilla kernel.

%package trace
Summary: The realtime kernel with tracing options turned on

Group: System Environment/Kernel
Provides: kernel = %{rpmversion}
Provides: kernel-drm = 4.3.0
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}trace
Prereq: %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description trace
This package includes a version of the realtime Linux kernel with tracing
options compiled turned on and compield in. It is useful in tracking down
latency hot-spots in kernel code.


%package trace-devel
Summary: Development package for building kernel modules to match the tracing kernel.
Group: System Environment/Kernel
AutoReqProv: no
Provides: kernel-rt-trace-devel-%{_target_cpu} = %{rpmversion}-%{pkg_release}
Provides: kernel-rt-trace-devel = %{rpmversion}-%{pkg_release}trace
Prereq: /usr/bin/find

%description trace-devel
This package provides kernel headers and makefiles sufficient to build modules
against the tracing kernel package.


%package vanilla-devel
Summary: Development package for building kernel modules to match the vanilla kernel.
Group: System Environment/Kernel
Provides: kernel-rt-vanilla-devel-%{_target_cpu} = %{rpmversion}-%{pkg_release}
Provides: kernel-rt-vanilla-devel-%{_target_cpu} = %{rpmversion}-%{pkg_release}vanilla
Provides: kernel-rt-vanilla-devel = %{rpmversion}-%{pkg_release}vanilla
AutoReqProv: no
Prereq: /usr/bin/find

%description vanilla-devel
This package provides kernel headers and makefiles sufficient to build modules
against the vanilla kernal package.

%package debug
Summary: A debug realtime kernel and modules
Group: System Environment/Kernel
License: GPLv2
Provides: kernel-rt-debug = %{rpmversion}
Provides: kernel-rt-debug-drm = 4.3.0
Provides: kernel-rt-debug-%{_target_cpu} = %{rpmversion}-%{pkg_release}debug
Prereq: %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
AutoReq: no
AutoProv: yes

%description debug
This package contains the realtime kernel and modules compiled with various
tracing and debugging options enabled. It is primarily useful for tracking
down problem discovered with the regular realtime kernel.

%package debug-devel
Summary: Development package for building kernel modules to match the debug realtime kernel.
Group: System Environment/Kernel
Provides: kernel-rt-debug-devel-%{_target_cpu} = %{rpmversion}-%{pkg_release}
Provides: kernel-rt-debug-devel-%{_target_cpu} = %{rpmversion}-%{pkg_release}debug
Provides: kernel-rt-debug-devel = %{rpmversion}-%{pkg_release}debug
AutoReqProv: no
Prereq: /usr/bin/find

%description debug-devel
This package provides kernel headers and makefiles sufficient to build modules
against the debug kernel-rt package.


%prep
patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    echo "Can't find $RPM_SOURCE_DIR/$patch"
    exit 1;
  fi
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%if 0%{?released_kernel}
%define vanillaversion 2.6.%{base_sublevel}
# released_kernel with stable_update available case
%if 0%{?stable_update}
%define vanillaversion 2.6.%{base_sublevel}.%{stable_update}
%endif
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 2.6.%{base_sublevel}-git%{gitrev}
%endif
%endif
%endif

if [ ! -d %{name}-%{rpmversion}-%{pkg_release}/vanilla-%{vanillaversion} ]; then
  # Ok, first time we do a make prep.
  rm -f pax_global_header
%setup -q -n %{name}-%{rpmversion}-%{pkg_release} -c
  mv linux-%{kversion} vanilla-%{vanillaversion}
  cd vanilla-%{vanillaversion}

# Update vanilla to the latest upstream.
# released_kernel with stable_update available case
%if 0%{?stable_update}
  ApplyPatch patch-2.6.%{base_sublevel}.%{stable_update}.bz2
# non-released_kernel case
%else
%if 0%{?rcrev}
  ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}.bz2
%if 0%{?gitrev}
  ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.bz2
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
  ApplyPatch patch-2.6.%{base_sublevel}-git%{gitrev}.bz2
%endif
%endif
%endif

# This patch adds a "make nonint_oldconfig" which is non-interactive and
# also gives a list of missing options at the end. Useful for automated
# builds (as used in the buildsystem).
ApplyPatch linux-2.6-build-nonintconfig.patch

# create a directory to hold the config files
  mkdir configs

# now move back up and get ready to work
  cd ..

else
  # We already have a vanilla dir.
  cd %{name}-%{rpmversion}-%{pkg_release}
  if [ -d linux-%{rpmversion}.%{_target_cpu} ]; then
     # Just in case we ctrl-c'd a prep already
     rm -rf deleteme.%{_target_cpu}
     # Move away the stale away, and delete in background.
     mv linux-%{rpmversion}.%{_target_cpu} deleteme.%{_target_cpu}
     rm -rf deleteme.%{_target_cpu} &
  fi
fi

cp -rl vanilla-%{vanillaversion} linux-%{rpmversion}.%{_target_cpu}

cd linux-%{rpmversion}.%{_target_cpu}

cp $RPM_SOURCE_DIR/config-* .
cp %{SOURCE15} .
cp %{SOURCE30} .

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE3} VERSION=%{rpmversion} configs

# START OF PATCH APPLICATIONS
%if 0%{?rcrev}
ApplyPatch patch-%{rpmversion}-%{rctag}-%{rttag}.bz2
%else
ApplyPatch patch-%{rpmversion}-%{rttag}.bz2
%endif

# ApplyPatch smi-detector.patch
ApplyPatch Allocate-RTSJ-memory-for-TCK-conformance-test.patch
ApplyPatch Add-dev-rmem-device-driver-for-real-time-JVM-testing.patch
ApplyPatch ibm-rmem-for-rtsj.patch
ApplyPatch linux-2.6-dynticks-off-by-default.patch
ApplyPatch linux-2.6-rt-oomkill.patch
ApplyPatch RT-die.patch
ApplyPatch pci-nommconf-noseg.patch

### 2.6.29.1-3
ApplyPatch linux-2.6-panic-on-oops.patch

### 2.6.29-4
# Only a config change

### 2.6.29.1-5
ApplyPatch RHEL-RT_AMD_TSC_sync_PN.patch
ApplyPatch bz465745-rtc-fix_kernel_panic_on_second_use_of_SIGIO_nofitication.patch
ApplyPatch bz465837-rtc-compat-rhel5.patch-ported-to-V2.patch
ApplyPatch bz467739-ibm-add-amd64_edac-driver.patch
ApplyPatch irq-tracer-fix.patch
ApplyPatch forward-port-of-limit-i386-ram-to-16gb.patch
ApplyPatch forward-port-of-quiet-plist-warning.patch

### 2.6.29.1-6
ApplyPatch bz460217-nagle-tunables.patch
ApplyPatch ibm-rtl-driver.patch
ApplyPatch ibm-hs21-tmid-fix.patch
ApplyPatch ibm-qla-disable-msi-on-rt.patch

### 2.6.29.1-7
ApplyPatch aic94xx-inline-fw-rt.patch
ApplyPatch qla2xxx-inline-fw-rt.patch
# ApplyPatch preempt-rt-implement-rt_downgrade_write.patch
ApplyPatch ntp-logarithmic.patch

### 2.6.29.1-8
# ApplyPatch lockdep-fix-debug-lock-counting.patch
ApplyPatch ibm-amd-edac-rh-v1-2.6.29_forward_port.patch
ApplyPatch bz448574-increase-max-stack-trace-entries.patch
# ApplyPatch net-link-workaround-silly-yield.patch

### 2.6.29.1-9
# Rebased to 2.6.29.1-rt8
# Removed redundant patches

### 2.6.29.1-10
# Rebased to 2.6.29.1-rt9

### 2.6.29.1-11
# rebased to 2.6.29.2
# rebased rt to 2.6.29.2-rt10
ApplyPatch forward-port-from-bz465862-ib-fix-locking-order.patch
ApplyPatch jstultz-ntp.patch

### 2.6.29.1-12
# rebased rt to 2.6.29.2-rt11

### 2.6.29.1-13
# ftrace function profiler
# ApplyPatch 0001-tracing-add-function-profiler.patch
# ApplyPatch 0002-tracing-move-function-profiler-data-out-of-function.patch
# ApplyPatch 0003-tracing-adding-function-timings-to-function-profile.patch
# ApplyPatch 0004-tracing-make-the-function-profiler-per-cpu.patch
# ApplyPatch 0005-function-graph-add-option-to-calculate-graph-time-o.patch
# ApplyPatch 0006-tracing-remove-on-the-fly-allocator-from-function-p.patch
# ApplyPatch 0007-tracing-add-average-time-in-function-to-function-pr.patch
# ApplyPatch 0008-backport-function-profiler-fixes.patch

### 2.6.29.3-14
# rebased to 2.6.29.3
# rebased rt to 2.6.29.3-rt12

### 2.6.29.3-15
# rebased rt to 2.6.29.3-rt13

### 2.6.29.3-16
# rebased rt to 2.6.29.3-rt14

### 2.6.29.4-17
# rebased rt to 2.6.29.4-rt15
# ApplyPatch ftrace-function_profiler-bandaid.patch
ApplyPatch net-avoid-extra-wakeups-in-wait_for_packet.patch

### 2.6.29.4-18
# rebased rt to 2.6.29.4-rt16

### 2.6.29.4-19
# ApplyPatch ftrace-fix-profile-race.patch

### 2.6.29.4-20
ApplyPatch bz503758-increase-hung_task_timeout_secs-on-rt.patch

### 2.6.29.4-21
# Rebased to 2.6.29.4-rt17

### 2.6.29.4-22
# Rebased to 2.6.29.4-rt18

### 2.6.29.4-23
# Rebased to 2.6.29.4-rt19

### 2.6.29.5-24
# Rebased to 2.6.29.5-rt20

### 2.6.29.5-25
# Rebased to 2.6.29.5-rt21

# END OF PATCH APPLICATIONS

# empty final patch to facilitate testing of kernel patches
ApplyPatch linux-kernel-test.patch

cp %{SOURCE10} Documentation/

# Necessary for BZ459141 (ftrace daemon removal)
chmod +x scripts/recordmcount.pl

# now run oldconfig over all the config files
for i in *.config
do
  if [ "$i" != ${i//vanilla/chocolate/} ]; then
     isvanilla=true
     OLDDIR=`pwd`
  else
     isvanilla=false
  fi
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  if [ "$isvanilla" = "true" ]; then
    pushd ../vanilla-%{vanillaversion};
    mv $OLDDIR/.config .
  fi
  pwd
  make ARCH=$Arch nonint_oldconfig > /dev/null
  pwd
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
  if [ "$isvanilla" = "true" ]; then
    popd
  fi
done

# make sure the kernel has the sublevel we know it has. This looks weird
# but for -pre and -rc versions we need it since we only want to use
# the higher version when the final kernel is released.
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -prep/" Makefile

# get rid of unwanted files resulting from patch fuzz
cd ..
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

###
### build
###
%build
#
# Create gpg keys for signing the modules
#

%if %{signmodules}
gpg --homedir . --batch --gen-key %{SOURCE11}
gpg --homedir . --export --keyring ./kernel.pub Red > extract.pub
make linux-%{rpmversion}.%{_target_cpu}/scripts/bin2c
linux-%{rpmversion}.%{_target_cpu}/scripts/bin2c ksign_def_public_key __initdata < extract.pub > linux-%{rpmversion}.%{_target_cpu}/crypto/signature/key.h
%endif

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    DoDevel=$4

    if [ "vanilla" = "$Flavour" ]; then
      pushd ../vanilla-%{vanillaversion}
    fi

    # Pick the right config file for the kernel we're building
    if [ -n "$Flavour" ] ; then
      Config=kernel-%{rpmversion}-%{_target_cpu}-%{realtime}$Flavour.config
      DevelDir=/usr/src/kernels/%{KVERREL}-$Flavour-%{_target_cpu}
      DevelLink=
    else
      Config=kernel-%{rpmversion}-%{_target_cpu}-%{realtime}.config
      DevelDir=/usr/src/kernels/%{KVERREL}-%{_target_cpu}
      DevelLink=
    fi

    KernelVer=%{KVERREL}$Flavour
    echo BUILDING A KERNEL FOR $Flavour %{_target_cpu}...
    echo "KernelVer => $KernelVer"
    echo "_smp_mflags => %{_smp_mflags}"

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = %{?stablerev}-%{pkg_release}$Flavour/" Makefile

    # ensure the sublevel is correct (the upstream sublevel)
    perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{upstream_sublevel}/" Makefile

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    if [ "$KernelImage" == "x86" ]; then
       KernelImage=arch/$Arch/boot/bzImage
    fi

    make -s ARCH=$Arch nonint_oldconfig > /dev/null
    make -s ARCH=$Arch %{?_smp_mflags} $MakeTarget
    make -s ARCH=$Arch %{?_smp_mflags} modules || exit 1

    # Start installing the results

%if "%{_enable_debug_packages}" == "1"
    mkdir -p $RPM_BUILD_ROOT/usr/lib/debug/boot
    mkdir -p $RPM_BUILD_ROOT/usr/lib/debug/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
    touch $RPM_BUILD_ROOT/boot/initrd-$KernelVer.img
    cp $KernelImage $RPM_BUILD_ROOT/%{image_install_path}/vmlinuz-$KernelVer
    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    make ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer

%if %{buildkabi}
    # Create the kABI metadata for use in packaging
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
    chmod 0755 %_sourcedir/kabitool
    if [ ! -e $RPM_SOURCE_DIR/kabi_whitelist ]; then
        %_sourcedir/kabitool -b $RPM_BUILD_ROOT/$DevelDir -k $KernelVer -l $RPM_BUILD_ROOT/kabi_whitelist
    else
	cp $RPM_SOURCE_DIR/kabi_whitelist $RPM_BUILD_ROOT/kabi_whitelist
    fi
    rm -f %{_tmppath}/kernel-$KernelVer-kabideps
    %_sourcedir/kabitool -b . -d %{_tmppath}/kernel-$KernelVer-kabideps -k $KernelVer -w $RPM_BUILD_ROOT/kabi_whitelist
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    if [ "$DoDevel" = "True" ]
    then
    	rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
	rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
	mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
	(cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
	# dirs for additional modules per module-init-tools, kbuild/modules.txt
    	mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    	mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    	mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    	# first copy everything
    	cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    	cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%if %{buildkabi}
    	mv $RPM_BUILD_ROOT/kabi_whitelist $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    	cp symsets-$KernelVer.tar.gz $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%endif
    	# then drop all but the needed Makefiles/Kconfig files
    	rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    	rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    	rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    	cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    	cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    	if [ -d arch/%{_arch}/scripts ]; then
      	  cp -a arch/%{_arch}/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    	fi
    	if [ -f arch/%{_arch}/*lds ]; then
    	  cp -a arch/%{_arch}/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    	fi
    	rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    	rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
	if [ -d arch/%{asmarch}/include ]; then
      	    cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
        fi
    	mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    	cd include
    	cp -a acpi config keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound video asm asm-generic $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    	cp -a `readlink asm` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    	# While arch/powerpc/include/asm is still a symlink to the old
    	# include/asm-ppc{64,} directory, include that in kernel-devel too.
    	if [ "$Arch" = "powerpc" -a -r ../arch/powerpc/include/asm ]; then
    	  cp -a `readlink ../arch/powerpc/include/asm` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    	  mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch/include
    	  pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch/include
    	  ln -sf ../../../include/asm-ppc* asm
    	  popd
    	fi
    	# Make sure the Makefile and version.h have a matching timestamp so that
    	# external modules can be built
    	touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    	touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    	# Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    	cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf
    	cd ..

    	#
    	# save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    	#
%if "%{_enable_debug_packages}" == "1"
    	mkdir -p $RPM_BUILD_ROOT/usr/lib/debug/lib/modules/$KernelVer
    	cp vmlinux $RPM_BUILD_ROOT/usr/lib/debug/lib/modules/$KernelVer
%endif

    	find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # gpg sign the modules
%if %{signmodules}
    	gcc -o scripts/modsign/mod-extract scripts/modsign/mod-extract.c -Wall
    	KEYFLAGS="--no-default-keyring --homedir .."
    	KEYFLAGS="$KEYFLAGS --secret-keyring ../kernel.sec"
    	KEYFLAGS="$KEYFLAGS --keyring ../kernel.pub"
    	export KEYFLAGS

    	for i in `cat modnames`
    	do
    	  sh ./scripts/modsign/modsign.sh $i Red
    	  mv -f $i.signed $i
    	done
    	unset KEYFLAGS
%endif
    	# mark modules executable so that strip-to-file can strip them
    	cat modnames | xargs chmod u+x

    	# detect missing or incorrect license tags
    	for i in `cat modnames`
    	do
    	  echo -n "$i "
    	  /sbin/modinfo -l $i >> modinfo
    	done
    	cat modinfo |\
    	  grep -v "^GPL" |
    	  grep -v "^Dual BSD/GPL" |\
    	  grep -v "^Dual MPL/GPL" |\
    	  grep -v "^GPL and additional rights" |\
    	  grep -v "^GPL v2" && exit 1
    	rm -f modinfo
    	rm -f modnames
    	# remove files that will be auto generated by depmod at rpm -i time
    	rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.*

    	# Move the devel headers out of the root file system
    	mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    	mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    	ln -sf ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    	[ -z "$DevelLink" ] || ln -sf `basename $DevelDir` $RPM_BUILD_ROOT/$DevelLink
    fi
    if [ "vanilla" = "$Flavour" ]; then
      popd
    fi
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot

cd linux-%{rpmversion}.%{_target_cpu}

%if %{buildrt}
BuildKernel %make_target %kernel_image "" True
%endif

%if %{builddebug}
BuildKernel %make_target %kernel_image debug  True
%endif

%if %{buildtrace}
BuildKernel %make_target %kernel_image trace True
%endif

%if %{buildvanilla}
BuildKernel %make_target %kernel_image vanilla True
%endif

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if "%{_enable_debug_packages}" == "1"
%ifnarch noarch
%global __debug_package 1
%package debuginfo-common
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
Provides: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}

%description debuginfo-common
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%files debuginfo-common
%defattr(-,root,root)
/usr/src/debug/%{name}-%{rpmversion}-%{pkg_release}/linux-%{rpmversion}.%{_target_cpu}
/usr/src/debug/.build-id
%if %{buildvanilla}
/usr/src/debug/%{name}-%{rpmversion}-%{pkg_release}/vanilla-%{vanillaversion}
%endif
%dir /usr/src/debug
%dir /usr/lib/debug
%dir /usr/lib/debug/%{image_install_path}
%dir /usr/lib/debug/lib
%dir /usr/lib/debug/lib/modules
%dir /usr/lib/debug/usr/src/kernels
%endif
%endif

###
### install
###

%install

cd linux-%{rpmversion}.%{_target_cpu}

# make the build-id directory (for building on fedora)
mkdir -p $RPM_BUILD_ROOT/usr/src/debug/.build-id

%if %{builddoc}
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/kernel-doc-%{rpmversion}/Documentation

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a+r *
# copy the source over
tar cf - Documentation | tar xf - -C $RPM_BUILD_ROOT/usr/share/doc/kernel-doc-%{rpmversion}
%endif

%if %{buildheaders}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Manually go through the 'headers_check' process for every file, but
# don't die if it fails
chmod +x scripts/hdrcheck.sh
echo -e '*****\n*****\nHEADER EXPORT WARNINGS:\n*****' > hdrwarnings.txt
for FILE in `find $RPM_BUILD_ROOT/usr/include` ; do
    scripts/hdrcheck.sh $RPM_BUILD_ROOT/usr/include $FILE >> hdrwarnings.txt || :
done
echo -e '*****\n*****' >> hdrwarnings.txt
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

# glibc provides scsi headers for itself, for now
rm -rf $RPM_BUILD_ROOT/usr/include/scsi
rm -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif
###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%post
/sbin/new-kernel-pkg --package kernel-rt --banner "Red Hat Enterprise Linux (realtime)" --mkinitrd --depmod --install %{KVERREL} || exit $?

%post devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%{KVERREL}-%{_target_cpu} > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post vanilla
/sbin/new-kernel-pkg --package kernel-rt-vanilla --mkinitrd --depmod --install %{KVERREL}vanilla || exit $?

%post trace
/sbin/new-kernel-pkg --package kernel-rt-trace --mkinitrd --depmod --install %{KVERREL}trace || exit $?

%post debug
/sbin/new-kernel-pkg --package kernel-rt --banner "Red Hat Enterprise Linux (realtime debug)" --mkinitrd --depmod --install %{KVERREL}debug || exit $?

%preun
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL} || exit $?

%preun vanilla
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}vanilla || exit $?

%preun trace
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}trace || exit $?

%preun debug
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}debug || exit $?

###
### file lists
###

# This is %{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

%if %{buildrt}
%if "%{_enable_debug_packages}" == "1"
%ifnarch noarch
%global __debug_package 1
%package debuginfo
Summary: Debug information for package %{name}
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-debuginfo-%{_target_cpu} = %{KVERREL}
%description debuginfo
This package provides debug information for package %{name}
This is required to use SystemTap with %{name}-%{KVERREL}.
%files debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
/usr/lib/debug/%{elf_image_install_path}/*-%{KVERREL}.debug
%endif
/usr/lib/debug/lib/modules/%{KVERREL}
/usr/lib/debug/usr/src/kernels/%{KVERREL}-%{_target_cpu}
%endif
%endif

%files
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}
/boot/System.map-%{KVERREL}
%if %{buildkabi}
/boot/symvers-%{KVERREL}.gz
%endif
/boot/config-%{KVERREL}
%dir /lib/modules/%{KVERREL}
/lib/modules/%{KVERREL}/kernel
/lib/modules/%{KVERREL}/build
/lib/modules/%{KVERREL}/source
/lib/modules/%{KVERREL}/extra
/lib/modules/%{KVERREL}/updates
/lib/modules/%{KVERREL}/weak-updates
/lib/firmware
%ghost /boot/initrd-%{KVERREL}.img


%files devel
%defattr(-,root,root)
/usr/src/kernels/%{KVERREL}-%{_target_cpu}

%endif # buildrt

%if %{buildheaders}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{builddebug}
%files debug
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}debug
/boot/System.map-%{KVERREL}debug
%if %{buildkabi}
/boot/symvers-%{KVERREL}debug.gz
%endif
/boot/config-%{KVERREL}debug
%dir /lib/modules/%{KVERREL}debug
/lib/modules/%{KVERREL}debug/kernel
/lib/modules/%{KVERREL}debug/build
/lib/modules/%{KVERREL}debug/source
/lib/modules/%{KVERREL}debug/extra
/lib/modules/%{KVERREL}debug/updates
/lib/modules/%{KVERREL}debug/weak-updates
/lib/firmware
%ghost /boot/initrd-%{KVERREL}debug.img

%files debug-devel
%defattr(-,root,root)
/usr/src/kernels/%{KVERREL}-debug-%{_target_cpu}

%if "%{_enable_debug_packages}" == "1"
%ifnarch noarch
%global __debug_package 1
%package debug-debuginfo
Summary: Debug information for package %{name}-debug
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-debug-debuginfo-%{_target_cpu} = %{KVERREL}
%description debug-debuginfo
This package provides debug information for package %{name}-debug
This is required to use SystemTap with %{name}-debug-%{KVERREL}.
%files debug-debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
/usr/lib/debug/%{elf_image_install_path}/*-%{KVERREL}debug.debug
%endif
/usr/lib/debug/lib/modules/%{KVERREL}debug
/usr/lib/debug/usr/src/kernels/%{KVERREL}-debug-%{_target_cpu}
%endif
%endif
%endif # builddebug

%if %{buildvanilla}
%if "%{_enable_debug_packages}" == "1"
%ifnarch noarch
%global __debug_package 1
%package vanilla-debuginfo
Summary: Debug information for package %{name}-vanilla
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-vanilla-debuginfo-%{_target_cpu} = %{KVERREL}
%description vanilla-debuginfo
This package provides debug information for package %{name}-vanilla
This is required to use SystemTap with %{name}-vanilla-%{KVERREL}.
%files vanilla-debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
/usr/lib/debug/%{image_install_path}/*-%{KVERREL}vanilla.debug
%endif
/usr/lib/debug/lib/modules/%{KVERREL}vanilla
/usr/lib/debug/usr/src/kernels/%{KVERREL}-vanilla-%{_target_cpu}
%endif
%endif

%files vanilla
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}vanilla
/boot/System.map-%{KVERREL}vanilla
%if %{buildkabi}
/boot/symvers-%{KVERREL}vanilla.gz
%endif
/boot/config-%{KVERREL}vanilla
%dir /lib/modules/%{KVERREL}vanilla
/lib/modules/%{KVERREL}vanilla/kernel
/lib/modules/%{KVERREL}vanilla/build
/lib/modules/%{KVERREL}vanilla/source
/lib/modules/%{KVERREL}vanilla/extra
/lib/modules/%{KVERREL}vanilla/updates
/lib/modules/%{KVERREL}vanilla/weak-updates
/lib/firmware
%ghost /boot/initrd-%{KVERREL}vanilla.img

%files vanilla-devel
%defattr(-,root,root)
/usr/src/kernels/%{KVERREL}-vanilla-%{_target_cpu}
%endif

%if %{buildtrace}
%if "%{_enable_debug_packages}" == "1"
%ifnarch noarch
%global __debug_package 1
%package trace-debuginfo
Summary: Debug information for package %{name}-trace
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-trace-debuginfo-%{_target_cpu} = %{KVERREL}
%description trace-debuginfo
This package provides debug information for package %{name}-trace
This is required to use SystemTap with %{name}-trace-%{KVERREL}.
%files trace-debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
/usr/lib/debug/%{elf_image_install_path}/*-%{KVERREL}trace.debug
%endif
/usr/lib/debug/lib/modules/%{KVERREL}trace
/usr/lib/debug/usr/src/kernels/%{KVERREL}-trace-%{_target_cpu}
%endif
%endif

%files trace
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}trace
/boot/System.map-%{KVERREL}trace
%if %{buildkabi}
/boot/symvers-%{KVERREL}trace.gz
%endif
/boot/config-%{KVERREL}trace
%dir /lib/modules/%{KVERREL}trace
/lib/modules/%{KVERREL}trace/kernel
/lib/modules/%{KVERREL}trace/build
/lib/modules/%{KVERREL}trace/source
/lib/modules/%{KVERREL}trace/extra
/lib/modules/%{KVERREL}trace/updates
/lib/modules/%{KVERREL}trace/weak-updates
/lib/firmware
%ghost /boot/initrd-%{KVERREL}trace.img

%files trace-devel
%defattr(-,root,root)
/usr/src/kernels/%{KVERREL}-trace-%{_target_cpu}
%endif

# only some architecture builds need kernel-doc

%if %{builddoc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%endif

%changelog
* Wed Jun 17 2009 John Kacur <jkacur@redhat.com> - 2.6.29.5-25
- Rebased to 2.6.29.5-rt21

* Tue Jun 16 2009 John Kacur <jkacur@redhat.com> - 2.6.29.5-24
- Rebased to 2.6.29.5-rt20

* Mon Jun 15 2009 John Kacur <jkacur@redhat.com> - 2.6.29.4-23
- Rebased to 2.6.29.4-rt19

* Sat Jun 13 2009 John Kacur <jkacur@redhat.com> - 2.6.29.4-22
- Rebased to 2.6.29.4-rt18
- The mrg smi-detector.patch is replaced by the following patch
- hwlat_detector-a-system-hardware-latency-detector.patch

* Thu Jun 11 2009 John Kacur <jkacur@redhat.com> - 2.6.29.4-21
- Rebased to 2.6.29.4-rt17
- The following mrg patches are no longer necessary.
- Patch32, Patch33, Patch34, Patch35, Patch36, Patch37, Patch38, Patch39
- Patch40, Patch42

* Tue Jun 02 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.4-20
- [sched] Increase hung_task_timeout_secs defaul on RT [503758]

* Mon Jun 01 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.4-19
- [ftrace] fix function profiler race (Steven Rostedt) [500156]

* Mon May 25 2009 John Kacur <jkacur@redhat.com> - 2.6.29.4-18
- Rebased to 2.6.29.4-rt16

* Fri May 22 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.4-17
- Rebased to 2.6.29.4
- Rebased rt to 2.6.29.4-rt15
- Enhanced the stability of the function profiler
- Avoid extra wakeups of threads blocked in wait_for_packet()

* Mon May 18 2009 John Kacur <jkacur@redhat.com> - 2.6.29.3-16
- rebased rt to 2.6.29.3-rt14

* Wed May 14 2009 John Kacur <jkacur@redhat.com> - 2.6.29.3-15
- rebased rt to 2.6.29.3-rt13

* Tue May 12 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.3-14
- rebased to 2.6.29.3
- rebased rt to 2.6.29.3-rt12

* Tue May 05 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.2-13
- added the ftrace function profiler patches

* Mon May 04 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.2-12
- rebased RT to 2.6.29.2-rt11

* Wed Apr 29 2009 Clark Williams <williams@redhat.com> - 2.6.29.2-11
- rebased to upstream stable 2.6.29.2 patch
- rebased RT to 2.6.29.2-rt10
- turned on modules CONFIG_KVM, CONFIG_KVM_INTEL and CONFIG_KVM_AMD
  in config-x86-generic and config-x86_64-generic
- added jstultz patch to change NTP parameter SHIFT_PLL from 4 to 2 
  to improve client convergence times 


* Mon Apr 27 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.1-10
- Rebased to PREEMPT_RT patch-2.6.29.1-rt9

* Mon Apr 20 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29.1-9
- Rebased to 2.6.29.1-rt8
- Removed redundant patches

* Fri Apr 17 2009 Clark Williams <williams@redhat.com> - 2.6.29.1-8
- Disabled CONFIG_DRM_I915_KMS again.
- Disabled CONFIG_GROUP_SCHED 
- added patch to fix lockdep selftest
- added ibm-amd-edac driver
- increased stack trace entries
- sched_yield() workaround

* Wed Apr 15 2009 Clark Williams <williams@redhat.com> - 2.6.29.1-7
- added patch for bundling f/w with AIC94xx driver
- added patch for bundling f/w with QLA2xxx driver
- added patch to implement rt_downgrade_write (rostedt)
- added logarithmic timekeeping accumulation patch from jstultz
- added specfile logic to copy arch includes for devel package

* Mon Apr 13 2009 Clark Williams <williams@redhat.com> - 2.6.29.1-6
- rebased RT to 2.6.29.1-rt7 (lgoncalv)
- added Nagle algorthim tunable from Chris Snook (BZ460217)
- added IBM's rtl driver (for SMI remediation)
- modified specfile to copy stap trace headers (BZ495560)
- added forward ported HS21 tmid patch
- added jvrao's QLA2XXX MSI workaround patch from LKML

* Thu Apr  9 2009 Clark Williams <williams@redhat.com> - 2.6.29.1-5
- rebased RT to 2.6.29.1-rt6
- ported RHEL-RT_AMD_TSC_sync_PN.patch from previous MRG RT
- ported bz465745-rtc-fix_kernel_panic_on_second_use_of_SIGIO_nofitication.patch from previous MRG RT
- ported bz465837-rtc-compat-rhel5.patch-ported-to-V2.patch from previous MRG RT
- ported bz467739-ibm-add-amd64_edac-driver.patch from previous MRG RT
- ported forward-port-of-limit-i386-ram-to-16gb.patch from previous MRG RT
- ported forward-port-of-quiet-plist-warning.patch from previous MRG RT
- ported irq-tracer-fix.patch from previous MRG RT
- Disabled CONFIG_DRM_I915_KMS.
- added config sanity check script
- reworked configs to remove duplicate definitions
- added configs to satisfy new 2.6.29.1 requirements

* Mon Apr  6 2009 Clark Williams <williams@redhat.com> - 2.6.29.1-4
- enabled CONFIG_DYNAMIC_FTRACE for production kernels

* Fri Apr  3 2009 Clark Williams <williams@redhat.com> - 2.6.29-3
- rebased to stable 2.6.29.1
- rebased RT to 2.6.29.1-rt4
- added IBM RTSJ patches
- added RHEL OOM patches
- BZ 384881 patch forward port
- added dynticks-off-by-default patch
- turned off *_GROUP_SCHED in config-generic
- added compression configs in config-generic

* Thu Mar 26 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29-2
- Redefined config options upon suggestions from the MRG-RT team

* Wed Mar 25 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29-1
- Rebased to 2.6.29-rt1

* Tue Mar 24 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29-rc8-2
- Rebased to 2.6.29-rc8-rt4

* Fri Mar 20 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29-rc8-1
- Rebased to 2.6.29-rc8-rt1

* Mon Mar 16 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29-rc7-1
- Rebased to 2.6.29-rc7-rt1

* Mon Mar 09 2009 Luis Claudio R. Goncalves <lgoncalv@redhat.com> - 2.6.29-rc6-1
- Added kernel 2.6.29-rc6
- Added PREEMPT_RT patch-2.6.29-rc6-rt3.patch
- Adjusted the spec file


