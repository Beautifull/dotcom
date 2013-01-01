########################################################################
# Copyright (c) 2013 Michael J. Radwin.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#  * Redistributions of source code must retain the above
#    copyright notice, this list of conditions and the following
#    disclaimer.
#
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials
#    provided with the distribution.
#
#  * Neither the name of Hebcal.com nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
########################################################################

package HebcalHtml;

use strict;

use CGI qw(-no_xhtml);

$HebcalHtml::gregorian_warning = qq{<div class="alert alert-block">
<button type="button" class="close" data-dismiss="alert">&times;</button>
<strong>Warning!</strong>
Results for year 1752 C.E. and earlier may be inaccurate.
<p>Hebcal does not take into account a correction of ten days that
was introduced by Pope Gregory XIII known as the Gregorian
Reformation.<sup><a
href="http://en.wikipedia.org/wiki/Gregorian_calendar#Adoption_in_Europe">[1]</a></sup></p>
</div><!-- .alert -->
};

$HebcalHtml::indiana_warning = qq{<div class="alert alert-block">
<button type="button" class="close" data-dismiss="alert">&times;</button>
<strong>Warning!</strong>
Indiana has confusing time zone &amp; Daylight Saving Time
rules.</span><br>Please check <a
href="http://www.mccsc.edu/time.html#WHAT">What time is it in
Indiana?</a> to make sure the above settings are correct.
</div><!-- .alert -->
};

$HebcalHtml::usno_warning =  qq{<div class="alert alert-block">
<button type="button" class="close" data-dismiss="alert">&times;</button>
<strong>Warning!</strong>
Candle-lighting times are guaranteed to be wrong at extreme
northern or southern latitudes.</span><br>Please consult your
local halachic authority for correct candle-lighting times.
</div><!-- .alert -->
};

sub accordion_bootstrap {
    my($title,$anchor,$inner) = @_;
    my $s = <<EOHTML;
<div class="accordion-group">
 <div class="accordion-heading">
  <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#${anchor}-body">$title</a>
 </div>
 <div id="${anchor}-body" class="accordion-body collapse">
  <div class="accordion-inner">
   $inner
  </div>
 </div><!-- #${anchor}-body -->
</div>
EOHTML
;
    return $s;
}

