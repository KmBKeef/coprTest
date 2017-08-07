Name:           alacritty
Summary:        A cross-platform, GPU enhanced terminal emulator
License:        ASL 2.0
Release:        2%{?dist}

%define git_owner       jwilm
%define git_url         https://github.com/%{git_owner}/%{name}

URL:            %{git_url}

%define use_pinned      0
%define pinned          702df40da4ea8585ddfa129cd240c54bab6e42d7
%if %{use_pinned} || %(command -v git > /dev/null; echo $?)
%define git_rev         %{pinned}
%else
%define git_rev         %(git ls-remote %{git_url} HEAD | cut -f 1)
%endif
%define abbrev          %(printf '%0.7s' %{git_rev})

%if "%{pinned}" != "%{git_rev}"
%define bakdate     %(date +%%y%%m%%d_%%H%%M%%S)
%(mv alacritty.spec.new alacritty.spec.new.%{bakdate}.bak 2> /dev/null)
%(sed 's/^\(^[%%]define\spinned\s\+\)\([[:xdigit:]]\+\)/\1%{git_rev}/' \
    alacritty.spec > alacritty.spec.new)
%endif

Version:        0.1.0
Source0:        %{git_url}/tarball/%{git_rev}#/%{git_owner}-%{name}-%{abbrev}.tar.gz

Requires:       freetype-devel
Requires:       fontconfig-devel
Requires:       xclip

BuildRequires:  cmake

# Check ~/.cargo/bin/* before going system-wide
%if %(command -v rustc &> /dev/null; echo $?)
BuildRequires:  rust
%endif
%if %(command -v cargo &> /dev/null; echo $?)
BuildRequires:  cargo
%endif


%description
Alacritty is the fastest terminal emulator in existence. Using the GPU for
rendering enables optimizations that simply aren't possible in other emulators.

%prep
%setup -qn %{git_owner}-%{name}-%{abbrev}
%if "%{pinned}" != "%{git_rev}"
(
    awkarg='/^\[package\]$/,/^version/ {gsub(/["]/, "");'
    awkarg+='if ($1 == "version") print $NF}'
    vcheck=$(awk "$awkarg" Cargo.toml) || :
    if [[ "$vcheck" != %{version} ]]; then
        sedarg='s/^\(^Release:\s\+\)\([[:digit:]]\+\)/\11/;'
        sedarg+='s/^\(^Version:\s\+\)\([[:digit:].]\+\)/\1'"$vcheck/"
        sed -i "$sedarg" %{_specdir}/alacritty.spec.new
        echo "NOTICE - the version has changed from %{version} to $vcheck"
    fi || :
)
%endif

%build
cargo build --release

%install
install -D -m755 target/release/%{name} %{buildroot}/%{_bindir}/%{name}
install -D -m644 Alacritty.desktop %{buildroot}/%{_datadir}/applications/Alacritty.desktop
install -d -m755 %{buildroot}/%{_datadir}/%{name}
install -m644 alacritty*.yml %{buildroot}/%{_datadir}/%{name}
install -d -m755 %{buildroot}/%{_datadir}/terminfo/a
tic -o %{buildroot}/%{_datadir}/terminfo alacritty.info

%post
update-desktop-database &> /dev/null ||:

%postun
update-desktop-database &> /dev/null ||:

%posttrans
desktop-file-validate %{_datadir}/applications/alacritty.desktop &> /dev/null || :

%files
%{_bindir}/alacritty
%{_datadir}/applications/*.desktop
%{_datadir}/%{name}/*.yml
%{_datadir}/terminfo/*

%changelog
* Sat Jun 17 2017 Poppy Schmo <poppyschmoATprouxTawnMaighlDawtCahm> 0.1.0-2
- Remove trailing abbrev sha from version number

* Mon Apr 10 2017 Poppy Schmo <poppyschmoATprouxTawnMaighlDawtCahm> 0.1.0-1
- Copy PKGBUILD from the AUR https://aur.archlinux.org/packages/alacritty-git

