#!/usr/local/bin/perl5 -w

########################################################################
# Hebcal Interactive Jewish Calendar is a web site that lets you
# generate a list of Jewish holidays for any year. Candle lighting times
# are calculated from your latitude and longitude (which can be
# determined by your zip code or closest city).
#
# Copyright (c) 1999  Michael John Radwin.  All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
########################################################################

package hebcal;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DB_File;
use Time::Local;

$author = 'michael@radwin.org';
$expires_date = 'Thu, 15 Apr 2010 20:00:00 GMT';

# constants for DBA export
$PALM_DBA_MAGIC      = 1145176320;
$PALM_DBA_FILENAME   = "hebcal.dba";
$PALM_DBA_INTEGER    = 1;
$PALM_DBA_DATE       = 3;
$PALM_DBA_BOOL       = 6;
$PALM_DBA_REPEAT     = 7;
$PALM_DBA_MAXENTRIES = 2500;

@DoW = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
@MoY_short =
    ('Jan','Feb','Mar','Apr','May','Jun',
     'Jul','Aug','Sep','Oct','Nov','Dec');
%MoY_long = (
	     'x' => '- entire year -',
	     1   => 'January',
	     2   => 'Februrary',
	     3   => 'March',
	     4   => 'April',
	     5   => 'May',
	     6   => 'June',
	     7   => 'July',
	     8   => 'August',
	     9   => 'September',
	     10  => 'October',
	     11  => 'November',
	     12  => 'December',
	     );

# these states are known to span multiple timezones:
# AK, FL, ID, IN, KS, KY, MI, ND, NE, OR, SD, TN, TX
%known_timezones =
    (
     '99692', -10,		# AK west of 170W
     '99547', -10,		# AK west of 170W
     '99660', -10,		# AK west of 170W
     '99742', -10,		# AK west of 170W
     '98791', -10,		# AK west of 170W
     '99769', -10,		# AK west of 170W
     '996', '??',		# west AK
     '324', -6,			# west FL
     '325', -6,			# west FL
     '463', '??',		# Jasper, Lake, LaPorte, Newton, and 
     '464', '??',		#  Porter counties, IN
     '476', '??',		# Gibson, Posey, Spencer, Vanderburgh,
     '477', '??',		#  and Warrick counties, IN
     '677', '??',		# west KS
     '678', '??',		# west KS
     '679', '??',		# west KS
     '799', -7,			# el paso, TX
     '798', '??',		# west TX
     '838', -8,			# north ID
     '835', -8,			# north ID
     '979', '??',		# east OR
     '49858', -6,		# Menominee, MI
     '498', '??',		# west MI
     '499', '??',		# west MI
     'KS', -6,
     'IN', -5,
     'MI', -5,
     'ID', -7,
     'OR', -8,
     'FL', -5,
     'HI', -10,
     'AK', -9,
     'CA', -8,
     'NV', -8,
     'WA', -8,
     'MT', -7,
     'AZ', -7,
     'UT', -7,
     'WY', -7,
     'CO', -7,
     'NM', -7,
     'TX', -6,
     'OK', -6,
     'IL', -6,
     'WI', -6,
     'MN', -6,
     'IA', -6,
     'MO', -6,
     'AR', -6,
     'LA', -6,
     'MS', -6,
     'AL', -6,
     'OH', -5,
     'RI', -5,
     'MA', -5,
     'NY', -5,
     'NH', -5,
     'VT', -5,
     'ME', -5,
     'CT', -5,
     'NJ', -5,
     'DE', -5,
     'DC', -5,
     'PA', -5,
     'WV', -5,
     'VA', -5,
     'NC', -5,
     'SC', -5,
     'GA', -5,
     'MD', -5,
     'PR', -5,
     );

# these cities should have DST set to 'none'
%city_nodst =
    (
     'Berlin', 1,
     'Bogota', 1,
     'Buenos Aires', 1,
     'Johannesburg', 1,
     'London', 1,
     'Mexico City', 1,
     'Toronto', 1,
     'Vancouver', 1,
     );

%city_tz =
    (
     'Atlanta', -5,
     'Austin', -6,
     'Berlin', 1,
     'Baltimore', -5,
     'Bogota', -5,
     'Boston', -5,
     'Buenos Aires', -3,
     'Buffalo', -5,
     'Chicago', -6,
     'Cincinnati', -5,
     'Cleveland', -5,
     'Dallas', -6,
     'Denver', -7,
     'Detroit', -5,
     'Gibraltar', -10,
     'Hawaii', -10,
     'Houston', -6,
     'Jerusalem', 2,
     'Johannesburg', 1,
     'London', 0,
     'Los Angeles', -8,
     'Miami', -5,
     'Mexico City', -6,
     'New York', -5,
     'Omaha', -7,
     'Philadelphia', -5,
     'Phoenix', -7,
     'Pittsburgh', -5,
     'Saint Louis', -6,
     'San Francisco', -8,
     'Seattle', -8,
     'Toronto', -5,
     'Vancouver', -8,
     'Washington DC', -5,
     );

# this doesn't work for weeks that have double parashiot
# todo: automatically get URL from hebrew year
%sedrot = (
   "Bereshit", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/bereishi.htm',
   "Bereshis", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/bereishi.htm',
   "Noach", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/noach.htm',
   "Lech-Lecha", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/lech.htm',
   "Vayera", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/vayera.htm',
   "Chayei Sara", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/chayeisa.htm',
   "Toldot", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/toldos.htm',
   "Toldos", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/toldos.htm',
   "Vayetzei", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/vayeitze.htm',
   "Vayishlach", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/vayishla.htm',
   "Vayeshev", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/vayeshev.htm',
   "Miketz", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/miketz.htm',
   "Vayigash", 'http://www.virtual.co.il/education/education/ohr/tw/5760/bereishi/vayigash.htm',
   "Vayechi", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bereishi/vayechi.htm',
   "Shemot", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/shmos.htm',
   "Shemos", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/shmos.htm',
   "Vaera", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/vaera.htm',
   "Bo", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/bo.htm',
   "Beshalach", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/beshalac.htm',
   "Yitro", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/yisro.htm',
   "Yisro", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/yisro.htm',
   "Mishpatim", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/mishpati.htm',
   "Terumah", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/terumah.htm',
   "Tetzaveh", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/tetzaveh.htm',
   "Ki Tisa", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/kisisa.htm',
   "Ki Sisa", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/kisisa.htm',
   "Vayakhel", 'http://www.virtual.co.il/education/education/ohr/tw/5759/shmos/vayakhel.htm',
   "Pekudei", 'http://www.virtual.co.il/education/education/ohr/tw/5757/shmos/pekudei.htm',
   "Vayikra", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/vayikra.htm',
   "Tzav", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/tzav.htm',
   "Shmini", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/shmini.htm',
   "Tazria", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/tazria.htm',
   "Sazria", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/tazria.htm',
   "Metzora", 'http://www.virtual.co.il/education/education/ohr/tw/5757/vayikra/metzora.htm',
   "Achrei Mot", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/acharei.htm',
   "Achrei Mos", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/acharei.htm',
   "Kedoshim", 'http://www.virtual.co.il/education/education/ohr/tw/5757/vayikra/kedoshim.htm',
   "Emor", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/emor.htm',
   "Behar", 'http://www.virtual.co.il/education/education/ohr/tw/5759/vayikra/behar.htm',
   "Bechukotai", 'http://www.virtual.co.il/education/education/ohr/tw/5757/vayikra/bechukos.htm',
   "Bechukosai", 'http://www.virtual.co.il/education/education/ohr/tw/5757/vayikra/bechukos.htm',
   "Bamidbar", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/bamidbar.htm',
   "Nasso", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/naso.htm',
   "Beha'alotcha", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/behaalos.htm',
   "Beha'aloscha", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/behaalos.htm',
   "Sh'lach", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/shlach.htm',
   "Korach", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/korach.htm',
   "Chukat", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/chukas.htm',
   "Chukas", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/chukas.htm',
   "Balak", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/balak.htm',
   "Pinchas", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/pinchas.htm',
   "Matot", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/matos.htm',
   "Matos", 'http://www.virtual.co.il/education/education/ohr/tw/5759/bamidbar/matos.htm',
   "Masei", '',
   "Devarim", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/devarim.htm',
   "Vaetchanan", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/vaeschan.htm',
   "Vaeschanan", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/vaeschan.htm',
   "Eikev", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/eikev.htm',
   "Re'eh", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/reeh.htm',
   "Shoftim", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/shoftim.htm',
   "Ki Teitzei", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/kiseitze.htm',
   "Ki Seitzei", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/kiseitze.htm',
   "Ki Tavo", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/kisavo.htm',
   "Ki Savo", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/kisavo.htm',
   "Nitzavim", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/nitzavim.htm',
   "Vayeilech", 'http://www.virtual.co.il/education/education/ohr/tw/5758/devarim/vayelech.htm',
   "Ha'Azinu", 'http://www.virtual.co.il/education/education/ohr/tw/5759/devarim/haazinu.htm',
	   );

