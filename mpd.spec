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
Version:        0.23.12
Release:        2%{?dist}
Summary:        The Music Player Daemon
License:        GPLv2+
URL:            https://www.musicpd.org

Source0:        %{url}/download/mpd/0.23/mpd-%{version}.tar.xz
Source1:        %{url}/download/mpd/0.23/mpd-%{version}.tar.xz.sig
Source2:        https://pgp.key-server.io/download/0x236E8A58C6DB4512#/gpgkey.asc
# Note that the 0.18.x branch doesn't yet work with Fedora's version of
# libmpcdec which needs updating.
# https://bugzilla.redhat.com/show_bug.cgi?id=1014468
# http://bugs.musicpd.org/view.php?id=3814#bugnotes
Source3:        mpd.logrotate
Source4:        mpd.tmpfiles.d
Source5:        mpd.xml
Patch0:         mpd-0.23-mpdconf.patch
Patch1:         mpd-0.20-remove_NoNewPrivileges.patch
Patch2:         timidity_path.patch

BuildRequires:     alsa-lib-devel
BuildRequires:     audiofile-devel
BuildRequires:     meson
BuildRequires:     boost-devel
BuildRequires:     bzip2-devel
BuildRequires:     faad2-devel
BuildRequires:     ffmpeg-devel
BuildRequires:     firewalld-filesystem
BuildRequires:     flac-devel
BuildRequires:     fmt-devel
BuildRequires:     gcc
BuildRequires:     gnupg2
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
BuildRequires:     avahi-compat-libdns_sd-devel
BuildRequires:     avahi-devel
BuildRequires:     dbus-devel
BuildRequires:     expat-devel
BuildRequires:     fluidsynth-devel
BuildRequires:     libopenmpt-devel
BuildRequires:     libsndfile-devel
BuildRequires:     libupnp-devel
%if 0%{?fedora} || 0%{?rhel} <= 8
BuildRequires:     libmpdclient-devel
BuildRequires:     libnfs-devel
BuildRequires:     mikmod-devel
BuildRequires:     wildmidi-devel
%endif
%if 0%{?fedora}
BuildRequires:     pipewire-devel > 0.3
%ifnarch %{arm}
BuildRequires:     liburing-devel
%endif
%endif
BuildRequires:     mpg123-devel
BuildRequires:     openal-soft-devel
BuildRequires:     python3-sphinx
BuildRequires:     twolame-devel
# Need new version with SV8
# BuildRequires:     libmpcdec-devel

BuildRequires:     libogg-devel
BuildRequires:     libsamplerate-devel
BuildRequires:     libshout-devel
BuildRequires:     libsidplayfp-devel
BuildRequires:     libvorbis-devel
BuildRequires:     opus-devel
BuildRequires:     pcre2-devel
BuildRequires:     pkgconfig(libpulse)
BuildRequires:     soxr-devel
BuildRequires:     sqlite-devel
BuildRequires:     systemd-devel
BuildRequires:     wavpack-devel
BuildRequires:     yajl-devel
BuildRequires:     zlib-devel
BuildRequires:     zziplib-devel

Requires(pre):     shadow-utils
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd
Requires:          (mpd-firewalld = %{?epoch}:%{version}-%{release} if firewalld)
Requires:          ffmpeg-libs%{?_isa}

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
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%autosetup -p1

# Force python3-sphinx
sed -i -e 's@sphinx-build@sphinx-build-3@g' doc/meson.build

# redhat meson is too old
%if 0%{?rhel}
sed -i -e 's@>= 0.56.0@>= 0.55.0@g'  meson.build
%endif

%build
%{meson} \
    -Dsystemd_system_unit_dir=%{_unitdir} \
    -Dsystemd_user_unit_dir=%{_userunitdir} \
    -Dadplug=disabled \
    -Dipv6=enabled \
    -Dpipe=true \
%ifarch %{arm}
    -Dio_uring=disabled \
%endif
%if 0%{?rhel}
    -Dio_uring=disabled \
%if 0%{?rhel} > 8
    -Dlibmpdclient=disabled \
    -Dmikmod=disabled \
    -Dnfs=disabled \
    -Dwildmidi=disabled \
%endif
    -Dpipewire=disabled \
    -Dshout=disabled \
%endif
    -Ddocumentation=auto \
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

install -p -D -m 0644 %{SOURCE3} \
    %{buildroot}%{_sysconfdir}/logrotate.d/mpd

install -p -D -m 0644 %{SOURCE4} \
    %{buildroot}%{_prefix}/lib/tmpfiles.d/mpd.conf
install -p -D -m 0644 %{SOURCE5} \
    %{buildroot}%{_prefix}/lib/firewalld/services/mpd.xml
mkdir -p %{buildroot}/run
install -d -m 0755 %{buildroot}/%{mpd_rundir}

mkdir -p %{buildroot}%{mpd_homedir}
mkdir -p %{buildroot}%{mpd_logdir}
mkdir -p %{buildroot}%{mpd_musicdir}
mkdir -p %{buildroot}%{mpd_playlistsdir}
touch %{buildroot}%{mpd_dbfile}
touch %{buildroot}%{mpd_logfile}
touch %{buildroot}%{mpd_statefile}

