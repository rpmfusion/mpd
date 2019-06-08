%global  _hardened_build     1

%global  mpd_user            mpd
%global  mpd_group           %{mpd_user}

%global  mpd_homedir         %{_localstatedir}/lib/mpd
%global  mpd_logdir          %{_localstatedir}/log/mpd
%global  mpd_musicdir        %{mpd_homedir}/music
%global  mpd_playlistsdir    %{mpd_homedir}/playlists
%global  mpd_rundir          /run/mpd

%global  mpd_configfile      %{_sysconfdir}/mpd.conf
%global  mpd_dbfile          %{mpd_homedir}/mpd.db
%global  mpd_logfile         %{mpd_logdir}/mpd.log
%global  mpd_statefile       %{mpd_homedir}/mpdstate

Name:           mpd
Epoch:          1
Version:        0.21.10
Release:        1%{?dist}
Summary:        The Music Player Daemon
License:        GPLv2+
URL:            https://www.musicpd.org

Source0:        %{url}/download/mpd/0.21/mpd-%{version}.tar.xz
Source1:        %{url}/download/mpd/0.21/mpd-%{version}.tar.xz.sig
# Note that the 0.18.x branch doesn't yet work with Fedora's version of
# libmpcdec which needs updating.
# https://bugzilla.redhat.com/show_bug.cgi?id=1014468
# http://bugs.musicpd.org/view.php?id=3814#bugnotes
Source2:        mpd.logrotate
Source3:        mpd.tmpfiles.d
Source4:        mpd.xml
Patch0:         mpd-0.18-mpdconf.patch
Patch1:         mpd-0.20-remove_NoNewPrivileges.patch

BuildRequires:     alsa-lib-devel
BuildRequires:     audiofile-devel
BuildRequires:     meson
BuildRequires:     boost-devel
BuildRequires:     bzip2-devel
BuildRequires:     faad2-devel
BuildRequires:     ffmpeg-devel
BuildRequires:     firewalld-filesystem
BuildRequires:     flac-devel
BuildRequires:     gcc
BuildRequires:     jack-audio-connection-kit-devel
BuildRequires:     lame-devel
BuildRequires:     libao-devel
BuildRequires:     libcdio-paranoia-devel
BuildRequires:     libcurl-devel
BuildRequires:     libgcrypt-devel
BuildRequires:     libid3tag-devel
BuildRequires:     libmad-devel
BuildRequires:     libmms-devel
BuildRequires:     libmodplug-devel
BuildRequires:     adplug-devel
BuildRequires:     avahi-glib-devel
BuildRequires:     avahi-compat-libdns_sd-devel
BuildRequires:     avahi-devel
BuildRequires:     dbus-devel
BuildRequires:     expat-devel
BuildRequires:     fluidsynth-devel
BuildRequires:     libmpdclient-devel
BuildRequires:     libnfs-devel
BuildRequires:     libsmbclient-devel
BuildRequires:     libsndfile-devel
BuildRequires:     libupnp-devel
BuildRequires:     mpg123-devel
BuildRequires:     openal-soft-devel
BuildRequires:     python3-sphinx
BuildRequires:     twolame-devel
BuildRequires:     wildmidi-devel
# Need new version with SV8
# BuildRequires:     libmpcdec-devel

BuildRequires:     libogg-devel
BuildRequires:     libsamplerate-devel
BuildRequires:     libshout-devel
BuildRequires:     libvorbis-devel
BuildRequires:     mikmod-devel
BuildRequires:     opus-devel
BuildRequires:     pkgconfig(libpulse)
BuildRequires:     soxr-devel
BuildRequires:     sqlite-devel
BuildRequires:     systemd-devel
BuildRequires:     wavpack-devel
BuildRequires:     yajl-devel
BuildRequires:     zlib-devel
BuildRequires:     zziplib-devel
BuildRequires:     libsidplayfp-devel

Requires(pre):     shadow-utils
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd
Requires:          (%{name}-firewalld = %{?epoch}:%{version}-%{release} if firewalld)

%description
Music Player Daemon (MPD) is a flexible, powerful, server-side application for
playing music. Through plugins and libraries it can play a variety of sound
files (e.g., OGG, MP3, FLAC, AAC, WAV) and can be controlled remotely via its
network protocol. It can be used as a desktop music player, but is also great
for streaming music to a stereo system over a local network. There are many
GUI and command-line applications to choose from that act as a front-end for
browsing and playing your MPD music collection.


%package firewalld
Summary: FirewallD metadata file for MPD
Requires: firewalld-filesystem
Requires(post): firewalld-filesystem

%description firewalld
This package contains FirewallD file for MPD.


%prep
%setup -q
%patch0 -p0
%patch1 -p1
# Force python3-sphinx
sed -i -e 's@sphinx-build@sphinx-build-3@g' doc/meson.build

%build
%{meson} \
    -Dsystemd_system_unit_dir=%{_unitdir} \
    -Dsystemd_user_unit_dir=%{_userunitdir} \
    -Dipv6=enabled \
    -Dpipe=true \
    -Ddocumentation=true \
    -Dsolaris_output=disabled \
    -Dsndio=disabled \
    -Dchromaprint=disabled \
    -Dgme=disabled \
    -Dmpcdec=disabled \
    -Dshine=disabled \
    -Dtremor=disabled

%{meson_build}

%install
%{meson_install}

install -p -D -m 0644 %{SOURCE2} \
    %buildroot%{_sysconfdir}/logrotate.d/mpd

