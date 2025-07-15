%bcond_without	tests
Summary:	Small XPath syntax decoder
Name:		tinyxpath
Version:	1.3.1
Release:	1
License:	zlib
Group:		Libraries
URL:		http://tinyxpath.sourceforge.net/
Source0:	http://downloads.sourceforge.net/tinyxpath/%{name}_1_3_1.zip
# Source0-md5:	043f9b3e2e7cca3e98324ce41983e7a3
# tinyxpath include a bundled version of tinyxml
Patch0:		%{name}.remove_bundled_tinyxml.patch
# Fix false-positive of the binary test (see https://sourceforge.net/p/tinyxpath/support-requests/7/ )
Patch1:		%name.fix_test.patch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	tinyxml-devel

%description
TinyXPath is a small footprint XPath syntax decoder, written in C++.
- Syntax decoding
- Application to a TinyXML tree
- Function to extract a result from a tree (string, node set or
  integer)

%package        devel
Summary:	Development files for %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	tinyxml-devel

%description    devel
The %{name}-devel package contains library and header files for
developing applications that use %{name}.

%prep
%setup -q -c %{name}-%{version}
%patch -P0
%patch -P1
rm -rf tinyxml* tinystr*

# Correct some errors due to bundled tinyxml
sed -i 's+TiXmlNode::+TiXmlNode::TINYXML_+g' *.cpp
sed -i 's+#include "tinystr.h"+//#include "tinystr.h"+g' *.h

# Fix wrong EOF encoding
sed -i 's/\r$//' AUTHORS

%build
%{__make} -f Makefile.configure
# Build with -fPIC for the library
%configure \
   CPPFLAGS="-fPIC %{rpmcppflags}"
%{__make}

# Not really designed to be build as lib, DYI
%{__cxx} $RPM_OPT_FLAGS -shared -o lib%{name}.so.0.1 \
   -Wl,-soname,lib%{name}.so.0.1 `ls *.o | grep -v main.o` -ltinyxml


%if %{with tests}
./tinyxpath
grep -q '<em>' out.htm && false
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# Install headers by hands.
install -d $RPM_BUILD_ROOT%{_includedir}/%{name}
install -pDm644 *.h $RPM_BUILD_ROOT%{_includedir}/%{name}

#Install lib by hands.
install -d $RPM_BUILD_ROOT%{_libdir}
cp -p lib%{name}.so.0.1 $RPM_BUILD_ROOT%{_libdir}
ln -s lib%{name}.so.0.1 $RPM_BUILD_ROOT%{_libdir}/lib%{name}.so.0
ln -s lib%{name}.so.0.1 $RPM_BUILD_ROOT%{_libdir}/lib%{name}.so

# binary, whicih is only for test
rm $RPM_BUILD_ROOT%{_bindir}/tinyxpath

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS
%attr(755,root,root) %ghost %{_libdir}/lib%{name}.so.0
%attr(755,root,root) %{_libdir}/lib%{name}.so.0.*

%files devel
%defattr(644,root,root,755)
%{_includedir}/%{name}
%attr(755,root,root) %{_libdir}/lib%{name}.so
