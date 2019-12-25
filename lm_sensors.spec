Name:     lm_sensors
Version:  3.4.0
Release:  19
Summary:  Linux-monitoring sensors
# lib/libsensors.3 is licensed Verbatim
# dist-git files are licensed MIT
# and others are licensed by GPLv2+ or LGPLv2+
License:  LGPLv2+ and GPLv2+ and Verbatim and MIT
URL:      http://github.com/groeck/lm-sensors

Source0:  lm-sensors-70f7e0848410b9ca4dde7abff669bbbecbf137e0.tar.gz
Source1:  lm_sensors.sysconfig
Source2:  sensord.sysconfig
Source3:  lm_sensors-modprobe-wrapper
Source4:  lm_sensors-modprobe-r-wrapper
Source5:  sensord.service
Source6:  sensord-service-wrapper
Source7:  lm_sensors.service
Patch6000:pwmconfig-Fix-a-sed-expression.patch

Requires:      kmod, systemd-units
BuildRequires: kernel-headers >= 2.2.16, bison, libsysfs-devel, flex, gawk
BuildRequires: perl-generators, rrdtool-devel, gcc
Provides:      %{name}-libs
Obsoletes:     %{name}-libs

%description
lm_sensors (Linux-monitoring sensors), is a free open source software-tool for Linux
that provides tools and drivers for monitoring temperatures, voltage,
humidity, and fans. It can also detect chassis intrusions.

%package devel
Summary: lm_sensors's development files
Requires: %{name}-libs = %{version}-%{release}
#only lib/libsensors.3 is licensed Verbatim.
License: LGPLv2+ and Verbatim

%description devel
libsensors offers a way for applications to access the hardware
monitoring chips of the system. A system-dependent configuration file
controls how the different inputs are labeled and what scaling factors
have to be applied for the specific hardware, so that the output makes
sense to the user.

%package sensord
Summary:  hardware health monitoring daemon
Requires: %{name} = %{version}-%{release}
# only prog/sensord/sensord.8 is licensed Verbatim.
# dist-git files are licensed MIT.
License:  GPLv2+ and Verbatim and MIT

%description sensord
Daemon that periodically logs sensor readings to syslog or a round-robin
database, and warns of sensor alarms.

%package help
Summary:  Help information for user

%description help
Help information for user

%prep
%autosetup -n lm-sensors-70f7e0848410b9ca4dde7abff669bbbecbf137e0 -p1
rm -f prog/init/sysconfig-lm_sensors-convert prog/hotplug/unhide_ICH_SMBus
mv prog/init/README prog/init/README.initscripts
chmod -x prog/init/fancontrol.init

cp -p %{SOURCE5} sensord.service
cp -p %{SOURCE7} lm_sensors.service
sed -i "s|\@WRAPPER_DIR\@|%{_libexecdir}/%{name}|" sensord.service
sed -i "s|\@WRAPPER_DIR\@|%{_libexecdir}/%{name}|" lm_sensors.service

%build
%set_build_flags
%make_build PREFIX=%{_prefix} LIBDIR=%{_libdir} MANDIR=%{_mandir} \
  EXLDFLAGS="$LDFLAGS" PROG_EXTRA=sensord BUILD_STATIC_LIB=0 user

%install
%make_build PREFIX=%{_prefix} LIBDIR=%{_libdir} MANDIR=%{_mandir} PROG_EXTRA=sensord \
  DESTDIR=$RPM_BUILD_ROOT BUILD_STATIC_LIB=0 user_install

ln -s sensors.conf.5.gz $RPM_BUILD_ROOT%{_mandir}/man5/sensors3.conf.5.gz

mkdir -p -m 755 $RPM_BUILD_ROOT%{_initrddir}
mkdir -p -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/sensors.d
mkdir -p -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -pm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/lm_sensors
install -pm 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/sensord

# service files
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -pm 644 prog/init/fancontrol.service $RPM_BUILD_ROOT%{_unitdir}
install -pm 644 lm_sensors.service           $RPM_BUILD_ROOT%{_unitdir}
install -pm 644 sensord.service              $RPM_BUILD_ROOT%{_unitdir}

# customized modprobe calls
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}/%{name}
install -pm 755 %{SOURCE3} $RPM_BUILD_ROOT%{_libexecdir}/%{name}/lm_sensors-modprobe-wrapper
install -pm 755 %{SOURCE4} $RPM_BUILD_ROOT%{_libexecdir}/%{name}/lm_sensors-modprobe-r-wrapper

# sensord service wrapper
install -pm 755 %{SOURCE6} $RPM_BUILD_ROOT%{_libexecdir}/%{name}/sensord-service-wrapper

# Note non standard systemd scriptlets, since reload / stop makes no sense
# for lm_sensors
%triggerun -- lm_sensors < 3.3.0-2
if [ -L /etc/rc3.d/S26lm_sensors ]; then
    /bin/systemctl enable lm_sensors.service >/dev/null 2>&1 || :
fi
/sbin/chkconfig --del lm_sensors

# ===== main =====
%post
%systemd_post lm_sensors.service
%preun
%systemd_preun lm_sensors.service
%postun
%systemd_postun_with_restart lm_sensors.service

# ==== sensord ===
%post sensord
%systemd_post sensord.service
%preun sensord
%systemd_preun sensord.service
%postun sensord
%systemd_postun_with_restart sensord.service

# ===== libs =====
%ldconfig_scriptlets

%files
%doc CHANGES CONTRIBUTORS doc README*
%doc prog/init/fancontrol.init prog/init/README.initscripts
%license COPYING COPYING.LGPL
%config %{_sysconfdir}/sensors3.conf
%config %{_sysconfdir}/sysconfig/lm_sensors
%dir %{_sysconfdir}/sensors.d
%{_bindir}/*
%{_sbindir}/*
%{_unitdir}/lm_sensors.service
%{_unitdir}/fancontrol.service
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/lm_sensors-modprobe*wrapper
%{_libdir}/*.so.*
%exclude %{_sbindir}/sensord

%files devel
%{_includedir}/sensors
%{_libdir}/lib*.so

%files sensord
%doc prog/sensord/README
%config(noreplace) %{_sysconfdir}/sysconfig/sensord
%{_sbindir}/sensord
%{_unitdir}/sensord.service
%{_libexecdir}/%{name}/sensord-service-wrapper

%files help
%{_mandir}/man*
%exclude %{_mandir}/man8/sensord.8.gz

%changelog
* Thu Dec 12 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.4.0-19
- Fix upgrade problem

* Tue Apr 16 2019 yuejiayan<yuejiayan@huawei.com> - 3.4.0-18
- Type:bugfix
- ID:NA
- SUG:NA
  DESC:pwmconfig: Fix a sed expression

* Mon Apr 1 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.4.0-17
- Package init