sub download_html_bootstrap {
    my($q,$filename,$events,$title) = @_;

    my($greg_year1,$greg_year2) = (0,0);
    my($numEntries) = scalar(@{$events});
    if ($numEntries > 0) {
	$greg_year1 = $events->[0]->[$Hebcal::EVT_IDX_YEAR];
	$greg_year2 = $events->[$numEntries - 1]->[$Hebcal::EVT_IDX_YEAR];
    }

    my $ical1 = Hebcal::download_href($q, $filename, "ics");
    $ical1 =~ /\?(.+)$/;
    my $args = $1;
    my $ical_href = Hebcal::get_vcalendar_cache_fn($args) . "?" . $args;
    my $subical_href = $ical_href;
    $subical_href =~ s/\?dl=1/\?subscribe=1/g;
    my $vhost = $q->virtual_host();
    my $href_ol_usa = Hebcal::download_href($q, "${filename}_usa", "csv");
    my $href_ol_eur = Hebcal::download_href($q, "${filename}_eur", "csv") . ";euro=1";
    my $href_vcs = Hebcal::download_href($q, $filename, "vcs");
    my $title_esc = $title ? Hebcal::url_escape("Hebcal $title")
	: Hebcal::url_escape("Hebcal $filename");
    my $ics_title = $title ? "Jewish Calendar $title.ics" : "$filename.ics";
 

    my $ol_ics_title = "Outlook 2007, Outlook 2010 (Windows)";
    my $ol_csv_title = "Outlook 97, 98, 2000, 2002, 2003 (Windows)";
    my $ical_title = "Apple iCal (Mac OS X)";
    my $ol_mac_title = "Outlook 2011 (Mac OS X)";
    my $ios_title = "iPhone &amp; iPad (iOS 3.0 and higher)";
    my $gcal_title = "Google Calendar";
    my $wlive_title = "Windows Live Calendar";
    my $ycal_title = "Yahoo! Calendar";
    my $palm_title = "Palm Desktop (Windows-only)";

    my $ol_ics = <<EOHTML;
<ol>
<li>Internet Calendar Subscription: <a class="download"
href="webcal://$vhost$subical_href"
id="dl-ol-ics">$ics_title</a>
<li><a title="Outlook Internet Calendar Subscription - import Hebcal Jewish calendar to Outlook 2007, Outlook 2010"
href="/home/8/outlook-internet-calendar-subscription-jewish-calendar">How to import ICS file into Outlook</a>
</ol>
EOHTML
;
    my $ol_csv = <<EOHTML;
<ol>
<li>Export Outlook CSV file. Select one of:
<ul>
<li>USA date format (month/day/year): <a class="download"
href="$href_ol_usa"
id="dl-ol-csv-usa">${filename}_usa.csv</a>
<li>European date format (day/month/year): <a class="download"
href="$href_ol_eur"
id="dl-ol-csv-eur">${filename}_eur.csv</a>
</ul>
<li><a title="Outlook CSV - import Hebcal Jewish calendar to Outlook 97, 98, 2000, 2002, 2003"
href="/home/12/outlook-csv-jewish-calendar">How to import CSV file into Outlook</a>
</ol>
EOHTML
;
    my $ical = <<EOHTML;
<ol>
<li>Subscribe to: <a class="download"
href="webcal://$vhost$subical_href"
id="dl-ical-sub">$ics_title</a>
<li><a title="Apple iCal - import Hebcal Jewish calendar"
href="/home/79/apple-ical-import-hebcal-jewish-calendar">How to import ICS file into Apple iCal</a>
</ol>
Alternate option: <a class="download"
href="${ical_href}"
id="dl-ical-alt">download $ics_title</a>
and then import manually into Apple iCal.
EOHTML
;
    my $ol_mac = <<EOHTML;
<ol>
<li>Download <a class="download"
href="${ical_href}"
id="dl-ol-mac">$ics_title</a>
<li><a title="Outlook 2011 Mac OS X - import Hebcal Jewish calendar"
href="/home/186/outlook-2011-mac-import">How to import .ics file into Outlook 2011 for Mac OS X</a>
</ol><!-- #ol-mac-body -->
EOHTML
;
    my $ios = <<EOHTML;
<ol>
<li>Subscribe to: <a class="download"
href="webcal://$vhost$subical_href"
id="dl-ios-sub">$ics_title</a>
<li><a title="iPhone and iPad - import Hebcal Jewish calendar"
href="/home/77/iphone-ipad-jewish-calendar">Step-by-step import instructions</a>
</ol>
EOHTML
;

    #############################################################
    # Google Calendar

    my $gcal_subical_href = $subical_href;
    $gcal_subical_href =~ s/;/&/g;
    my $full_http_href = "http://" . $vhost . $gcal_subical_href;
    my $gcal_href = Hebcal::url_escape($full_http_href);
    my $gcal = <<EOHTML;
<p><a title="Add to Google Calendar"
class="download" id="dl-gcal-sub"
href="http://www.google.com/calendar/render?cid=${gcal_href}"><img
src="/i/gc_button6.gif" width="114" height="36" style="border:none" alt="Add to Google Calendar"></a></p>
<p>Alternate option:
<a class="download" id="dl-gcal-alt"
href="${ical_href}">download</a> and then <a
title="Google Calendar alternative instructions - import Hebcal Jewish calendar"
href="/home/59/google-calendar-alternative-instructions">follow
our Google Calendar import instructions</a>.</p>
EOHTML
;

    #############################################################
    # Windows Live Calendar

    my $wlive = <<EOHTML;
<p>Add to&nbsp;&nbsp;
<a title="Windows Live Calendar" class="dl-wlive"
href="http://calendar.live.com/calendar/calendar.aspx?rru=addsubscription&amp;url=${gcal_href}&amp;name=${title_esc}"><img
src="/i/wlive-150x20.png"
width="150" height="20" style="border:none"
alt="Windows Live Calendar"></a></p>
EOHTML
;

    ############################################################
    # Yahoo! Calendar

    my $ampersand_subical_href = $subical_href;
    $ampersand_subical_href =~ s/;/&amp;/g;
    my $ampersand_http_href = "http://" . $vhost . $ampersand_subical_href;
    my $ycal = <<EOHTML;
<form id="GrabLinkForm" action="#">
<ol>
<li>Copy the entire iCal URL here:
<label for="iCalUrl"><small><input type="text" size="80" id="iCalUrl" name="iCalUrl"
onfocus="this.select();" onKeyPress="return false;"
value="${ampersand_http_href}"></small></label>
<li>Go to your <a href="http://calendar.yahoo.com/">Yahoo! Calendar</a>,
and click the "<b>+</b>" button next to "Calendars" on the left side of the page
<li>Click <b>Subscribe to Calendar</b>
<li>Paste the web address into the "Email or iCal address" window
<li>Click <b>Next</b> at the top of the page
<li>Type a name for the calendar in the window after "Display as."
<li>Choose a color for the calendar in the "Color:" pull-down menu
<li>Click <b>Save</b> at the top of the page
</ol>
</form>
EOHTML
;

    #############################################################
    # Palm

    # only offer DBA export when we know timegm() will work
    my $palm_dba = "";
    my $dst;
    if ($q->param("geo") && $q->param("geo") ne "off"
	&& $q->param("c") && $q->param("c") ne "off") {
	if (defined $q->param("dst") && $q->param("dst") ne "") {
	    $dst = $q->param("dst");
	}
	elsif ($q->param("geo") eq "city" && $q->param("city")
	       && defined $Hebcal::city_dst{$q->param("city")}) {
	    $dst = $Hebcal::city_dst{$q->param("city")};
	}
    }

    if ($greg_year1 > 1969 && $greg_year2 < 2038 &&
	(!defined($dst) || $dst eq "usa" || $dst eq "none")) {
	my $dba_href = Hebcal::download_href($q, $filename, 'dba');
	$palm_dba = <<EOHTML;
<li>Palm Desktop 4.1.4 - Date Book Archive
<ol>
<li>Export <a class="download" id="dl-dba" href="$dba_href">$filename.dba</a>
<li><a title="Palm Desktop - import Hebcal Jewish calendar"
href="/home/87/palm-desktop-import-hebcal-jewish-calendar">How to import DBA file into Palm Desktop 4.1.4</a>
</ol>
EOHTML
;
    }

    my $palm = <<EOHTML;
<ul>
<li>Palm Desktop 6.2 by ACCESS - vCal (.vcs format)
<ol>
<li>Export <a class="download" id="dl-vcs" href="$href_vcs">${filename}.vcs</a>
<li><a title="Palm Desktop 6.2 - import Hebcal Jewish calendar"
href="/home/188/palm-desktop-62">Import VCS file into Palm Desktop 6.2 for Windows</a>
</ol>
$palm_dba
</ul>
EOHTML
;


    my $s = qq{<div class="accordion" id="accordion2">\n};
    $s .= accordion_bootstrap($ol_ics_title, "ol-ics", $ol_ics);
    $s .= accordion_bootstrap($ol_csv_title, "ol-csv", $ol_csv);
    $s .= accordion_bootstrap($ical_title, "ical", $ical);
    $s .= accordion_bootstrap($ol_mac_title, "ol-mac", $ol_mac);
    $s .= accordion_bootstrap($ios_title, "ios", $ios);
    $s .= accordion_bootstrap($gcal_title, "gcal", $gcal);
    $s .= accordion_bootstrap($wlive_title, "wlive", $wlive);
    $s .= accordion_bootstrap($ycal_title, "ycal", $ycal);
    $s .= accordion_bootstrap($palm_title, "palm", $palm);
    $s .= qq{</div><!-- #accordion2 -->\n};

    return $s;
}

sub download_html_modal {
    my($q,$filename,$events,$title) = @_;

    my $html = download_html_bootstrap($q,$filename,$events,$title);
    my $s = <<EOHTML;
<div id="hcdl-modal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="hcdl-modalLabel" aria-hidden="true">
 <div class="modal-header">
  <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
  <h3 id="hcdl-modalLabel">Download calendar</h3>
 </div>
 <div class="modal-body">
$html
 </div>
 <div class="modal-footer">
   <button class="btn btn-primary" data-dismiss="modal" aria-hidden="true">Close</button>
 </div>
</div>
EOHTML
;
    return $s;
}

sub download_html_modal_button {
    return qq{<a href="#hcdl-modal" role="button" class="btn" data-toggle="modal"><i class="icon-download-alt"></i> Download ...</a>};
}

1;