install -D -p -m644 doc/mpdconf.example %{buildroot}%{mpd_configfile}

rm -rf %{buildroot}%{_docdir}/mpd/


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
%doc AUTHORS NEWS README.md
%license COPYING
%{_bindir}/mpd
%{_mandir}/man1/mpd.1*
%{_mandir}/man5/mpd.conf.5*
%{_unitdir}/mpd.service
%{_unitdir}/mpd.socket
%{_userunitdir}/mpd.service
%{_userunitdir}/mpd.socket
%config(noreplace) %{mpd_configfile}
%config(noreplace) %{_sysconfdir}/logrotate.d/mpd
%{_prefix}/lib/tmpfiles.d/mpd.conf
%{_datadir}/icons/hicolor/scalable/apps/mpd.svg

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
* Tue Feb 28 2023 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.12-2
- Rebuild for new ffmpeg

* Tue Jan 17 2023 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.12-1
- Update to 0.23.12

* Mon Nov 28 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.11-1
- Update to 0.23.11

* Fri Oct 14 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.10-1
- Update to 0.23.10

* Fri Aug 19 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.9-1
- Update to 0.23.9

* Fri Jul 22 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.8-2
- Rebuild for new ffmpeg

* Sat Jul 09 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.8-1
- Update to 0.23.8

* Tue May 10 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.7-1
- Update to 0.23.7

* Mon Mar 14 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.6-1
- Update to 0.23.6

* Sat Feb 05 2022 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.5-2
- Rebuilt for ffmpeg

* Thu Dec 09 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.5-1
- Update to 0.23.5

* Tue Nov 16 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.4-1
- Update to 0.23.4

* Tue Nov 09 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.3-2
- Rebuilt for new ffmpeg snapshot

* Sun Oct 31 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.3-1
- Update to 0.23.3

* Fri Oct 22 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.2-1
- Update to 0.23.2

* Tue Oct 19 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23.1-1
- Update to 0.23.1

* Mon Oct 18 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23-2
- Fix pipewire samplerate

* Thu Oct 14 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.23-1
- Update to 0.23

* Fri Aug 27 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.11-1
- Update to 0.22.11

* Sat Aug 07 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.10-1
- Update to 0.22.10

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1:0.22.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed Jun 23 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.9-1
- Update to 0.22.9

* Tue Jun 08 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.8-2
- Drop fluidsynth support due to poor fedora maintenance (.so bumps to stable releases)

* Sun May 23 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.8-1
- Update to 0.22.8

* Fri May 21 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.7-1
- Update to 0.22.7

* Tue May 11 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.6-2
- rebuilt

* Wed Feb 17 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.6-1
- Update to 0.22.6

* Mon Feb 15 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.5-1
- Update to 0.22.5

* Wed Feb 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1:0.22.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Jan 21 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.4-1
- Update to 0.22.4

* Wed Jan  6 2021 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.3-3
- Disable adplug support

* Thu Dec 31 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.3-2
- Rebuilt for new ffmpeg snapshot

* Fri Nov  6 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.3-1
- Update to 0.22.3

* Wed Oct 28 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.2-1
- Update to 0.22.2

* Sat Oct 17 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.22.1-1
- Update to 0.22.1

* Sun Oct 11 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.22-1
- Update to 0.22

* Wed Sep 23 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.26-1
- Update to 0.21.26

* Tue Aug 18 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1:0.21.25-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sat Jul 18 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.25-2
- Rebuilt

* Wed Jul 08 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.25-1
- Update to 0.21.25

* Thu Jun 11 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.24-1
- Update to 0.21.24

* Fri Apr 24 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.23-1
- Update to 0.21.23

* Fri Apr 10 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.22-2
- Rebuild for new libcdio version

* Sat Apr 04 2020 leigh123linux <leigh123linux@googlemail.com> - 1:0.21.22-1
- Update to 0.21.22

* Thu Mar 19 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.21-1
- Update to 0.21.21

* Sat Feb 22 2020 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1:0.21.20-2
- Rebuild for ffmpeg-4.3 git

* Thu Feb 20 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.20-1
- Update to 0.21.20

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1:0.21.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jan 17 2020 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.19-1
- Update to 0.21.19

* Wed Dec 25 2019 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.18-1
- Update to 0.21.18

* Tue Dec 17 2019 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.17-1
- Update to 0.21.17

* Sun Dec 01 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.16-2
- Rebuilt for new libicu

* Wed Oct 16 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.16-1
- Update to 0.21.16

* Thu Sep 26 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.15-1
- Update to 0.21.15

* Wed Sep 11 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.14-3
- Rebuild for new libnfs version

* Sat Aug 31 2019 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.14-2
- Rebuild for libsidplayfp-2.0.0 (rfbz #5374)

* Thu Aug 22 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.14-1
- Update to 0.21.14

* Mon Aug 12 2019 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.13-1
- Update to 0.21.13

* Tue Aug 06 2019 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.12-2
- Rebuild for new ffmpeg version

* Sat Aug 03 2019 Leigh Scott <leigh123linux@gmail.com> - 1:0.21.12-1
- Update to 0.21.12

* Thu Jul 04 2019 Leigh Scott <leigh123linux@googlemail.com> - 1:0.21.11-1
- Update to 0.21.11
- Clean up

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

