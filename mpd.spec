%global  mpd_user            mpd
%global  mpd_group           %{mpd_user}

%global  mpd_homedir         %{_localstatedir}/lib/mpd
%global  mpd_logdir          %{_localstatedir}/log/mpd
%global  mpd_musicdir        %{mpd_homedir}/music
%global  mpd_playlistsdir    %{mpd_homedir}/playlists

%global  mpd_configfile      %{_sysconfdir}/mpd.conf
%global  mpd_dbfile          %{mpd_homedir}/mpd.db
%global  mpd_logfile         %{mpd_logdir}/mpd.log
%global  mpd_statefile       %{mpd_homedir}/mpdstate

Name:           mpd
Version:        0.16.8
Release:        1%{?dist}
Summary:        The Music Player Daemon
License:        GPLv2+
Group:          Applications/Multimedia
URL:            http://mpd.wikia.com/

Source0:        http://downloads.sourceforge.net/musicpd/%{name}-%{version}.tar.bz2
Source1:        mpd.init
Patch0:         mpd-0.16.7-default-pulseaudio.patch

BuildRequires:     alsa-lib-devel
BuildRequires:     audiofile-devel
BuildRequires:     autoconf
BuildRequires:     avahi-glib-devel
BuildRequires:     bzip2-devel
BuildRequires:     faad2-devel
BuildRequires:     ffmpeg-devel
BuildRequires:     flac-devel
BuildRequires:     jack-audio-connection-kit-devel
BuildRequires:     lame-devel
BuildRequires:     libao-devel
BuildRequires:     libcue-devel
BuildRequires:     libcurl-devel
BuildRequires:     libid3tag-devel
BuildRequires:     libmad-devel
BuildRequires:     libmms-devel
BuildRequires:     libmodplug-devel
BuildRequires:     libmpcdec-devel
BuildRequires:     libogg-devel
BuildRequires:     libsamplerate-devel
BuildRequires:     libshout-devel 
BuildRequires:     libsidplay-devel
BuildRequires:     libvorbis-devel
BuildRequires:     mikmod-devel
BuildRequires:     pulseaudio-lib-devel
BuildRequires:     sqlite-devel
BuildRequires:     wavpack-devel
BuildRequires:     zlib-devel
BuildRequires:     zziplib-devel
Requires(pre):     shadow-utils
Requires(post):    chkconfig
Requires(preun):   chkconfig initscripts
Requires(postun):  initscripts
Conflicts:         mpich2

%description
Music Player Daemon (MPD) is a flexible, powerful, server-side application for
playing music. Through plugins and libraries it can play a variety of sound
files (e.g., OGG, MP3, FLAC, AAC, WAV) and can be controlled remotely via its
network protocol. It can be used as a desktop music player, but is also great
for streaming music to a stereo system over a local network. There are many
GUI and command-line applications to choose from that act as a front-end for
browsing and playing your MPD music collection.

%prep
%setup -q
%patch0 -p0

%build
%configure --enable-mikmod --enable-bzip2 --enable-zzip
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{mpd_homedir}
mkdir -p $RPM_BUILD_ROOT%{mpd_logdir}
mkdir -p $RPM_BUILD_ROOT%{mpd_musicdir}
mkdir -p $RPM_BUILD_ROOT%{mpd_playlistsdir}
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
touch $RPM_BUILD_ROOT%{mpd_dbfile}
touch $RPM_BUILD_ROOT%{mpd_logfile}
touch $RPM_BUILD_ROOT%{mpd_statefile}

install -D -p -m644 doc/mpdconf.example $RPM_BUILD_ROOT%{mpd_configfile}

sed -i -e "s|#music_directory.*$|music_directory \"%{mpd_musicdir}\"|g" \
       -e "s|#playlist_directory.*$|playlist_directory \"%{mpd_playlistsdir}\"|g" \
       -e "s|#db_file.*$|db_file \"%{mpd_dbfile}\"|g" \
       -e "s|#log_file.*$|log_file \"%{mpd_logfile}\"|g" \
       -e "s|#state_file.*$|state_file \"%{mpd_statefile}\"|g" \
       -e 's|#user.*$|user "mpd"|g' \
       $RPM_BUILD_ROOT%{mpd_configfile}

sed -e "s|@bindir@|%{_bindir}|g" \
    -e "s|@var@|%{_localstatedir}|g" \
    %{SOURCE1} > $RPM_BUILD_ROOT%{_initrddir}/%{name}

rm -rf $RPM_BUILD_ROOT%{_docdir}/%{name}/

%pre
if [ $1 -eq 1 ]; then
    getent group %{mpd_group} >/dev/null || groupadd -r %{mpd_group}
    getent passwd %{mpd_user} >/dev/null || \
    useradd -r -g %{mpd_group} -d %{mpd_homedir} -s /sbin/nologin \
        -c "Music Player Daemon" %{mpd_user}
    gpasswd -a %{mpd_group} audio || :
    exit 0
fi

%post
if [ "$1" -eq "1" ]; then
        /sbin/chkconfig --add %{name}
else
    # as we switched from running as root.root to mpd.mpd
    # chown the db files and playlists on upgrades
    chown -R %{mpd_user}.%{mpd_group} \
        %{mpd_playlistsdir} > /dev/null 2>&1 ||:
    chown %{mpd_user}.%{mpd_group} \
        %{mpd_dbfile} > /dev/null 2>&1 ||:
    chown %{mpd_user}.%{mpd_group} \
        %{mpd_logfile} > /dev/null 2>&1 ||:
    chown %{mpd_user}.%{mpd_group} \
        %{mpd_statefile} > /dev/null 2>&1 ||:
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
%doc README UPGRADING AUTHORS COPYING
%{_bindir}/%name
%attr(755,root,root) %{_initrddir}/%{name}
%{_mandir}/man1/*
%{_mandir}/man5/*
%config(noreplace) %{_sysconfdir}/mpd.conf

%defattr(-,%{mpd_user},%{mpd_group})
%dir %{mpd_homedir}
%dir %{mpd_musicdir}
%dir %{mpd_playlistsdir}
%ghost %{mpd_dbfile}
%ghost %{mpd_logfile}
%ghost %{mpd_statefile}

%changelog
* Mon Apr 09 2012 Jamie Nguyen <jamie@tomoyolinux.co.uk> - 0.16.8-1
- update to 0.16.8

* Sat Feb 25 2012 Jamie Nguyen <jamie@tomoyolinux.co.uk> - 0.16.7-1
- update to upstream release 0.16.7
- add convenient global variables
- change incorrect --enable-zip to --enable-zzip
- change default log file location to /var/log/mpd/mpd.log
- change default audio output to pulseaudio
- remove obsolete BuildRoot tag, %%clean section and %%defattr
- remove obsolete mpd-error file
- remove obsolete hal fdi file
- do not add mpd to pulse-rt group as system mode is not recommended by
  pulseaudio upstream, and the group no longer exists

* Wed Oct 12 2011 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.16.5-1
- Update to latest upstream release (#1954)

* Mon Sep 26 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.15.13-2
- Rebuilt for FFmpeg-0.8

* Thu Oct 28 2010 Adrian Reber <adrian@lisas.de> - 0.15.13-1
- updated to 0.15.13
- added mpd user to audio group (#1461)

* Wed Sep 29 2010 Adrian Reber <adrian@lisas.de> - 0.15.12-1
- updated to 0.15.12

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