%tz_names = (
     'auto' => 'Attempt to auto-detect',
     '-5'   => 'GMT -05:00 (U.S. Eastern)',
     '-6'   => 'GMT -06:00 (U.S. Central)',
     '-7'   => 'GMT -07:00 (U.S. Mountain)',
     '-8'   => 'GMT -08:00 (U.S. Pacific)',
     '-9'   => 'GMT -09:00 (U.S. Alaskan)',
     '-10'  => 'GMT -10:00 (U.S. Hawaii)',
     '-11'  => 'GMT -11:00',
     '-12'  => 'GMT -12:00',
     '12'   => 'GMT +12:00',
     '11'   => 'GMT +11:00',
     '10'   => 'GMT +10:00',
     '9'    => 'GMT +09:00',
     '8'    => 'GMT +08:00',
     '7'    => 'GMT +07:00',
     '6'    => 'GMT +06:00',
     '5'    => 'GMT +05:00',
     '4'    => 'GMT +04:00',
     '3'    => 'GMT +03:00',
     '2'    => 'GMT +02:00',
     '1'    => 'GMT +01:00',
     '0'    => 'Greenwich Mean Time',
     '-1'   => 'GMT -01:00',
     '-2'   => 'GMT -02:00',
     '-3'   => 'GMT -03:00',
     '-4'   => 'GMT -04:00',
     );

