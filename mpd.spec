%define _default_patch_fuzz 2

Name:           mpd
Version:        0.15.11
Release:        1%{?dist}
Summary:        The Music Player Daemon
License:        GPLv2+
Group:          Applications/Multimedia
URL:            http://mpd.wikia.com/
Source:         http://downloads.sourceforge.net/musicpd/mpd-0.15.11.tar.bz2
Source1:        mpd.init
Source2:        95-grant-audio-devices-to-mpd.fdi
Patch0:         mpd.git-9e9d7b73d2165f197eeec12ee953add5f49746b7.patch
Patch1:         mpd.git-f3a5b753ae053eb1a862343b0fd3d62973cacc18.patch
Patch2:         mpd.git-00503c9251141b427457c17a9677444bf29c3992.patch
Patch3:         6a071efa2794806ad5a2a62f0fcdee4b1843b41f.patch

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
BuildRequires:  avahi-glib-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  faad2-devel
BuildRequires:  libmad-devel
BuildRequires:  lame-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  wavpack-devel
BuildRequires:  libcurl-devel
BuildRequires:  libmms-devel
BuildRequires:  libmodplug-devel
BuildRequires:  libsidplay-devel
BuildRequires:  bzip2-devel
BuildRequires:  zziplib-devel
BuildRequires:  sqlite-devel
BuildRequires:  autoconf
BuildRequires:  libcue-devel
Requires(pre):  shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig /sbin/service
Requires(postun): /sbin/service

Conflicts: mpich2

%description
Music Player Daemon (MPD) allows remote access for playing music (MP3, Ogg
Vorbis, FLAC, Mod, AAC and wave files) and managing playlists. MPD is designed
for integrating a computer into a stereo system that provides control for music
playback over a local network. It is also makes a great desktop music player,
especially if you are a console junkie, like frontend options or restart X often

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
autoreconf --force --install

%build
%configure --enable-mikmod --enable-bzip2 --enable-zip
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
%{__sed} -i -e "s,~/.mpd/log,%{_localstatedir}/lib/%{name}/mpd.log,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/error-log,%{_localstatedir}/lib/%{name}/mpd.error,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/database,%{_localstatedir}/lib/%{name}/mpd.db,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,~/.mpd/state,%{_localstatedir}/lib/%{name}/mpdstate,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,#state_file,state_file,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,#music_directory,music_directory,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,#playlist_directory,playlist_directory,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,#db_file,db_file,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e "s,#log_file,log_file,g" $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
%{__sed} -i -e 's,#user.*"nobody",user "mpd",g' $RPM_BUILD_ROOT%{_sysconfdir}/mpd.conf
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
# fix for pulseaudio playback (#230)
usermod -aG pulse-rt mpd
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
%doc README UPGRADING AUTHORS COPYING
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
* Tue Jul 20 2010 Adrian Reber <adrian@lisas.de> - 0.15.11-1
- updated to 0.15.11 (#1301)

* Fri Jan 22 2010 Adrian Reber <adrian@lisas.de> - 0.15.8-1
- updated to 0.15.8 (#1042)

* Wed Dec 02 2009 Adrian Reber <adrian@lisas.de> - 0.15.6-1
- updated to 0.15.6 (#989)
- added BR libcue-devel (#930)

* Mon Nov 09 2009 Adrian Reber <adrian@lisas.de> - 0.15.5-1
- updated to 0.15.5 (#929)

* Wed Oct 21 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.15.2-2
- rebuild for new ffmpeg

* Tue Aug 25 2009 Adrian Reber <adrian@lisas.de> - 0.15.2-1
- updated to 0.15.2
- applied patches from David Woodhouse to fix
  "mpd fails to play to usb audio device" (#731)
- fix description (#765)

* Mon Jun 29 2009 Adrian Reber <adrian@lisas.de> - 0.15-1
- updated to 0.15
- added "Conflicts: mpich2" (#593)
- added BR libmms-devel, libmodplug-devel, libsidplay-devel, bzip2-devel
           zziplib-devel, sqlite-devel
- changed BR avahi-devel to avahi-glib-devel
- adapted config file fixups to newest config file layout

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.14.2-2
- rebuild for new F11 features

* Fri Feb 20 2009 Adrian Reber <adrian@lisas.de> - 0.14.2-1
- updated to 0.14.2

* Sat Jan 31 2009 Adrian Reber <adrian@lisas.de> - 0.14-4
- added BR libcurl-devel (#326)

* Sat Dec 27 2008 Adrian Reber <adrian@lisas.de> - 0.14-3
- updated to 0.14 (#229, #280)
- add mpd user to group pulse-rt (#230)
- added BR lame-devel, wavpack-devel, ffmpeg-devel

* Sun Sep 28 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.13.2-2
- rebuild

* Fri Jul 25 2008 Adrian Reber <adrian@lisas.de> - 0.13.2-1
- updated to 0.13.2
- added _default_patch_fuzz define

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
