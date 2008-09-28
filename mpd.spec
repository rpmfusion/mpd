Name:           mpd
Version:        0.13.2
Release:        2%{?dist}
Summary:        The Music Player Daemon
License:        GPLv2+
Group:          Applications/Multimedia
URL:            http://www.musicpd.org/
Source:         http://www.musicpd.org/uploads/files/mpd-0.13.2.tar.gz
Source1:        mpd.init
Source2:        95-grant-audio-devices-to-mpd.fdi
Patch0:         mpd.git-ab00513022af940b398601556bfb6256ff220546.patch
Patch1:         mpd.git-1f620ed803e4b5c69b875bb36519c3299022fe9d.patch
Patch2:         mpd.git-de2e69945604f831ece2c4dacf5a545ff1c80056.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libao-devel
BuildRequires:  libogg-devel
BuildRequires:  libvorbis-devel
BuildRequires:  flac-devel
BuildRequires:  audiofile-devel
BuildRequires:  libid3tag-devel
BuildRequires:  mikmod-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  zlib-devel
BuildRequires:  libshout-devel 
BuildRequires:  libmpcdec-devel
BuildRequires:  pulseaudio-lib-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  avahi-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  faad2-devel
BuildRequires:  libmad-devel
Requires(pre):  shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig /sbin/service
Requires(postun): /sbin/service

%description
Music Player Daemon (MPD) allows remote access for playing music (MP3, Ogg
Vorbis, FLAC, Mod, AAC and wave files) and managing playlists. MPD is designed
for integrating a computer into a stereo system that provides control for music
playback over a local network. It is also makes a great desktop music player,
especially if your a console junkie, like frontend options, or restart X often.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# conf file
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/playlists
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/music
mkdir -p $RPM_BUILD_ROOT%{_datadir}/hal/fdi/policy/20thirdparty
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/mpd.log
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/mpd.error
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/mpd.db
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/mpdstate
install -p -m644 doc/mpdconf.example $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/music,%{_localstatedir}/lib/%{name}/music,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/playlists,%{_localstatedir}/lib/%{name}/playlists,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/mpd.log,%{_localstatedir}/lib/%{name}/mpd.log,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/mpd.error,%{_localstatedir}/lib/%{name}/mpd.error,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/mpd.db,%{_localstatedir}/lib/%{name}/mpd.db,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/mpdstate,%{_localstatedir}/lib/%{name}/mpdstate,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,#state_file,state_file,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e 's,#user                            "nobody",user "mpd",g' $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -e "s,@bindir@,%{_bindir},g;s,@var@,%{_localstatedir},g" %{SOURCE1} > $RPM_BUILD_ROOT%{_initrddir}/%{name}
install -p -m644 %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/hal/fdi/policy/20thirdparty

rm -rf $RPM_BUILD_ROOT/%{_docdir}/%{name}/

%clean
rm -rf $RPM_BUILD_ROOT

%pre
#creating mpd user
getent group mpd >/dev/null || groupadd -r mpd
getent passwd mpd >/dev/null || \
useradd -r -g mpd -d %{_localstatedir}/lib/%{name} -s /sbin/nologin \
	-c "Music Player Daemon" mpd
exit 0


%post
if [ "$1" -eq "1" ]; then
        #register %{name} service
        /sbin/chkconfig --add %{name}
else
	# as we switched from running as root.root to mpd.mpd
	# chown the db files and playlists on upgrades
	chown -R mpd.mpd %{_localstatedir}/lib/%{name}/playlists > /dev/null 2>&1 ||:
	chown mpd.mpd %{_localstatedir}/lib/%{name}/mpd.log > /dev/null 2>&1 ||:
	chown mpd.mpd %{_localstatedir}/lib/%{name}/mpd.error > /dev/null 2>&1 ||:
	chown mpd.mpd %{_localstatedir}/lib/%{name}/mpd.db > /dev/null 2>&1 ||:
	chown mpd.mpd %{_localstatedir}/lib/%{name}/mpdstate > /dev/null 2>&1 ||:
fi

%preun
if [ "$1" -eq "0" ]; then
        /sbin/service %{name} stop > /dev/null 2>&1
        /sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" -eq "1" ]; then
        /sbin/service %{name} condrestart > /dev/null 2>&1
fi

%files
%defattr(-,root,root)
%doc README UPGRADING doc/COMMANDS AUTHORS COPYING ChangeLog
%{_bindir}/%name
%attr(755,root,root) %{_initrddir}/%{name}
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_datadir}/hal/fdi/policy/20thirdparty/*fdi
%defattr(-,mpd,mpd)
%config(noreplace) %{_sysconfdir}/mpd.conf
%dir %{_localstatedir}/lib/%{name}
%{_localstatedir}/lib/%{name}/playlists
%{_localstatedir}/lib/%{name}/music
%ghost %{_localstatedir}/lib/%{name}/mpd.log
%ghost %{_localstatedir}/lib/%{name}/mpd.error
%ghost %{_localstatedir}/lib/%{name}/mpd.db
%ghost %{_localstatedir}/lib/%{name}/mpdstate

%changelog
* Sun Sep 28 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.13.2-2
- rebuild

* Fri Jul 25 2008 Adrian Reber <adrian@lisas.de> - 0.13.2-1
- updated to 0.13.2

* Thu May 29 2008 Hans de Goede <j.w.r.degoede@hhs.nl> - 0.13.1-3
- Fix mpd crashing when reading in modtracker files (rh bug 448964)

* Thu Mar 06 2008 Adrian Reber <adrian@lisas.de> - 0.13.1-2
- added patches from Thomas Jansen to run mpd by default
  not as root.root but as mpd.mpd

* Mon Feb 11 2008 Adrian Reber <adrian@lisas.de> - 0.13.1-1
- updated to 0.13.1

* Thu Nov 15 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-4
- another rebuilt for faad2

* Fri Nov 09 2007 Thorsten Leemhuis <fedora[AT]leemhuis.info> - 0.13.0-3
- rebuild after faad2 downgrade to fix undefined symbols

* Sat Oct 13 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-2
- rebuilt for rpmfusion
- updated License

* Sun Jul 29 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-1
- update to 0.13.0
- added dwmw2's patches (#1569)
- fixed rpmlint errors and warnings
- added libsamplerate-devel, avahi-devel and
  jack-audio-connection-kit-devel as BR

* Tue Mar 06 2007 Adrian Reber <adrian@lisas.de> - 0.12.1-3
- added flac-1.1.4 patch

* Sat Mar 03 2007 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.12.1-2
- Rebuild

* Mon Nov 27 2006 Adrian Reber <adrian@lisas.de> - 0.12.1-1
- updated to 0.12.1
- added missing Requires
- removed deletion of user mpd during %%preun
- removed -m (create home) from useradd

* Wed Oct 11 2006 Adrian Reber <adrian@lisas.de> - 0.11.6-6
- rebuilt

* Tue Mar 21 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- Add missing BR zlib-devel

* Thu Mar 09 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- switch to new release field

* Mon Mar 06 2006 Thorsten Leemhuis <fedora[AT]livna.org>
- no build time defines anymore so adapt spec completely to livna

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Sun Nov 28 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.3
- Apply Adrian Reber's patch to use a system-wide daemon, see bug 2234

* Tue Nov 09 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.2
- Prepare for FC3 (different BuildRequires)

* Fri Nov 05 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.fdr.1
- Initial Fedora package (from Mandrake)