local($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
$year += 1900;

my($rcsrev) = '$Revision$'; #'
$rcsrev =~ s/\s*\$//g;

my($hhmts) = "<!-- hhmts start -->
Last modified: Mon Dec 27 10:30:40 PST 1999
<!-- hhmts end -->";

$hhmts =~ s/<!--.*-->//g;
$hhmts =~ s/\n//g;
$hhmts =~ s/Last modified: /Software last updated: /g;
$hhmts = 'This page generated: ' . localtime() . '<br>' . $hhmts;

$html_footer = "<hr noshade size=\"1\">
<small>$hhmts ($rcsrev)
<br><br>Copyright &copy; $year Michael John Radwin. All rights
reserved.<br><a target=\"_top\" href=\"/michael/projects/hebcal/\">Frequently
asked questions about this service.</a></small>
</body></html>
";

# boolean options
@opts = ('c','x','o','s','i','h','a','d');
$cmd  = "/home/users/mradwin/bin/hebcal";

# process form params
$q = new CGI;
$q->delete('.s');		# we don't care about submit button

$script_name =  $q->script_name();
$script_name =~ s,/index.html$,/,;

$q->default_dtd("-//W3C//DTD HTML 4.0 Transitional//EN\"\n" . 
		"\t\"http://www.w3.org/TR/REC-html40/loose.dtd");

if (! $q->param('v') &&
    defined $q->raw_cookie() &&
    $q->raw_cookie() =~ /[\s;,]*C=([^\s,;]+)/)
{
    &process_cookie($1);
}

# sanitize input to prevent people from trying to hack the site.
# remove anthing other than word chars, white space, or hyphens.
foreach $key ($q->param())
{
    $val = $q->param($key);
    $val =~ s/[^\w\s-]//g;
    $val =~ s/^\s*//g;		# nuke leading
    $val =~ s/\s*$//g;		# and trailing whitespace
    $q->param($key,$val);
}

# decide whether this is a results page or a blank form
&form('') unless $q->param('v');

&form("Please specify a year.")
    unless $q->param('year');

&form("Sorry, invalid year\n<b>" . $q->param('year') . "</b>.")
    if $q->param('year') !~ /^\d+$/;

if ($q->param('city'))
{
    &form("Sorry, invalid city\n<b>" . $q->param('city') . "</b>.")
	unless defined($city_tz{$q->param('city')});

    $q->param('geo','city');
    $q->param('tz',$city_tz{$q->param('city')});
    $q->delete('dst');

    $cmd .= " -C '" . $q->param('city') . "'";

    $city_descr = "Closest City: " . $q->param('city');
    $lat_descr  = '';
    $long_descr = '';
    $dst_tz_descr = '';
}
elsif (defined $q->param('lodeg') && defined $q->param('lomin') &&
       defined $q->param('lodir') &&
       defined $q->param('ladeg') && defined $q->param('lamin') &&
       defined $q->param('ladir'))
{
    &form("Sorry, all latitude/longitude\narguments must be numeric.")
	if (($q->param('lodeg') !~ /^\d*$/) ||
	    ($q->param('lomin') !~ /^\d*$/) ||
	    ($q->param('ladeg') !~ /^\d*$/) ||
	    ($q->param('lamin') !~ /^\d*$/));

    $q->param('lodir','w') unless ($q->param('lodir') eq 'e');
    $q->param('ladir','n') unless ($q->param('ladir') eq 's');

    $q->param('lodeg',0) if $q->param('lodeg') eq '';
    $q->param('lomin',0) if $q->param('lomin') eq '';
    $q->param('ladeg',0) if $q->param('ladeg') eq '';
    $q->param('lamin',0) if $q->param('lamin') eq '';

    &form("Sorry, longitude degrees\n" .
	  "<b>" . $q->param('lodeg') . "</b> out of valid range 0-180.")
	if ($q->param('lodeg') > 180);

    &form("Sorry, latitude degrees\n" .
	  "<b>" . $q->param('ladeg') . "</b> out of valid range 0-90.")
	if ($q->param('ladeg') > 90);

    &form("Sorry, longitude minutes\n" .
	  "<b>" . $q->param('lomin') . "</b> out of valid range 0-60.")
	if ($q->param('lomin') > 60);

    &form("Sorry, latitude minutes\n" .
	  "<b>" . $q->param('lamin') . "</b> out of valid range 0-60.")
	if ($q->param('lamin') > 60);

    ($long_deg,$long_min,$lat_deg,$lat_min) =
	($q->param('lodeg'),$q->param('lomin'),
	 $q->param('ladeg'),$q->param('lamin'));

    $q->param('dst','none')
	unless $q->param('dst');
    $q->param('tz','0')
	unless $q->param('tz');
    $q->param('geo','pos');

    $city_descr = "Geographic Position";
    $lat_descr  = "${lat_deg}d${lat_min}' " .
	uc($q->param('ladir')) . " latitude";
    $long_descr = "${long_deg}d${long_min}' " .
	uc($q->param('lodir')) . " longitude";
    $dst_tz_descr = "Daylight Savings Time: " .
	$q->param('dst') . "</small>\n<dd><small>Time zone: " .
	    $tz_names{$q->param('tz')};

    # don't multiply minutes by -1 since hebcal does it internally
    $long_deg *= -1  if ($q->param('lodir') eq 'e');
    $lat_deg  *= -1  if ($q->param('ladir') eq 's');

    $cmd .= " -L $long_deg,$long_min -l $lat_deg,$lat_min";
}
elsif ($q->param('zip'))
{
    $q->param('dst','usa')
	unless $q->param('dst');
    $q->param('tz','auto')
	unless $q->param('tz');
    $q->param('geo','zip');

    &form("Please specify a 5-digit\nzip code.")
	if $q->param('zip') eq '';

    &form("Sorry, <b>" . $q->param('zip') . "</b> does\n" .
	  "not appear to be a 5-digit zip code.")
	unless $q->param('zip') =~ /^\d\d\d\d\d$/;

    $dbmfile = 'zips.db';
    tie(%DB, 'DB_File', $dbmfile, O_RDONLY, 0444, $DB_File::DB_HASH)
	|| die "Can't tie $dbmfile: $!\n";

    $val = $DB{$q->param('zip')};
    untie(%DB);

    &form("Sorry, can't find\n".  "<b>" . $q->param('zip') . 
	  "</b> in the zip code database.\n",
          "<ul><li>Please try a nearby zip code or select candle\n" . 
	  "lighting times by\n" .
          "<a target=\"_top\"\nhref=\"" . $script_name .
	  "?c=on&amp;geo=city\">city</a> or\n" .
          "<a target=\"_top\"\nhref=\"" . $script_name .
	  "?c=on&amp;geo=pos\">latitude/longitude</a></li></ul>")
	unless defined $val;

    ($long_deg,$long_min,$lat_deg,$lat_min) = unpack('ncnc', $val);
    ($city,$state) = split(/\0/, substr($val,6));

    my(@city) = split(/([- ])/, $city);
    $city = '';
    foreach (@city)
    {
	$_ = lc($_);
	$_ = "\u$_";		# inital cap
	$city .= $_;
    }

    $city_descr = "$city, $state &nbsp;" . $q->param('zip');

    if ($q->param('tz') !~ /^-?\d+$/)
    {
	$ok = 0;
	if (defined $known_timezones{$q->param('zip')})
	{
	    if ($known_timezones{$q->param('zip')} ne '??')
	    {
		$q->param('tz',$known_timezones{$q->param('zip')});
		$ok = 1;
	    }
	}
	elsif (defined $known_timezones{substr($q->param('zip'),0,3)})
	{
	    if ($known_timezones{substr($q->param('zip'),0,3)} ne '??')
	    {
		$q->param('tz',$known_timezones{substr($q->param('zip'),0,3)});
		$ok = 1;
	    }
	}
	elsif (defined $known_timezones{$state})
	{
	    if ($known_timezones{$state} ne '??')
	    {
		$q->param('tz',$known_timezones{$state});
		$ok = 1;
	    }
	}

	if ($ok == 0)
	{
	    &form("Sorry, can't auto-detect\n" .
		  "timezone for <b>" . $city_descr . "</b>\n".
		  "(state <b>" . $state . "</b> spans multiple time zones).",
		  "<ul><li>Please select your time zone below.</li></ul>");
	}
    }

    $lat_descr  = "${lat_deg}d${lat_min}' N latitude";
    $long_descr = "${long_deg}d${long_min}' W longitude";
    $dst_tz_descr = "Daylight Savings Time: " .
	$q->param('dst') . "</small>\n<dd><small>Time zone: " .
	    $tz_names{$q->param('tz')};

    $cmd .= " -L $long_deg,$long_min -l $lat_deg,$lat_min";
}
else
{
    $q->delete('c');
    $q->delete('zip');
    $q->delete('city');
    $q->delete('geo');
}

foreach (@opts)
{
    $cmd .= ' -' . $_
	if defined $q->param($_) &&
	    ($q->param($_) eq 'on' || $q->param($_) eq '1');
}

$cmd .= " -m " . $q->param('m')
    if (defined $q->param('m') && $q->param('m') =~ /^\d+$/);

$cmd .= " -z " . $q->param('tz')
    if (defined $q->param('tz') && $q->param('tz') ne '');

$cmd .= " -Z " . $q->param('dst')
    if (defined $q->param('dst') && $q->param('dst') ne '');

$cmd .= " " . $q->param('month')
    if (defined $q->param('month') && $q->param('month') =~ /^\d+$/ &&
	$q->param('month') >= 1 && $q->param('month') <= 12);

$cmd .= " " . $q->param('year');


if (! defined $q->path_info())
{
    &results_page();
}
elsif ($q->path_info() =~ /.csv$/)
{
    &csv_display();
}
elsif ($q->path_info() =~ /.dba$/)
{
    &dba_display();
}
else
{
    &results_page();
}

close(STDOUT);
exit(0);

sub invoke_hebcal {
    local($cmd) = @_;
    local(*HEBCAL,@events,$prev,$loc,$_);

    @events = ();
    open(HEBCAL,"$cmd |") || die "Can't exec '$cmd': $!\n";

    $prev = '';
    $loc = (defined $city_descr && $city_descr ne '') ?
	"in $city_descr" : '';
    $loc =~ s/\s*&nbsp;\s*/ /g;

    while(<HEBCAL>)
    {
	next if $_ eq $prev;
	$prev = $_;
	chop;
	($date,$descr) = split(/ /, $_, 2);

	push(@events,
	     join("\cA", &parse_date_descr($date,$descr),$descr,$loc));
    }
    close(HEBCAL);

    @events;
}

sub dba_display {
    local(@events) = &invoke_hebcal($cmd);
    local($time) = defined $ENV{'SCRIPT_FILENAME'} ?
	(stat($ENV{'SCRIPT_FILENAME'}))[9] : time;

    print $q->header(-type =>
		     "application/x-palm-dba; filename=$PALM_DBA_FILENAME",
		     -last_modified => &http_date($time));

    &dba_contents(@events);
}

sub csv_display {
    local(@events) = &invoke_hebcal($cmd);
    local($time) = defined $ENV{'SCRIPT_FILENAME'} ?
	(stat($ENV{'SCRIPT_FILENAME'}))[9] : time;

    my($path_info) = $q->path_info();
    $path_info =~ s,^.*/,,;
    print $q->header(-type => 'text/x-csv; filename=' . $path_info,
		     -last_modified => &http_date($time));

    $endl = "\012";			# default Netscape and others
    if (defined $q->user_agent() && $q->user_agent() !~ /^\s*$/)
    {
	$endl = "\015\012"
	    if $q->user_agent() =~ /Microsoft Internet Explorer/;
	$endl = "\015\012" if $q->user_agent() =~ /MSP?IM?E/;
    }

    print STDOUT "\"Subject\",\"Start Date\",\"Start Time\",\"End Date\",",
    "\"End Time\",\"All day event\",\"Description\",",
    "\"Private\",\"Show time as\"$endl";

    foreach (@events)
    {
	($subj,$date,$start_time,$end_date,$end_time,$all_day,
	 $hour,$min,$mon,$mday,$year,$descr,$loc) = split(/\cA/);

	print STDOUT '"', $subj, '","', $date, '",', $start_time, ',',
	    $end_date, ',', $end_time, ',', $all_day, ',"',
	    ($start_time eq '' ? '' : $loc), '","true","3"', $endl;
    }

    1;
}

sub form
{
    local($message,$help) = @_;
    my($key,$val);

    print STDOUT $q->header(),
    $q->start_html(-title=>"Hebcal Interactive Jewish Calendar",
		   -head=>[
			   "<meta http-equiv=\"PICS-Label\" content='(PICS-1.1 \"http://www.rsac.org/ratingsv01.html\" l gen true by \"$author\" on \"1998.03.10T11:49-0800\" r (n 0 s 0 v 0 l 0))'>",
			   $q->Link({-rel=>'SCHEMA.dc',
				     -href=>'http://purl.org/metadata/dublin_core_elements'}),
			   $q->Link({-rev=>'made', -href=>"mailto:$author"}),
			   ],
		   -meta=>{
		       'description'=>
		       'Generates a list of Jewish holidays and candle lighting times customized to your zip code, city, or latitude/longitude',

		       'keywords' =>
		       'hebcal, Jewish calendar, Hebrew calendar, candle lighting, Shabbat, Havdalah, sedrot, Sadinoff',

		       'DC.Title' => 'Hebcal Interactive Jewish Calendar',
		       'DC.Creator.PersonalName' => 'Radwin, Michael',
		       'DC.Creator.PersonalName.Address' => $author,
		       'DC.Subject' => 'Jewish calendar, Hebrew calendar, hebcal',
		       'DC.Type' => 'Text.Form',
		       'DC.Identifier' => 'http://www.radwin.org/hebcal/',
		       'DC.Language' => 'en',
		       'DC.Date.X-MetadataLastModified' => '1999-12-24',
		       }),
    "<table border=\"0\" width=\"100%\" cellpadding=\"0\"\nclass=\"navbar\">",
    "<tr valign=\"top\"><td><small>",
    "<a target=\"_top\"\nhref=\"/\">radwin.org</a>\n<tt>-&gt;</tt>\n",
    "hebcal</small></td>",
    "<td align=\"right\"><small><a target=\"_top\"\n",
    "href=\"/search/\">Search</a></small>",
    "</td></tr></table>",
    "<h1>Hebcal\nInteractive Jewish Calendar</h1>";

    if ($message ne '')
    {
	$help = '' unless defined $help;
	$message = "<hr noshade size=\"1\"><p><font\ncolor=\"#ff0000\">" .
	    $message . "</font></p>" . $help . "<hr noshade size=\"1\">";
    }

    print STDOUT $message, "\n",
    "<form target=\"_top\" action=\"", $script_name, "\">\n",
    "Jewish Holidays for:&nbsp;&nbsp;&nbsp;\n",
    "<label for=\"year\">Year:\n",
    $q->textfield(-name=>'year',
		  -id=>'year',
		  -default=>$year,
		  -size=>4,
		  -maxlength=>4),
    "</label>\n",
    $q->hidden(-name=>'v',-value=>1,-override=>1),
    "\n&nbsp;&nbsp;&nbsp;\n",
    "<label for=\"month\">Month:\n",
    $q->popup_menu(-name=>'month',
		   -id=>'month',
		   -values=>['x',1..12],
		   -default=>'x',
		   -labels=>\%MoY_long),
    "</label>\n",
    $q->br(),
    $q->small("Use all digits to specify a year.\nYou probably aren't",
	      "interested in 93, but rather 1993.\n"),
    $q->br(), $q->br();

    if (!defined $q->param('c') || $q->param('c') eq 'off')
    {
	print STDOUT "(Candle lighting times are off.  Turn them on for:\n",
	$q->a({-href=>$script_name . "?c=on&amp;geo=zip",
	       -target=>'_top'},
	      "zip code"), ",\n",
	$q->a({-href=>$script_name . "?c=on&amp;geo=city",
	       -target=>'_top'},
	      "closest city"), ", or\n",
	$q->a({-href=>$script_name . "?c=on&amp;geo=pos",
	       -target=>'_top'},
	      "latitude/longitude"), ".)",
	$q->br(), $q->br();
    }
    else
    {
	print STDOUT $q->hidden(-name=>'c',-value=>'on'),
	"Include\ncandle lighting times for ";

	print STDOUT "zip code:\n"
	    if (! defined $q->param('geo') || $q->param('geo') eq 'zip');
	print STDOUT "closest city:\n"
	    if (defined $q->param('geo') && $q->param('geo') eq 'city');
	print STDOUT "latitude/longitude:\n"
	    if (defined $q->param('geo') && $q->param('geo') eq 'pos');

	print STDOUT $q->br(), "<small>",
	"(or ", $q->a({-href=>$script_name . "?c=off",
		       -target=>'_top'},
		      "turn them off"), ",\nor select by\n";
	
	if (defined $q->param('geo') && $q->param('geo') eq 'city')
	{
	    print STDOUT
		$q->a({-href=>$script_name . "?c=on&amp;geo=zip",
		       -target=>'_top'},
		      "zip code"), " or\n",
		$q->a({-href=>$script_name . "?c=on&amp;geo=pos",
		       -target=>'_top'},
		      "latitude/longitude");
	}
	elsif (defined $q->param('geo') && $q->param('geo') eq 'pos')
	{
	    print STDOUT
		$q->a({-href=>$script_name . "?c=on&amp;geo=zip",
		       -target=>'_top'},
		      "zip code"), " or\n",
		$q->a({-href=>$script_name . "?c=on&amp;geo=city",
		       -target=>'_top'},
		      "closest city");
	}
	else
	{
	    print STDOUT
		$q->a({-href=>$script_name . "?c=on&amp;geo=city",
		       -target=>'_top'},
		      "closest city"), " or\n",
		$q->a({-href=>$script_name . "?c=on&amp;geo=pos",
		       -target=>'_top'},
		      "latitude/longitude");
	}
	print STDOUT ")</small><br><blockquote>\n";
	
	if (defined $q->param('geo') && $q->param('geo') eq 'city')
	{
	    print STDOUT $q->hidden(-name=>'geo',-value=>'city'),
	    "<label for=\"city\">Closest City:\n",
	    $q->popup_menu(-name=>'city',
			   -id=>'city',
			   -values=>[sort keys %city_tz],
			   -default=>'Jerusalem'),
	    "</label>", $q->br(), "\n";
	}
	elsif (defined $q->param('geo') && $q->param('geo') eq 'pos')
	{
	    print STDOUT $q->hidden(-name=>'geo',-value=>'pos'),
	    "<label for=\"ladeg\">",
	    $q->textfield(-name=>'ladeg',
			  -id=>'ladeg',
			  -size=>3,
			  -maxlength=>2),
	    "&nbsp;deg</label>&nbsp;&nbsp;\n",
	    "<label for=\"lamin\">",
	    $q->textfield(-name=>'lamin',
			  -id=>'lamin',
			  -size=>2,
			  -maxlength=>2),
	    "&nbsp;min</label>&nbsp;\n",
	    $q->popup_menu(-name=>'ladir',
			   -id=>'ladir',
			   -values=>['n','s'],
			   -default=>'n',
			   -labels=>{'n'=>'North Latitude',
				     's'=>'South Latitude'}),
	    $q->br(),
	    "<label for=\"lodeg\">",
	    $q->textfield(-name=>'lodeg',
			  -id=>'lodeg',
			  -size=>3,
			  -maxlength=>3),
	    "&nbsp;deg</label>&nbsp;&nbsp;\n",
	    "<label for=\"lomin\">",
	    $q->textfield(-name=>'lomin',
			  -id=>'lomin',
			  -size=>2,
			  -maxlength=>2),
	    "&nbsp;min</label>&nbsp;\n",
	    $q->popup_menu(-name=>'lodir',
			   -id=>'lodir',
			   -values=>['w','e'],
			   -default=>'w',
			   -labels=>{'e'=>'East Longitude',
				     'w'=>'West Longitude'}),
	    $q->br();
	}
	else
	{
	    print STDOUT $q->hidden(-name=>'geo',-value=>'zip'),
	    "<label for=\"zip\">Zip code:\n",
	    $q->textfield(-name=>'zip',
			  -id=>'zip',
			  -size=>5,
			  -maxlength=>5),
	    "</label>&nbsp;&nbsp;&nbsp;\n";
	}

	if ($q->param('geo') ne 'city')
	{
	    print STDOUT "<label for=\"tz\">Time zone:\n",
	    $q->popup_menu(-name=>'tz',
			   -id=>'tz',
			   -values=>$q->param('geo') eq 'pos' ?
			   [-5,-6,-7,-8,-9,-10,-11,-12,
			    12,11,10,9,8,7,6,5,4,3,2,1,0,
			    -1,-2,-3,-4] : ['auto',-5,-6,-7,-8,-9,-10],
			   -default=>$q->param('geo') eq 'pos' ? 0 : 'auto',
			   -labels=>\%tz_names);

	    print STDOUT "</label>", $q->br(),
	    "Daylight Savings Time:\n",
	    $q->radio_group(-name=>'dst',
			    -id=>'dst',
			    -values=>$q->param('geo') eq 'pos' ?
			    ['usa','israel','none'] : ['usa','none'],
			    -default=>
			    $q->param('geo') eq 'pos' ? 'none' : 'usa',
			    -labels=>
			    {'usa' => "\nUSA (except AZ, HI, and IN) ",
			     'israel' => "\nIsrael ",
			     'none' => "\nnone ", }),
	     $q->br();
	}

	print STDOUT "<label for=\"m\">Havdalah minutes past sundown:\n",
	$q->textfield(-name=>'m',
		      -id=>'m',
		      -size=>3,
		      -maxlength=>3,
		      -default=>72),
	"</label>", $q->br(), "</blockquote>\n";
    }

    print STDOUT "<table border=\"0\"><tr>",
    "<td><label\nfor=\"a\">",
    $q->checkbox(-name=>'a',
		 -id=>'a',
		 -label=>'Use ashkenazis hebrew'),
    "</label></td>",
    "<td><label\nfor=\"o\">",
    $q->checkbox(-name=>'o',
		 -id=>'o',
		 -label=>'Add days of the Omer'),
    "</label></td>",
    "</tr><tr>",
    "<td><label\nfor=\"x\">",
    $q->checkbox(-name=>'x',
		 -id=>'x',
		 -label=>'Suppress Rosh Chodesh'),
    "</label></td>",
    "<td><label\nfor=\"h\">",
    $q->checkbox(-name=>'h',
		 -id=>'h',
		 -label=>'Suppress all default holidays'),
    "</label></td>",
    "</tr><tr>",
    "<td colspan=\"2\"><label\nfor=\"s\">",
    $q->checkbox(-name=>'s',
		 -id=>'s',
		 -label=>'Add weekly sedrot on Saturday'),
    "</label>\n(<label\nfor=\"i\">",
    $q->checkbox(-name=>'i',
		 -id=>'i',
		 -label=>'Use Israeli sedra scheme'),
    "</label>)</td>",
    "</tr><tr>",
    "<td colspan=\"2\"><label\nfor=\"d\">",
    $q->checkbox(-name=>'d',
		 -id=>'d',
		 -label=>'Print hebrew date for the entire date range'),
    "</label></td>",
    "</tr><tr>",
    "<td colspan=\"2\"><label\nfor=\"set\">",
    $q->checkbox(-name=>'set',
		 -id=>'set',
		 -checked=> 
		 (!defined $q->param('v') && defined $q->param('geo') &&
		  (!defined $q->raw_cookie() || $q->raw_cookie() =~ /^\s*$/))
		 ? 'checked' : undef,
		 -label=>'Save my preferences in a cookie'),
    "</label>(<a target=\"_top\"\n",
    "href=\"http://www.zdwebopedia.com/TERM/c/cookie.html\">What's\n",
    "a cookie?</a>)</td></tr></table>\n",
    $q->br(), $q->submit(-name=>'.s',-value=>'Get Calendar'),
    "</form>", $html_footer;

    exit(0);
    1;
}

sub results_page
{
    local($date);
    local($filename) = 'hebcal_' . $q->param('year');
    local($ycal) = (defined($q->param('y')) && $q->param('y') eq '1') ? 1 : 0;
    local($prev_url,$next_url,$prev_title,$next_title);

    if ($q->param('month') =~ /^\d+$/ &&
	$q->param('month') >= 1 && $q->param('month') <= 12)
    {
	$filename .= '_' . lc($MoY_short[$q->param('month')-1]);
	$date = $MoY_long{$q->param('month')} . ' ' . $q->param('year');
    }
    else
    {
	$date = $q->param('year');
    }

    if ($q->param('c'))
    {
	if (defined $q->param('zip'))
	{
	    $filename .= '_' . $q->param('zip');
	}
	elsif (defined $q->param('city'))
	{
	    $tmp = lc($q->param('city'));
	    $tmp =~ s/[^\w]/_/g;
	    $filename .= '_' . $tmp;
	}
    }

    $filename .= '.csv';

    # next and prev urls
    if ($q->param('month') =~ /^\d+$/ &&
	$q->param('month') >= 1 && $q->param('month') <= 12)
    {
	my($pm,$nm,$py,$ny);

	if ($q->param('month') == 1)
	{
	    $pm = 12;
	    $nm = 2;
	    $py = $q->param('year') - 1;
	    $ny = $q->param('year') - 1;
	}
	elsif ($q->param('month') == 12)
	{
	    $pm = 11;
	    $nm = 1;
	    $py = $q->param('year');
	    $ny = $q->param('year') + 1;
	}
	else
	{
	    $pm = $q->param('month') - 1;
	    $nm = $q->param('month') + 1;
	    $ny = $py = $q->param('year');
	}

	$prev_url = $script_name . "?year=" . $py . "&amp;month=" . $pm;
	foreach $key ($q->param())
	{
	    $val = $q->param($key);
	    $prev_url .= "&amp;$key=" . &url_escape($val)
		unless $key eq 'year' || $key eq 'month';
	}
	$prev_title = $MoY_long{$pm} . " " . $py;

	$next_url = $script_name . "?year=" . $ny . "&amp;month=" . $nm;
	foreach $key ($q->param())
	{
	    $val = $q->param($key);
	    $next_url .= "&amp;$key=" . &url_escape($val)
		unless $key eq 'year' || $key eq 'month';
	}
	$next_title = $MoY_long{$nm} . " " . $ny;
    }
    else
    {
	$prev_url = $script_name . "?year=" . ($q->param('year') - 1);
	foreach $key ($q->param())
	{
	    $val = $q->param($key);
	    $prev_url .= "&amp;$key=" . &url_escape($val)
		unless $key eq 'year';
	}
	$prev_title = ($q->param('year') - 1);

	$next_url = $script_name . "?year=" . ($q->param('year') + 1);
	foreach $key ($q->param())
	{
	    $val = $q->param($key);
	    $next_url .= "&amp;$key=" . &url_escape($val)
		unless $key eq 'year';
	}
	$next_title = ($q->param('year') + 1);
    }

    if ($q->param('set')) {
	$newcookie = &gen_cookie();
	if (! defined $q->raw_cookie() || $q->raw_cookie() ne $newcookie)
	{
	    print STDOUT "Set-Cookie: ", $newcookie, "; expires=",
	    $expires_date, "; path=/; domain=www.radwin.org\015\012";
	}
	$q->delete('set');
    }

    print STDOUT $q->header(-expires=>$expires_date),
    $q->start_html(-title=>"Hebcal: Jewish Calendar $date",
		   -head=>[
			   "<meta http-equiv=\"PICS-Label\" content='(PICS-1.1 \"http://www.rsac.org/ratingsv01.html\" l gen true by \"$author\" on \"1998.03.10T11:49-0800\" r (n 0 s 0 v 0 l 0))'>",
			   $q->Link({-rel=>'prev',
				 -href=>$prev_url,
				 -title=>$prev_title}),
			   $q->Link({-rel=>'next',
				 -href=>$next_url,
				 -title=>$next_title}),
			   $q->Link({-rel=>'start',
				 -href=>$script_name,
				 -title=>'Hebcal Interactive Jewish Calendar'})
			   ],
		   -meta=>{'robots'=>'noindex'});
    print STDOUT
	"<table border=\"0\" width=\"100%\" cellpadding=\"0\" ",
	"class=\"navbar\">\n",
	"<tr valign=\"top\"><td><small>\n",
	"<a target=\"_top\"\nhref=\"/\">radwin.org</a> <tt>-&gt;</tt>\n",
	"<a target=\"_top\"\nhref=\"", $script_name, "?v=0";

    foreach $key ($q->param())
    {
	$val = $q->param($key);
	print STDOUT "&amp;$key=", &url_escape($val)
	    unless $key eq 'v';
    }

    print STDOUT "\">hebcal</a>\n<tt>-&gt;</tt> $date</small>\n",
    "<td align=\"right\"><small><a target=\"_top\"\n",
    "href=\"/search/\">Search</a></small>\n",
    "</td></tr></table>\n",
    "<h1>Jewish Calendar $date</h1>\n";

    if ($q->param('c'))
    {
	print STDOUT "<dl>\n<dt>", $city_descr, "\n";
	print STDOUT "<dd><small>", $lat_descr, "</small>\n"
	    if $lat_descr ne '';
	print STDOUT "<dd><small>", $long_descr, "</small>\n"
	    if $long_descr ne '';
	print STDOUT "<dd><small>", $dst_tz_descr, "</small>\n"
	    if $dst_tz_descr ne '';
	print STDOUT "</dl>\n";
    }

    print STDOUT "Go to:\n",
    "<a target=\"_top\"\nhref=\"$prev_url\">", $prev_title, "</a> |\n",
    "<a target=\"_top\"\nhref=\"$next_url\">", $next_title, "</a><br>\n";

    print STDOUT "<p><a target=\"_top\"\nhref=\"", $script_name,
    "index.html/$filename?dl=1";
    foreach $key ($q->param())
    {
	$val = $q->param($key);
	print STDOUT "&amp;$key=", &url_escape($val);
    }
    print STDOUT "\">Download\nOutlook CSV file</a>";

    # only offer DBA export when we know timegm() will work
    if ($q->param('year') > 1969 && $q->param('year') < 2038 &&
	(!defined($q->param('dst')) || $q->param('dst') ne 'israel'))
    {
	print STDOUT " -\n<a target=\"_top\"\nhref=\"",
	$script_name, "index.html/$PALM_DBA_FILENAME?dl=1";
	foreach $key ($q->param())
	{
	    $val = $q->param($key);
	    print STDOUT "&amp;$key=", &url_escape($val);
	}
	print STDOUT "\">Download\nPalm Date Book Archive (.DBA)</a>";
    }

    if ($ycal == 0)
    {
	print STDOUT " -\n<a target=\"_top\"\nhref=\"", 
	$script_name, "?y=1";
	foreach $key ($q->param())
	{
	    $val = $q->param($key);
	    print STDOUT "&amp;$key=", &url_escape($val);
	}
	print STDOUT "\">Show\nYahoo! Calendar links</a>";
    }
    print STDOUT "</p>\n";

    print STDOUT 
"<div><small>
<p>Your personal <a target=\"_top\" href=\"http://calendar.yahoo.com/\">Yahoo!
Calendar</a> is a free web-based calendar that can synchronize with Palm
Pilot, Outlook, etc.</p>
<ul>
<li>If you wish to upload <strong>all</strong> of the below holidays to
your Yahoo!  Calendar, do the following:
<ol>
<li>Click the \"Download as an Outlook CSV file\" link above.
<li>Save the hebcal CSV file on your computer.
<li>Go to <a target=\"_top\"
href=\"http://calendar.yahoo.com/?v=81\">Import/Export page</a> of
Yahoo! Calendar.
<li>Find the \"Import from Outlook\" section and choose \"Import Now\"
to import your CSV file to your online calendar.
</ol>
<li>To import selected holidays <strong>one at a time</strong>, use
the \"add\" links below.  These links will pop up a new browser window
so you can keep this window open.
</ul></small></div>
" if $ycal;

    my($cmd_pretty) = $cmd;
    $cmd_pretty =~ s,.*/,,; # basename
    print STDOUT "<!-- $cmd_pretty -->\n";

    local(@events) = &invoke_hebcal($cmd);
    print STDOUT "<pre>";

    foreach (@events)
    {
	($subj,$date,$start_time,$end_date,$end_time,$all_day,
	 $hour,$min,$mon,$mday,$year,$descr,$loc) = split(/\cA/);

	if ($ycal)
	{
	    $ST  = sprintf("%04d%02d%02d", $year, $mon, $mday);
	    if ($hour >= 0 && $min >= 0)
	    {
		$loc = (defined $city_descr && $city_descr ne '') ?
		    "in $city_descr" : '';
	        $loc =~ s/\s*&nbsp;\s*/ /g;

		$hour += 12 if $hour < 12 && $hour > 0;
		$ST .= sprintf("T%02d%02d00", $hour, $min);

		if ($q->param('tz') ne '')
		{
		    $abstz = ($q->param('tz') >= 0) ?
			$q->param('tz') : -$q->param('tz');
		    $signtz = ($q->param('tz') < 0) ? '-' : '';

		    $ST .= sprintf("Z%s%02d00", $signtz, $abstz);
		}

		$ST .= "&amp;DESC=" . &url_escape($loc)
		    if $loc ne '';
	    }

	    print STDOUT
		"<a target=\"_calendar\" href=\"http://calendar.yahoo.com/";
	    print STDOUT "?v=60&amp;TYPE=16&amp;ST=$ST&amp;TITLE=",
		&url_escape($subj), "&amp;VIEW=d\">add</a> ";
	}

	$descr =~ s/&/&amp;/g;
	$descr =~ s/</&lt;/g;
	$descr =~ s/>/&gt;/g;

	if ($descr =~ /^(Parshas\s+|Parashat\s+)(.+)/)
	{
	    $parashat = $1;
	    $sedra = $2;
	    if (defined $sedrot{$sedra} && $sedrot{$sedra} !~ /^\s*$/)
	    {
		$descr = '<a target="_top" href="' . $sedrot{$sedra} .
		    '">' . $parashat . $sedra . '</a>';
	    }
	    elsif (($sedra =~ /^([^-]+)-(.+)$/) &&
		   (defined $sedrot{$1} && $sedrot{$1} !~ /^\s*$/))
	    {
		$descr = '<a target="_top" href="' . $sedrot{$1} .
		    '">' . $parashat . $sedra . '</a>';
	    }
	}

	$dow = ($year > 1969 && $year < 2038) ?
	    $DoW[&get_dow($year - 1900, $mon - 1, $mday)] . ' ' : '';
	printf STDOUT "%s%04d-%02d-%02d  %s\n",
	$dow, $year, $mon, $mday, $descr;
    }

    print STDOUT "</pre>", "Go to:\n",
    "<a target=\"_top\"\nhref=\"$prev_url\">", $prev_title, 
    "</a> |\n",
    "<a target=\"_top\"\nhref=\"$next_url\">", $next_title, "</a><br>\n";

    print STDOUT  $html_footer;

    1;
}

sub get_dow
{
    local($year,$mon,$mday) = @_;
    local($time) = &Time::Local::timegm(0,0,9,$mday,$mon,$year,0,0,0); # 9am

    (localtime($time))[6];	# $wday
}

sub parse_date_descr
{
    local($date,$descr) = @_;

    local($mon,$mday,$year) = split(/\//, $date);
    if ($descr =~ /^(.+)\s*:\s*(\d+):(\d+)\s*$/)
    {
	($subj,$hour,$min) = ($1,$2,$3);
	$start_time = sprintf("\"%d:%02d PM\"", $hour, $min);
#	$min += 15;
#	if ($min >= 60)
#	{
#	    $hour++;
#	    $min -= 60;
#	}
#	$end_time = sprintf("\"%d:%02d PM\"", $hour, $min);
#	$end_date = $date;
	$end_time = $end_date = '';
	$all_day = '"false"';
    }
    else
    {
	$hour = $min = -1;
	$start_time = $end_time = $end_date = '';
	$all_day = '"true"';
	$subj = $descr;
    }
    
    $subj =~ s/\"/''/g;
    $subj =~ s/\s*:\s*$//g;

    ($subj,$date,$start_time,$end_date,$end_time,$all_day,
     $hour,$min,$mon,$mday,$year);
}

sub url_escape
{
    local($_) = @_;
    local($res) = '';

    foreach (split(//))
    {
	if (/ /)
	{
	    $res .= '+';
	}
	elsif (/[^a-zA-Z0-9_.-]/)
	{
	    $res .= sprintf("%%%02X", ord($_));
	}
	else
	{
	    $res .= $_;
	}
    }

    $res;
}

sub http_date
{
    local($time) = @_;
    local($sec,$min,$hour,$mday,$mon,$year,$wday) =
	gmtime($time);

    sprintf("%s, %02d %s %4d %02d:%02d:%02d GMT",
	    $DoW[$wday],$mday,$MoY_short[$mon],$year+1900,$hour,$min,$sec);
}

sub gen_cookie {
    local($retval);

    $retval = 'C=t=' . time;

    if ($q->param('c')) {
	if ($q->param('geo') eq 'zip') {
	    $retval .= '&zip=' . $q->param('zip');
	    $retval .= '&dst=' . $q->param('dst')
	        if defined $q->param('dst') && $q->param('dst') ne '';
	    $retval .= '&tz=' . $q->param('tz')
	        if defined $q->param('tz') && $q->param('tz') ne '';
	} elsif ($q->param('geo') eq 'city') {
	    $retval .= '&city=' . &url_escape($q->param('city'));
	} elsif ($q->param('geo') eq 'pos') {
	    $retval .= '&lodeg=' . $q->param('lodeg');
	    $retval .= '&lomin=' . $q->param('lomin');
	    $retval .= '&lodir=' . $q->param('lodir');
	    $retval .= '&ladeg=' . $q->param('ladeg');
	    $retval .= '&lamin=' . $q->param('lamin');
	    $retval .= '&ladir=' . $q->param('ladir');
	    $retval .= '&dst=' . $q->param('dst')
	        if defined $q->param('dst') && $q->param('dst') ne '';
	    $retval .= '&tz=' . $q->param('tz')
	        if defined $q->param('tz') && $q->param('tz') ne '';
	}
	$retval .= '&m=' . $q->param('m')
	    if defined $q->param('m') && $q->param('m') ne '';
    }

    foreach (@opts)
    {
	next if $_ eq 'c';
	$retval .= "&$_=" . $q->param($_)
	    if defined $q->param($_) && $q->param($_) ne '';
    }

    $retval;
}


sub process_cookie {
    local($cookieval) = @_;

    my($c) = new CGI($cookieval);
    
    if ((! defined $q->param('c')) ||
	($q->param('c') eq 'on') ||
	($q->param('c') eq '1')) {
	if (defined $c->param('zip') && $c->param('zip') =~ /^\d{5}$/ &&
	    (! defined $q->param('geo') || $q->param('geo') eq 'zip')) {
	    $q->param('zip',$c->param('zip'));
	    $q->param('geo','zip');
	    $q->param('c','on');
	    $q->param('dst',$c->param('dst'))
		if (defined $c->param('dst') && ! defined $q->param('dst'));
	    $q->param('tz',$c->param('tz'))
		if (defined $c->param('tz') && ! defined $q->param('tz'));
	} elsif (defined $c->param('city') && $c->param('city') ne '' &&
		 (! defined $q->param('geo') || $q->param('geo') eq 'city')) {
	    $q->param('city',$c->param('city'));
	    $q->param('geo','city');
	    $q->param('c','on');
	} elsif (defined $c->param('lodeg') &&
		 defined $c->param('lomin') &&
		 defined $c->param('lodir') &&
		 defined $c->param('ladeg') &&
		 defined $c->param('lamin') &&
		 defined $c->param('ladir') &&
		 (! defined $q->param('geo') || $q->param('geo') eq 'pos')) {
	    $q->param('lodeg',$c->param('lodeg'));
	    $q->param('lomin',$c->param('lomin'));
	    $q->param('lodir',$c->param('lodir'));
	    $q->param('ladeg',$c->param('ladeg'));
	    $q->param('lamin',$c->param('lamin'));
	    $q->param('ladir',$c->param('ladir'));
	    $q->param('geo','pos');
	    $q->param('c','on');
	    $q->param('dst',$c->param('dst'))
		if (defined $c->param('dst') && ! defined $q->param('dst'));
	    $q->param('tz',$c->param('tz'))
		if (defined $c->param('tz') && ! defined $q->param('tz'));
	}
    }

    $q->param('m',$c->param('m'))
	if (defined $c->param('m') && ! defined $q->param('m'));
    
    foreach (@opts)
    {
	next if $_ eq 'c';
	$q->param($_,$c->param($_))
	    if (! defined $q->param($_) && defined $c->param($_));
    }

    1;
}

########################################################################
# export to Palm Date Book Archive (.DBA)
########################################################################

sub writeInt {
    print STDOUT pack("V", $_[0]);
}

sub writeByte {
    print STDOUT pack("C", $_[0]);
}

sub writePString {
    local($len) = length($_[0]);

    if ($len > 64) { $len = 64; }
    &writeByte($len);
    print STDOUT substr($_[0], 0, 64);
}

sub dba_header {
    &writeInt($PALM_DBA_MAGIC);
    &writePString($PALM_DBA_FILENAME);
    &writeByte(0);
    &writeInt(8);
    &writeInt(0);

    # magic OLE graph table stuff
    &writeInt(0x36);
    &writeInt(0x0f);
    &writeInt(0x00);
    &writeInt(0x01);
    &writeInt(0x02);
    &writeInt(0x1000f);
    &writeInt(0x10001);
    &writeInt(0x10003);
    &writeInt(0x10005);
    &writeInt(0x60005);
    &writeInt(0x10006);
    &writeInt(0x10006);
    &writeInt(0x80001);
    # end OLE stuff

    1;
}

sub dba_contents {
    local(@events) = @_;
    local($numEntries) = scalar(@events);
    local($memo,$untimed,$startTime,$i,$z,$secsEast,$local2local);
    
    # compute diff seconds between GMT and whatever our local TZ is
    # pick 1999/01/15 as a date that we're certain is standard time
    $startTime = &Time::Local::timegm(0,34,12,15,0,90,0,0,0);
    $secsEast = $startTime - &Time::Local::timelocal(0,34,12,15,0,90,0,0,0);
    if ($q->param('tz') =~ /^-?\d+$/)
    {
	# add secsEast to go from our localtime to GMT
	# then sub destination tz secsEast to get into local time
	$local2local = $secsEast - ($q->param('tz') * 60 * 60);
    }
    else
    {
	# the best we can do with unknown TZ is assume GMT
	$local2local = $secsEast;
    }

    &dba_header();

    $numEntries = $PALM_DBA_MAXENTRIES if ($numEntries > $PALM_DBA_MAXENTRIES);
    &writeInt($numEntries*15);

    for ($i = 0; $i < $numEntries; $i++) {
	local($subj,$z,$z,$z,$z,$all_day,
	      $hour,$min,$mon,$mday,$year) = split(/\cA/, $events[$i]);

        next if $year <= 1969 || $year >= 2038;

	if ($hour == -1 && $min == -1) {
	    $hour = $min = 0;
	} elsif ($hour > 0 || $min > 0) {
	    $hour += 12;	# candle-lighting times are always PM
	}

	if (!defined($q->param('dst')) || $q->param('dst') eq 'none' ||
	    ((defined $q->param('geo') && $q->param('geo') eq 'city' &&
	      defined $q->param('city') && $q->param('city') ne '' &&
	      defined $city_nodst{$q->param('city')})))
	{
	    # no DST, so just use gmtime and then add that city offset
	    $startTime = &Time::Local::timegm(0,$min,$hour,$mday,$mon-1,
					      $year-1900,0,0,0);
	    $startTime -= ($q->param('tz') * 60 * 60); # move into local tz
	}
	else
	{
	    $startTime = &Time::Local::timelocal(0,$min,$hour,$mday,$mon-1,
						 $year-1900,0,0,0);
	    $startTime += $local2local; # move into their local tz
	}

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(0);		# recordID

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(1);		# status

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(2147483647);	# position

	&writeInt($PALM_DBA_DATE);
	&writeInt($startTime);

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(0);		# endTime

	&writeInt(5);		# spacer
	&writeInt(0);		# spacer

	if ($subj eq '') {
	    &writeByte(0);
	} else {
	    &writePString($subj);
	}

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(0);		# duration

	&writeInt(5);		# spacer
	&writeInt(0);		# spacer

	$memo = '';
	if ($memo eq '') {
	    &writeByte(0);
	} else {
	    &writePString($memo);
	}

	$untimed = ($all_day eq '"true"');

	&writeInt($PALM_DBA_BOOL);
	&writeInt($untimed);

	&writeInt($PALM_DBA_BOOL);
	&writeInt(1);		# isPrivate

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(1);		# category

	&writeInt($PALM_DBA_BOOL);
	&writeInt(0);		# alarm

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(0xFFFFFFFF);	# alarmAdv

	&writeInt($PALM_DBA_INTEGER);
	&writeInt(0);		# alarmTyp

	&writeInt($PALM_DBA_REPEAT);
	&writeInt(0);		# repeat
    }

    1;
}
