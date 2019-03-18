Summary: Opencode Config Manager
Name: occonfman
Version: 1.0.1
Release: 16%{?dist}%{?ocrel}
BuildArch: noarch
URL: http://www.opencode.com
License: Commercial
Group: opencode
Source: occonfman-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Packager: hristo.slavov@opencode.com
Requires: python34, python34-libs, ocpytools

%description
Opencode conf manager

GIT commit

Contact: hristo.slavov@opencode.com

%prep
%setup -q

%clean
rm -rf $RPM_BUILD_ROOT

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/aux0/customer/containers/occonfman/bin/
mkdir -p $RPM_BUILD_ROOT/aux0/customer/containers/occonfman/etc/
mkdir -p $RPM_BUILD_ROOT/aux0/customer/containers/occonfman/lib/
mkdir -p $RPM_BUILD_ROOT/aux0/customer/containers/occonfman/run/
mkdir -p $RPM_BUILD_ROOT/aux1/occonfman/logs/
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/

cp -f lib/* $RPM_BUILD_ROOT/aux0/customer/containers/occonfman/lib/
cp -f bin/* $RPM_BUILD_ROOT/aux0/customer/containers/occonfman/bin/

ln -sf /aux0/customer/containers/occonfman/bin/occonfman.py $RPM_BUILD_ROOT/usr/local/bin/occonfman

%files
%defattr(-,root,root)
%dir /aux0/customer/containers/occonfman/
/aux0/customer/containers/occonfman/bin
/aux0/customer/containers/occonfman/etc
/aux0/customer/containers/occonfman/lib
/aux0/customer/containers/occonfman/run
/aux1/occonfman/logs/

/usr/local/bin/occonfman

%changelog