install -p -D -m 0644 %{SOURCE3} \
    %buildroot%{_prefix}/lib/tmpfiles.d/mpd.conf
install -p -D -m 0644 %{SOURCE4} \
    %buildroot%{_prefix}/lib/firewalld/services/mpd.xml
mkdir -p %{buildroot}/run
install -d -m 0755 %{buildroot}/%{mpd_rundir}

mkdir -p %buildroot%{mpd_homedir}
mkdir -p %buildroot%{mpd_logdir}
mkdir -p %buildroot%{mpd_musicdir}
mkdir -p %buildroot%{mpd_playlistsdir}
touch %buildroot%{mpd_dbfile}
touch %buildroot%{mpd_logfile}
touch %buildroot%{mpd_statefile}

install -D -p -m644 doc/mpdconf.example %buildroot%{mpd_configfile}
sed -i -e "s|#music_directory.*$|music_directory \"%{mpd_musicdir}\"|g" \
       -e "s|#playlist_directory.*$|playlist_directory \"%{mpd_playlistsdir}\"|g" \
       -e "s|#db_file.*$|db_file \"%{mpd_dbfile}\"|g" \
       -e "s|#log_file.*$|log_file \"%{mpd_logfile}\"|g" \
       -e "s|#state_file.*$|state_file \"%{mpd_statefile}\"|g" \
       -e 's|#user.*$|user "mpd"|g' \
       %buildroot%{mpd_configfile}

rm -rf %buildroot%{_docdir}/%{name}/


%pre
if [ $1 -eq 1 ]; then
    getent group %{mpd_group} >/dev/null || groupadd -r %{mpd_group}
    getent passwd %{mpd_user} >/dev/null || \
        useradd -r -g %{mpd_group} -d %{mpd_homedir} \
            -s /sbin/nologin -c "Music Player Daemon" %{mpd_user}
    gpasswd -a %{mpd_group} audio || :
    exit 0
fi

%post
%systemd_post mpd.service

%preun
%systemd_preun mpd.service

%postun
%systemd_postun_with_restart mpd.service

%post firewalld
%firewalld_reload


%files
%doc AUTHORS README.md
%license COPYING
%{_bindir}/%{name}
%{_mandir}/man1/mpd.1*
%{_mandir}/man5/mpd.conf.5*
%{_unitdir}/mpd.service
%{_unitdir}/mpd.socket
%{_userunitdir}/mpd.service
%{_userunitdir}/mpd.socket
%config(noreplace) %{mpd_configfile}
%config(noreplace) %{_sysconfdir}/logrotate.d/mpd
%{_prefix}/lib/tmpfiles.d/mpd.conf
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%defattr(-,%{mpd_user},%{mpd_group})
%dir %{mpd_homedir}
%dir %{mpd_logdir}
%dir %{mpd_musicdir}
%dir %{mpd_playlistsdir}
%ghost %dir %{mpd_rundir}
%ghost %{mpd_dbfile}
%ghost %{mpd_logfile}
%ghost %{mpd_statefile}

%files firewalld
%{_prefix}/lib/firewalld/services/mpd.xml


%changelog
* Sat Jun 08 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.10-1
- Update to 0.21.10

* Wed May 22 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.9-1
- Update to 0.21.9

* Wed Apr 24 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.8-1
- Update to 0.21.8

* Wed Apr 03 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.7-1
- Update to 0.21.7
- Add upstream commit to fix gcc-9 build issue

* Mon Mar 18 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.6-1
- Update to 0.21.6

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1:0.21.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Feb 25 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.5-2
- Add BuildRequires firewalld-filesystem

* Sat Feb 23 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.5-1
- Update to 0.21.5
- Force python3-sphinx for docs

* Wed Jan 16 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.4-2
- Add firewalld sub-package

* Mon Jan 14 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.4-1
- Update to 0.21.4
- Add changes for meson build

* Thu Oct 25 2018 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.22-1
- Update to 0.20.22
- Switch buildroot macro

* Wed Oct 17 2018 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.21-1
- Update to 0.20.21
- Remove Group tag

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1:0.20.19-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 09 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1:0.20.19-2
- Update to add BRs for plugins
- rpmfusionbz: 4961

* Sun Apr 29 2018 Sérgio Basto <sergio@serjux.com> - 1:0.20.19-1
- Update 0.20.19

* Thu Mar 08 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1:0.20.16-3
- Rebuilt for new ffmpeg snapshot

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1:0.20.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Feb 06 2018 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.16-1
- Update to 0.20.16

* Sun Jan 28 2018 Nicolas Chauvet <kwizart@gmail.com> - 1:0.20.15-1
- Update to 0.20.15

* Sun Jan 28 2018 Nicolas Chauvet <kwizart@gmail.com> - 1:0.20.10-5
- Rebuilt for libcdio

* Thu Jan 18 2018 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.10-4
- Rebuilt for ffmpeg-3.5 git

* Mon Oct 16 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.10-3
- Rebuild for ffmpeg update

* Sat Oct 07 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.10-2
- Enable sidplay (rfbz #2305)

* Sat Oct 07 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.10-1
- Update to 0.20.10
- Remove NoNewPrivileges (rfbz #4549)

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 1:0.20.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon May 22 2017 Nicolas Chauvet <kwizart@gmail.com> - 1:0.20.8-1
- Update to 0.20.8

* Sat Apr 29 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.6-2
- Rebuild for ffmpeg update

* Mon Apr 10 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:0.20.6-1
- Update to latest upstream version
- Add systemd user service (rfbz #3768)

