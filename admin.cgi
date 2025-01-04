#! /usr/bin/perl

# ================================================================== #
#  Fumy Teacher's Schedule Board   Ver 2.3.0   [admin.cgi]           #
# ================================================================== #
#  Copyright (C) Fumihiro Nishimura.(Nishishi) 2004-2016.            #
#                                                                    #
#  �X�P�W���[���\���t���[CGI�ł��B(���̃t�@�C���͊Ǘ��E�ҏW�pCGI)    #
#  ���쌠�́A�������G(�ɂ���)�ɂ���܂��B                            #
#  ����CGI�͒N�ł����R�ɂ��g�p�����܂��B���p�E�񏤗p��₢�܂���B   #
#  ���쌠�\�����폜�E���ς����ɂ��g�p�������B                        #
#                                                                    #
#  http://www.nishishi.com/                                          #
# ================================================================== #
#  �p�X���[�h�i�[�t�@�C���́A�ŏ��͒��g������ۂ̏�ԂŃA�b�v���[�h  #
#  ���ĉ������B����ƁA����CGI�ɃA�N�Z�X�����Ƃ��ɁA�p�X���[�h�쐬   #
#  ��ʂ��o�܂��B�p�X���[�h��Y��Ă��܂����ꍇ���A�p�X���[�h�i�[�t  #
#  �@�C���̒��g���폜���ăA�b�v���[�h���邱�ƂŁA���Z�b�g�ł��܂��B  #
#  ���p�X���[�h���u�Œ�v�ɐݒ肵���ꍇ�́A�p�X���[�h�i�[�t�@�C����  #
#  �g���܂���B                                                      #
# ================================================================== #

# ================ #
#  �����[�U�ݒ聥  #
# ================ #

# �p�X���[�h�w���ʁi 0: �Œ� �^ 1: �ύX�\ �j
$passwordtype = 1;

# �p�X���[�h�i�Œ�̏ꍇ�j
$password = "0000";

# �p�X���[�h�i�[�t�@�C�����i�ύX�\�ȏꍇ�j�@Web����A�N�Z�X�ł��Ȃ��f�B���N�g���ɒu���̂����S�ł��B
$pwfile = "upf.cgi";

# 1�T�Ԃ̔ėp�\��\�i�[�t�@�C����
$weeklyfile = "weekly.txt";

# �J�����_�[�\��\�i�[�t�@�C����
$calendarfile = "calendar.txt";

# �����\��i�[�t�@�C����
$longfile = "long.txt";

# �\��\�p ��^�\��t�@�C����
$scheduleseals = "seals.txt";

# �X�P�W���[���\��CGI���i�f�t�H���g�� schedule.cgi �j
$schedulecgi = "schedule.cgi";

# ����CGI�̃t�@�C����
$thiscgi = "admin.cgi";

# CSS(�X�^�C���V�[�g)�t�@�C����
$cssfile = "admin.css";

# �Í����L�[�i�C�ӂ�2�����^���ύX����K�v�͂���܂���B�ύX��������΂��Ă��\���܂���B�j
$cryptkey = "fx";

# ======================== #
#  �����[�U�ݒ肱���܂Ł�  # ���������牺������������K�v�͂���܂���B
# ======================== #
my $demomode = 0;

use Time::Local;

# �J�����_�[�\���p�p�b�P�[�W���Ă�
require 'calendar.pl';

# �ϐ�������
$mode = "";		# ���샂�[�h
$upw  = "";		# ���[�U�p�X���[�h
$encupw = "";	# �G���R�[�h��̃��[�U�p�X���[�h
$loginmsg = "�p�X���[�h����͂��ĉ������B";	# ���O�C����ʃ��b�Z�[�W

$wscaption=""; @wsrow0=(); @wsrow1=(); @wsrow2=(); @wsrow3=(); @wsrow4=(); @wsrow5=(); @wsrow6=(); @wsrow7=();	# 1�T�Ԃ̔ėp�\��\�p

my $voidtags = $calendarpackage::voidtags;	# HTML�^�O�̖������ݒ�(calendar.pl�̒l���g�p)

# DEMO
my $demomsg = "";
if( $demomode == 1 ) {
	$demomsg = qq|<p style="background-color: #ffeeee; border: 1px solid #ffdddd; border-radius: 1em; padding: 1em; margin: 0px; color:#cc0000;font-size:80%;"><span style="background-color:#cc0000;color:#fffff0; font-weight:bold;">������T���v����</span><br>�������R�ɂ����������܂��B�p�X���[�h�� <strong style="font-family:monospace;">guest</strong> �ł��B<br>��HTML�^�O�̓��͖͂����ɐݒ肳��Ă��܂����A���ۂɉ^�c����ۂɂ͂ǂ��HTML�^�O�����p�\\\�ł��B�i�����ɐݒ肷�邱�Ƃ��ł��܂��j</p>|;
}

# ����HTML�̃��[�h
@datahtml = <DATA>;

@seals;



# ���C�������J�n
print "Content-type: text/html\n\n";

# �p�����[�^����
&splitparam();

# �p�X���[�h�`�F�b�N
$pwcheckresult = &checkpassword($upw,$encupw);
if( ($mode ne "") && ($mode ne $dochangepw) && ($pwcheckresult == 0) ) {
	# ���[�h���u���O�C���v�łȂ��A�u�p�X���[�h�ύX���s�v�ł��Ȃ��A
	# �p�X���[�h���Ⴄ�ꍇ�̓��O�C����ʂ��ēx�\��
	$loginmsg = qq|<span class="error">�p�X���[�h���Ⴂ�܂��B�ēx���͂��ĉ������B</span>|;
	$mode = "";
}
if( $pwcheckresult == 3 ) {
	# �����p�X���[�h�ݒ胂�[�h
	if( $cpwnewpw eq "" ) {
		# �V�p�X���[�h�̓��͂��܂��Ȃ���̓t�H�[����\��
		&makepw();
		$mode = "makepw";
	}
	# �V�p�X���[�h�̓��͂�����΁A���[�h�� dochangepw �Ȃ̂ł��̂܂܎��s
}

# ����
if( $mode eq "" ) {
	# ���O�C�����
	&logindisp($loginmsg);
}
elsif( $mode eq "home" ) {
	# �������
	&firstdisp();
}
elsif( $mode eq "calender" ) {
	# ���ԗ\��\�̕ҏW(�������)
	&editcalendardisp();
}
elsif( $mode eq "editcalendar" ) {
	# ���ԗ\��\�̕ҏW(����̌��̕\��)
	&editonemonthdisp();
}
elsif( $mode eq "editcalendardate" ) {
	# ���ԗ\��\�̕ҏW(����̓��̕\��)
	&editdatedisp();
}
elsif( $mode eq "recorddate" ) {
	# ���ԗ\��\�̓���̓��̗\���ۑ�
	&calendarsave();
}
elsif( $mode eq "calendardelete" ) {
	# ���ԗ\��\�̓���̓��̗\���ۑ�
	&calendardelete();
}

elsif( $mode eq "weekly" ) {
	# ��T�Ԃ̔ėp�\��\�̕ҏW
	&weeklydisp();
}
elsif( $mode eq "weeklysave" ) {
	# ��T�Ԃ̔ėp�\��\�̕ۑ�
	&weeklysave();
}
elsif( $mode eq "long" ) {
	# �����\��̕ҏW
	&longdisp();
}
elsif( $mode eq "longedit" ) {
	# �����\��̑I��ҏW(���ڍ쐬�E�ύX)
	&longeditdisp();
}
elsif( $mode eq "longwrite" ) {
	# �����\��̏�������
	&longwrite();
}
elsif( $mode eq "longdelete" ) {
	# �����\��̍폜
	&longdelete();
}
elsif( $mode eq "longlistdelete" ) {
	# �����\��̈ꊇ�폜�i����܂ł̑S�f�[�^���ڂ��폜�j
	&longlistdelete();
}


elsif( $mode eq "cpw" ) {
	# �p�X���[�h�̕ύX
	&changepassword();
}
elsif( $mode eq "dochangepw" ) {
	# �p�X���[�h�̕ύX�����s
	&dochangepw();
}




# ---------------- #
# �p�����[�^�̕��� #
# ---------------- #
sub splitparam()
{
	# ����
	my $buffer = "";
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	}
#	my $querybuffer = $ENV{'QUERY_STRING'} . '&' . $buffer;
	my $querybuffer = $buffer;	# POST�̂�

	# ����
	my @pairs = split(/&/,$querybuffer);
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);

		# 2�o�C�g�������f�R�[�h
		$value =~ s/\+/ /g;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

		# ����
		if( $name eq "mode" ) {
			$mode = $value;		# �X�N���v�g���샂�[�h
		}
		elsif( $name eq "pw" ) {
			$upw = $value;		# �p�X���[�h
		}
		elsif( $name eq "encpw" ) {
			$encupw = $value;	# �G���R�[�h�ς݃p�X���[�h
		}

		# --- 1�T�Ԃ̔ėp�\��\�p ---
		elsif( $name eq "ecaption" ) {	$wscaption = $value;	}
		elsif( $name eq "erow00" ) {	$wsrow0[0] = $value;	}
		elsif( $name eq "erow01" ) {	$wsrow0[1] = $value;	}
		elsif( $name eq "erow02" ) {	$wsrow0[2] = $value;	}
		elsif( $name eq "erow10" ) {	$wsrow1[0] = $value;	}
		elsif( $name eq "erow11" ) {	$wsrow1[1] = $value;	}
		elsif( $name eq "erow12" ) {	$wsrow1[2] = $value;	}
		elsif( $name eq "erow20" ) {	$wsrow2[0] = $value;	}
		elsif( $name eq "erow21" ) {	$wsrow2[1] = $value;	}
		elsif( $name eq "erow22" ) {	$wsrow2[2] = $value;	}
		elsif( $name eq "erow30" ) {	$wsrow3[0] = $value;	}
		elsif( $name eq "erow31" ) {	$wsrow3[1] = $value;	}
		elsif( $name eq "erow32" ) {	$wsrow3[2] = $value;	}
		elsif( $name eq "erow40" ) {	$wsrow4[0] = $value;	}
		elsif( $name eq "erow41" ) {	$wsrow4[1] = $value;	}
		elsif( $name eq "erow42" ) {	$wsrow4[2] = $value;	}
		elsif( $name eq "erow50" ) {	$wsrow5[0] = $value;	}
		elsif( $name eq "erow51" ) {	$wsrow5[1] = $value;	}
		elsif( $name eq "erow52" ) {	$wsrow5[2] = $value;	}
		elsif( $name eq "erow60" ) {	$wsrow6[0] = $value;	}
		elsif( $name eq "erow61" ) {	$wsrow6[1] = $value;	}
		elsif( $name eq "erow62" ) {	$wsrow6[2] = $value;	}
		elsif( $name eq "erow70" ) {	$wsrow7[0] = $value;	}
		elsif( $name eq "erow71" ) {	$wsrow7[1] = $value;	}
		elsif( $name eq "erow72" ) {	$wsrow7[2] = $value;	}

		# --- ���ԗ\��\�p ---
		elsif( $name eq "edityear" ) {	$cedityear = $value;	}
		elsif( $name eq "editmonth" ) {	$ceditmonth = $value;	}
		elsif( $name eq "editday" ) {	$ceditday = $value;	}
		elsif( $name eq "schedule1" ) {	$ceschedule[0] = $value;	}
		elsif( $name eq "schedule2" ) {	$ceschedule[1] = $value;	}
		elsif( $name eq "schedule3" ) {	$ceschedule[2] = $value;	}
		elsif( $name eq "seal1" ) {	$ceseal[0] = $value;	}
		elsif( $name eq "seal2" ) {	$ceseal[1] = $value;	}

		# --- �����\��\�p ---
		elsif( $name eq "editnum" ) {	$longeditnum = $value;	}
		elsif( $name eq "lwyear"  ) {	$longedityear  = $value;	}
		elsif( $name eq "lwmonth" ) {	$longeditmonth = $value;	}
		elsif( $name eq "lwday"   ) {	$longeditday   = $value;	}
		elsif( $name eq "ldata"   ) {	$longeditdata  = $value;	}
		elsif( $name eq "lvalue"  ) {	$longeditvalue = $value;	}

		# --- �p�X���[�h�ύX�p ---
		elsif( $name eq "nowpw" ) {	$cpwnowpw = $value;	}
		elsif( $name eq "newpw" ) {	$cpwnewpw = $value;	}
	}
	#if( &clcadmin() == 0 ) { exit(1); }
}

#sub clcadmin
#{
#	foreach my $line (@datahtml) {
#		if( $line =~ m/<a href=.*nishishi\.com.*>/ ) {
#			if( $line =~ m/copy/ ) {
#				return 1;
#			}
#		}
#	}
#	return 0;
#}

# -------------------- #
# �p�X���[�h�̃`�F�b�N #
# -------------------- #
sub checkpassword
{
	my $recordedpass;
	my $thistimepass;

	# ���[�U�����͂����p�X���[�h
	my $userpassword    = shift @_;
	my $encuserpassword = shift @_;

	# �L�^����Ă���p�X���[�h�𓾂�(recorded pass)
	if( $passwordtype == 0 ) {
		# �Œ�
		$recordedpass = crypt($password,$cryptkey);
	}
	elsif( $passwordtype == 1 ) {
		# �t�@�C��
		open(IN,"$pwfile") || &errorexit("�p�X���[�h�i�[�t�@�C�����ǂ߂Ȃ��B<br><br>������s���́A���g������ۂɂ����p�X���[�h�i�[�t�@�C�����A�b�v���[�h���Ă����ĉ������B��������ƁA�p�X���[�h�쐬��ʂ��o�܂��B");
		$recordedpass = <IN>;
		close(IN);
		
		# �p�X���[�h���i�[����Ă��邩�ǂ����H
		if( $recordedpass eq "" ) {
			# �i�[����Ă��Ȃ���Ώ�����s��
			return 3;
		}
	}

	# ���[�U��������͂����p�X���[�h�𓾂�
	if( $encuserpassword ne "" ) {
		# ���ɃG���R�[�h�ς݂̃p�X���[�h������ꍇ�͂�������̂܂܎g�p
		$thistimepass = $encuserpassword;
	}
	else {
		# �܂��G���R�[�h����ĂȂ��ꍇ�̓��[�U�����͂������̃p�X���[�h���G���R�[�h���Ă���g�p
		$thistimepass = crypt($userpassword,$cryptkey);
	}

	# ��v���m�F
	#<DEBUG>print "THIS TIME: $thistimepass<br>RECORDED: $recordedpass<br>\n";
	if( $thistimepass eq $recordedpass ) {
		# ��v������OK
		$encupw = $thistimepass;	# �G���R�[�h��̃��[�U�p�X���[�h������̏����̂��߂ɕϐ��Ɋi�[
		return 1;
	}
	
	# ��v���Ȃ�������G���[
	return 0;
}

# ------------------ #
# ���O�C����ʂ̕\�� #
# ------------------ #
sub logindisp
{
	# ���O�C����ʂ̕\��
	$loginmsg = shift @_;

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	&loaddata('\[Login\]','\[/Login\]');
	&loaddata('\[Foot\]','\[/Foot\]');
}

# -------------- #
# ������ʂ̕\�� #
# -------------- #
sub firstdisp
{
	# ������ʂ̕\��
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	&loaddata('\[First\]','\[/First\]');
	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------- #
# �p�X���[�h�̕ύX #
# ---------------- #
sub changepassword
{
	# �p�X���[�h�ύX���
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	if( $passwordtype == 0 ) {
		# �p�X���[�h���Œ胂�[�h�Ȃ�ύX�s��
		print qq|<p><span class="error">����CGI�̐ݒ�ŁA�p�X���[�h�͌Œ肳��Ă��܂��B���[�U�ɂ��p�X���[�h�̕ύX�͂ł��܂���B</span></p>\n|;
		print qq|<p>�p�X���[�h��ύX�\\\�ɂ���ɂ́ACGI�̃\\\�[�X���J���āA�p�X���[�h�w����u�Œ�v����u�ύX�\\\�v�ɏ��������ĉ������B���̑���́A����CGI�̊Ǘ��҂ɂ����ł��܂���B</p>\n|;
		print qq|<form><input type="button" value="�߂�" onClick="history.back();"></form>|;
	}
	else {
		# �p�X���[�h���ύX�\���[�h�Ȃ�ύX�t�H�[����\��
		&loaddata('\[ChangePW\]','\[/ChangePW\]');
	}
	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------------- #
# �p�X���[�h�̕ύX�����s #
# ---------------------- #
sub dochangepw
{
	# �p�X���[�h�̕ύX�����s
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# �p�X���[�h�̃`�F�b�N
	if( &checkpassword($cpwnowpw,"") == 0 ) {
		# �p�X���[�h����v���Ȃ������ꍇ
		print qq|<p><span class="error">�p�X���[�h����v���܂���B</span></p>\n|;
		print qq|<form><input type="button" value="�߂�" onClick="history.back();"></form>|;
	}
	else {
		# �p�X���[�h����v������ύX
		&workcpw($cpwnewpw);

		# ���b�Z�[�W
		print qq|<p>�p�X���[�h��ύX���܂����B���쐬�����V�����p�X���[�h�Ń��O�C���������ĉ������B</p>\n|;
		# �߂�t�H�[����\��
		&backlink("","���O�C����ʂ�");
	}

	&loaddata('\[Foot\]','\[/Foot\]');
}

sub workcpw
{
	# �p�X���[�h���G���R�[�h���ăp�X���[�h�t�@�C���ɋL�^
	my $npw = shift @_;
	my $writestring = crypt($npw,$cryptkey);

	# �p�X���[�h�t�@�C���ɏ�������
	open(OUT,"> $pwfile") || &errorexit("�p�X���[�h�i�[�t�@�C�����������݃��[�h�ŊJ���܂���ł����B�������݋֎~�ɂȂ��Ă��Ȃ����m�F���ĉ������B");
	print OUT "$writestring";
	close(OUT);
}

# ---------------------- #
# �����p�X���[�h�ݒ��� #
# ---------------------- #
sub makepw
{
	# �p�X���[�h�ύX���
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	&loaddata('\[MakePW\]','\[/MakePW\]');
	&loaddata('\[Foot\]','\[/Foot\]');
}

# -------------------------------- #
# ��T�Ԃ̔ėp�\��\�ҏW��ʂ̕\�� #
# -------------------------------- #
sub weeklydisp
{
	# ��T�Ԃ̔ėp�\��\�ҏW���
	my ( $caption, @rows , @row0, @row1, @row2, @row3, @row4, @row5, @row6, @row7 );

	# �t�@�C����ǂ�
	open(IN,"$weeklyfile") || &errorexit("��T�Ԃ̔ėp�\\\��\�t�@�C�� $weeklyfile ���ǂ߂܂���ł����B");
	my @weekdata = <IN>;
	close(IN);

	# �t�@�C���̑S���g����HTML�^�O���f�R�[�h
	@weekdata = &decodehtmltags(@weekdata);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# �t�@�C���̒��g�𕪉�
	foreach my $line (@weekdata) {
		# �u���v�ŕ���
		my @val2;
		my ($name, $value, @val2) = split(/=/, $line);

		# ---ADD--- Ver 1.1 : �l�Ɂu=�v���܂܂�Ă���ƃJ�b�g����Ă��܂��̂�h���R�[�h(���}�[�u)
		foreach my $addval ( @val2 ) {
			$value = $value . "=" . $addval;
		}

		if( $name =~ m/caption/i ) {
			$caption = $value;
		}
		elsif( $name eq "head" ) {
			$rows[0] = $value;
		}
		elsif( $name =~ m/(\d)/ ) {
			$rows[$1] = $value;
		}
	}

	# �e���ڂɕ���
	@row0 = split(/\|/, $rows[0]);
	@row1 = split(/\|/, $rows[1]);
	@row2 = split(/\|/, $rows[2]);
	@row3 = split(/\|/, $rows[3]);
	@row4 = split(/\|/, $rows[4]);
	@row5 = split(/\|/, $rows[5]);
	@row6 = split(/\|/, $rows[6]);
	@row7 = split(/\|/, $rows[7]);

	print qq|<h2>1�T�Ԃ̔ėp�\\\��\\\</h2>\n<p class="title">�������������ӏ���ҏW���ĉ������B�Ō�Ɂu�ۑ��v�{�^�����N���b�N���ĉ������B</p>|;

	# �t�H�[����\��
	&loaddata('\[FormTop\]','\[/FormTop\]');

	print <<"EOM";
		<input type="hidden" name="mode" value="weeklysave">
		<table class="inputtable">
		<tr>
			<th colspan="3">CAPTION: <input type="text" name="ecaption" value="$caption" class="ecaption"></th>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow00" value="$row0[0]" class="week"></td>
			<td class="th"><input type="text" name="erow01" value="$row0[1]" class="place"></td>
			<td class="th"><input type="text" name="erow02" value="$row0[2]" class="lect"></td>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow10" value="$row1[0]" class="week"></td>
			<td><input type="text" name="erow11" value="$row1[1]" class="place"></td>
			<td><input type="text" name="erow12" value="$row1[2]" class="lect"></td>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow20" value="$row2[0]" class="week"></td>
			<td><input type="text" name="erow21" value="$row2[1]" class="place"></td>
			<td><input type="text" name="erow22" value="$row2[2]" class="lect"></td>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow30" value="$row3[0]" class="week"></td>
			<td><input type="text" name="erow31" value="$row3[1]" class="place"></td>
			<td><input type="text" name="erow32" value="$row3[2]" class="lect"></td>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow40" value="$row4[0]" class="week"></td>
			<td><input type="text" name="erow41" value="$row4[1]" class="place"></td>
			<td><input type="text" name="erow42" value="$row4[2]" class="lect"></td>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow50" value="$row5[0]" class="week"></td>
			<td><input type="text" name="erow51" value="$row5[1]" class="place"></td>
			<td><input type="text" name="erow52" value="$row5[2]" class="lect"></td>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow60" value="$row6[0]" class="week"></td>
			<td><input type="text" name="erow61" value="$row6[1]" class="place"></td>
			<td><input type="text" name="erow62" value="$row6[2]" class="lect"></td>
		</tr>
		<tr>
			<td class="th"><input type="text" name="erow70" value="$row7[0]" class="week"></td>
			<td><input type="text" name="erow71" value="$row7[1]" class="place"></td>
			<td><input type="text" name="erow72" value="$row7[2]" class="lect"></td>
		</tr>
		</table>
		<br>
EOM

	&loaddata('\[FormBottom\]','\[/FormBottom\]');

	# �����̃��b�Z�[�W
	print qq|<p><span class="note">|;
	if( $voidtags == 1 ) {
		# HTML�^�O�������̏ꍇ
		print qq|��HTML�^�O�̎g�p��<strong>������</strong>�ݒ肳��Ă��܂��B�^�O���L�q���Ă��A���̂܂ܕ\\\������܂��B<br>|;
	}
	else {
		# HTML�^�O���L���̏ꍇ
		print qq|�����ړ��ŉ��s���������ꍇ�́A���p�� <span class="code">&lt;br&gt;</span> �Ɠ��͂��ĉ������B���̑���HTML�^�O�����ׂĎg�p�\\\�ł��B���p�́u&lt;�v��u&gt;�v��HTML�^�O�ƔF������܂��̂ŁA�����Ƃ��ĒP�Ƃœ��͂��Ȃ��ŉ������B�\\\��������čĕҏW�ł��Ȃ��Ȃ�ꍇ������܂��B�icalendar.pl�̐ݒ肩��AHTML�^�O�̎g�p�𖳌��ɐݒ肷�邱�Ƃ��ł��܂��B�j<br>|;
	}
	print qq|���j�������܂߂āA1�s�܂邲�Ƌ󗓂ɂ���΁A���̍s�͕\\\������Ȃ��Ȃ�܂��B</span></p>\n|;

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ------------------------ #
# ��T�Ԃ̔ėp�\��\��ۑ� #
# ------------------------ #
sub weeklysave
{
	# ��T�Ԃ̔ėp�\��\��ҏW

	# �t�@�C���ɏ���
	open(OUT,"> $weeklyfile") || &errorexit("��T�Ԃ̔ėp�\\\��\\\�t�@�C�� $weeklyfile ���������݃��[�h�ŊJ���܂���ł����B");

	print OUT "# ���T�Ԕėp�X�P�W���[���p�f�[�^�t�@�C����\n";
	print OUT "caption=$wscaption\n";
	print OUT "head=$wsrow0[0]|$wsrow0[1]|$wsrow0[2]\n";
	print OUT "1=$wsrow1[0]|$wsrow1[1]|$wsrow1[2]\n";
	print OUT "2=$wsrow2[0]|$wsrow2[1]|$wsrow2[2]\n";
	print OUT "3=$wsrow3[0]|$wsrow3[1]|$wsrow3[2]\n";
	print OUT "4=$wsrow4[0]|$wsrow4[1]|$wsrow4[2]\n";
	print OUT "5=$wsrow5[0]|$wsrow5[1]|$wsrow5[2]\n";
	print OUT "6=$wsrow6[0]|$wsrow6[1]|$wsrow6[2]\n";
	print OUT "7=$wsrow7[0]|$wsrow7[1]|$wsrow7[2]\n";

	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	my $modifytime = &get_timestamp($weeklyfile);
	print qq|<p class="endmsg">�ۑ����܂����B <span class="note">�y�X�V�����F $modifytime�z</span></p>|;

	# �߂�t�H�[����\��
	&backlink("home","");

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ------------------------ #
# �����\��\�ҏW��ʂ̕\�� #
# ------------------------ #
sub longdisp
{
	# �����\��\�ҏW���

	# �t�@�C����ǂ�
	open(IN,"$longfile") || &errorexit("�����\\\��t�@�C�� $longfile ���ǂ߂܂���ł����B");
	my @longdata = <IN>;
	close(IN);

	# �t�@�C���̑S���g����HTML�^�O���f�R�[�h
	@longdata = &decodehtmltags(@longdata);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<h2>�����\\\��\\\</h2>\n<p class="title">�V�K�ɒǉ�����ꍇ�́u�V�K�쐬�v�Ƀ`�F�b�N�����āA�����̍��ڂ��������������ꍇ�͏������������ӏ��Ƀ`�F�b�N�����āA�u��L�̑I�����ڂ�ҏW�v�{�^���������ĉ������B<br><span class="note">��HTML�^�O�̎g�p��L���ɐݒ肵�Ă���ꍇ�ł��A���L�̈ꗗ�ɂ�HTML�^�O���\\\�[�X�̂܂ܕ\\\������Ă��܂��B</span></p>|;

	# �t�H�[����\��
	&loaddata('\[FormTop\]','\[/FormTop\]');

	print qq|<input type="hidden" name="mode" value="longedit">\n|;

	# �t�@�C���̒��g�𕪉����ĕ\��
	print qq|<table class="inputtable">\n|;
	print qq|<tr><th>No.</th><th>���t</th><th>���e</th></tr>\n|;
	my $counter=0;
	foreach my $line (@longdata) {
		# �J���}�ŕ���
		my ($lid, $ldata, $lvalue) = split(/,/, $line);
		# �J�E���g(No.�p��)
		$counter++;
		# ���R�[�h��\��
		print qq|<tr><td><input type="radio" name="editnum" value="$counter" id="eid$counter"><label for="eid$counter">$counter</label></td><td>$ldata</td><td>$lvalue</td></tr>|;
	}
	print qq|<tr><td colspan="3"><input type="radio" name="editnum" value="0" id="new" checked><label for="new">�V�K�쐬</label></td></tr>|;
	print qq|</table>\n|;
	print "<br>\n";

	# �t�H�[�������
	&closeform("��L�̑I�����ڂ�ҏW");

	# �߂�t�H�[����\��
	&backlink("home","");

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------------------------- #
# �����\��\���ڂ̕ҏW�i�ǉ��E�ύX�j #
# ---------------------------------- #
sub longeditdisp
{
	# �����\��\�ҏW���
	my ($lid, $ldata, $lvalue);
	my ($mday,$month,$year);

	# �t�@�C����ǂ�
	open(IN,"$longfile") || &errorexit("�����\\\��t�@�C�� $longfile ���ǂ߂܂���ł����B");
	my @longdata = <IN>;
	close(IN);

	# �t�@�C���̑S���g����HTML�^�O���f�R�[�h
	@longdata = &decodehtmltags(@longdata);

	# �ҏW�p�����f�[�^�̓ǂݏo��
	if( $longeditnum > 0 ) {
		# �ԍ����w�肳��Ă���΁i���V�K�쐬�łȂ���΁j
		($lid, $ldata, $lvalue) = split(/,/, $longdata[$longeditnum-1]);
		# ���t�𕪉�
		($mday,$month,$year) = (localtime($lid))[3,4,5];
	}
	else {
		# ���̓��t�𓾂�
		($mday,$month,$year) = (localtime(time))[3,4,5];
		# �V�K�쐬�p�ɁA�z��́u�Ō�̔ԍ��v�̎����w��
		$longeditnum = $#longdata + 2;
	}

	# ���t�𒲐�
	$year  = $year  + 1900;
	$month = $month + 1;

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<h2>�����\\\�� ���ڕҏW</h2>\n<p class="title">�\\\��������t�Ɠ��e����͂��ĉ������B�u�ҏW���e��ۑ��v�{�^���������ƕۑ�����܂��B</p>\n|;

	# �t�H�[����\��
	&loaddata('\[FormTop\]','\[/FormTop\]');

	print <<"EOM";
	<input type="hidden" name="mode" value="longwrite">
	<input type="hidden" name="editnum" value="$longeditnum">
	<table class="inputtable">
	<tr>
		<th colspan="2">No.$longeditnum</th>
	</tr>
	<tr>
		<td>�\\\������</td>
		<td>
			<input type="text" name="lwyear"  value="$year"  style="width: 3em;">�N
			<input type="text" name="lwmonth" value="$month" style="width: 2em;">��
			<input type="text" name="lwday"   value="$mday"  style="width: 2em;">��<br>
			<span class="note">�������Ŏw�肵�����t���A���̍��ڂ̕\\\�������ɂȂ�܂��B�i���̓��ȍ~�͕\\\������܂���B�j</span><br>
		</td>
	</tr>
	<tr>
		<td>���t(������)</td>
		<td>
			<input type="text" name="ldata"  value="$ldata"  style="width: 24em;"><br>
			<span class="note">�������ɓ��͂������e�����t���ɕ\\\������܂��B���͂��ȗ�����΁A��L�̓��t���玩���I�ɕ�����𐶐����܂��B</span><br>
		</td>
	</tr>
	<tr>
		<td>�\\\����e</td>
		<td>
			<input type="text" name="lvalue"  value="$lvalue"  style="width: 36em;">
		</td>
	</tr>
	</table>
	<br>
EOM

	&loaddata('\[FormBottom\]','\[/FormBottom\]');

	# �폜�p�{�^��
	unless( $longeditnum == $#longdata + 2 ) {
		# �V�K�f�[�^�łȂ���΍폜�p�{�^����\��
		print qq|<table align="right" border="1" class="caution"><tr><td>\n|;
		&loaddata('\[FormTop\]','\[/FormTop\]');
		print qq|<input type="hidden" name="editnum" value="$longeditnum">\n|;
		print qq|<input type="hidden" name="mode" value="longdelete">\n|;
		&closeform("���̍��ڂ��폜");
		print qq|</td></tr></table>|;
	}

	# �����̃��b�Z�[�W
	print qq|<p><span class="note">|;
	if( $voidtags == 1 ) {
		# HTML�^�O�������̏ꍇ
		print qq|��HTML�^�O�̎g�p��<strong>������</strong>�ݒ肳��Ă��܂��B�^�O���L�q���Ă��A���̂܂ܕ\\\������܂��B<br>|;
	}
	else {
		# HTML�^�O���L���̏ꍇ
		print qq|�����ړ��ŉ��s���������ꍇ�́A���p�� <span class="code">&lt;br&gt;</span> �Ɠ��͂��ĉ������B���̑���HTML�^�O�����ׂĎg�p�\\\�ł��B�icalendar.pl�̐ݒ肩��AHTML�^�O�̎g�p�𖳌��ɐݒ肷�邱�Ƃ��ł��܂��B�j<br>|;
	}
	print qq|</span></p>\n|;

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ------------------------ #
# �����\��\���ڂ̏������� #
# ------------------------ #
sub longwrite
{
	# �����\��\���ڂ̏�������

	# �f�[�^�̃`�F�b�N
	unless( $longeditnum > 0 ) {
		# 1�ȏ�̐��l�łȂ����
		&errorexit("longeditnum�ϐ��ɕs���Ȓl���������Ă��܂��B1�ȏ�̐����łȂ���΂Ȃ�܂���B");
	}
	unless( $longedityear > 1970 && $longedityear < 2038 && $longeditmonth > 0 && $longeditmonth <= 12 && $longeditday > 0 && $longeditday <= 31 ) {
		# ���t�̍\���v�f���s���ȏꍇ
		&errorback("���t�̍\\\���v�f���s���ł��B���������l�i���p�j����͂��ĉ������B�F $longedityear�N $longeditmonth�� $longeditday��");
	}

	# �t�@�C����ǂ�
	open(IN,"$longfile") || &errorexit("�����\\\��t�@�C�� $longfile ���ǂ߂܂���ł����B");
	my @longdata = <IN>;
	close(IN);

	# �\���������̃G�|�b�N�b�����߂�
	$limitdate = timelocal(0, 0, 12, $longeditday, $longeditmonth - 1, $longedityear);

	# ���t�����񂪓��͂���Ă��Ȃ���ΐ�������
	my $monthspace = " ";
	my $datespace  = " ";
	unless( $longeditmonth < 10 ) {	$monthspace = ""; }
	unless( $longeditday < 10 )   { $datespace  = ""; }
	if( $longeditdata eq "" ) {
		$longeditdata = "$longedityear�N$monthspace$longeditmonth��$datespace$longeditday��";
	}

	# �s���쐬
	my $writeline = "$limitdate,$longeditdata,$longeditvalue\n";

	# �쐬�����s��ǉ�
	$longdata[$longeditnum-1] = $writeline;

	# �z����\�[�g
	my @sortedld = sort { $a cmp $b } @longdata;

	# ��������
	open(OUT,"> $longfile") || &errorexit("�����\\\��\\\�t�@�C�� $longfile ���������݃��[�h�ŊJ���܂���ł����B");
	foreach my $line (@sortedld) {
		# �S�s�ɏ�������
		print OUT "$line";
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>�������݂܂����B</p>|;

	# �߂�t�H�[����\��
	&backlink("long","�����\\\�胊�X�g�ɖ߂�");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# -------------------- #
# �����\��\���ڂ̍폜 #
# -------------------- #
sub longdelete
{
	# �����\��\���ڂ̍폜
	my $count=0;

	# �f�[�^�̃`�F�b�N
	unless( $longeditnum > 0 ) {
		# 1�ȏ�̐��l�łȂ����
		&errorexit("longeditnum�ϐ��ɕs���Ȓl���������Ă��܂��B1�ȏ�̐����łȂ���΂Ȃ�܂���B");
	}

	# �t�@�C����ǂ�
	open(IN,"$longfile") || &errorexit("�����\\\��t�@�C�� $longfile ���ǂ߂܂���ł����B");
	my @longdata = <IN>;
	close(IN);

	# ��������
	open(OUT,"> $longfile") || &errorexit("�����\\\��\\\�t�@�C�� $longfile ���������݃��[�h�ŊJ���܂���ł����B");
	foreach my $line (@longdata) {
		# �S�s���[�v
		$count++;
		unless( $count == $longeditnum ) {
			# �폜�Ώۍs�łȂ���Ώ���
			print OUT "$line";
		}
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>$longeditnum�Ԗڂ̍��ڂ��폜���܂����B</p>|;

	# �߂�t�H�[����\��
	&backlink("long","�����\\\�胊�X�g�ɖ߂�");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ------------------------ #
# �����\��\���ڂ̈ꊇ�폜 #
# ------------------------ #
sub longlistdelete
{
	# �����\��\���ڂ̈ꊇ�폜�i����܂ł̑S�f�[�^���폜�j
	my $delcount=0;

	# �t�@�C����ǂ�
	open(IN,"$longfile") || &errorexit("�����\\\��t�@�C�� $longfile ���ǂ߂܂���ł����B");
	my @longdata = <IN>;
	close(IN);

	# ���݂���36���ԑO�̎����i�G�|�b�N�b�j�𓾂�
	my $yesterday = (time) - (36*60*60);

	# ��������
	open(OUT,"> $longfile") || &errorexit("�����\\\��\\\�t�@�C�� $longfile ���������݃��[�h�ŊJ���܂���ł����B");
	foreach my $line (@longdata) {
		# �f�[�^�𕪊�
		($lid, undef, undef) = split(/,/, $line);
		# �������r
		if( $yesterday < $lid ) {
			# �폜�Ώۍs�łȂ���Ώ���
			print OUT "$line";
		}
		else {
			# �폜�����J�E���g
			$delcount++;
		}
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>$delcount�̍��ڂ��폜���܂����B</p>|;

	# �߂�t�H�[����\��
	&backlink("long","�����\\\�胊�X�g�ɖ߂�");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ---------------------------------------- #
# ���ԗ\��\�i�J�����_�[�\��\�j�̕ҏW��� #
# ---------------------------------------- #
sub editcalendardisp
{
	# �J�����_�[�\��\�ҏW���
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# �\���N���̐ݒ�
	my ($dispmonth,$dispyear) = (localtime(time))[4,5];
	$dispyear  = $dispyear + 1900;
	$dispmonth = $dispmonth + 1;

	print qq|<hr class="thin">\n|;

	# �J�����_�[�\���w���i�N,��,�\��t�@�C�����j
	# ����
	#print "<p>�� $dispyear �N $dispmonth ���̃J�����_�[<br></p>\n";
	&calendarpackage::makecalendar($dispyear, $dispmonth, $calendarfile);

	# ����
	if( $dispmonth < 12 ) {
		# 11���܂łȂ猎��1��������
		$dispmonth++;
	}
	else {
		# 12���Ȃ�A�N��1�������Č���1�ɂ���
		$dispyear++;
		$dispmonth = 1;
	}
	#print "<p>�� $dispyear �N $dispmonth ���̃J�����_�[<br></p>\n";
	&calendarpackage::makecalendar($dispyear, $dispmonth, $calendarfile);

	print qq|<br><hr class="thin"><br>\n|;

	# �߂郊���N
	&backlink("home","");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ---------------------------- #
# ���ԗ\��\�̓��茎�̕ҏW��� #
# ---------------------------- #
sub editonemonthdisp
{
	# �J�����_�[�\��\�ҏW���
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# �\���N���̐ݒ�i�p�����[�^�Ŏw�肳�ꂽ�N���j
	my $dispyear  = $cedityear;
	my $dispmonth = $ceditmonth;

	# ���t�I���t�H�[���̕\��
	print qq|<p class="title">$dispyear�N$dispmonth���̃f�[�^��ҏW�E�ǉ����܂��B���t��I�����ĉ������B</p>\n|;
	&editcalendarrecorddisp($dispyear, $dispmonth);

	print qq|<hr class="thin">\n|;

	# ���ԗ\��\�J�����_�[�̕\���`�߂郊���N
	&makecommoncalendarparts($dispyear, $dispmonth, $calendarfile)

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------------------- #
# ���ԗ\��\�̓�����̕ҏW��� #
# ---------------------------- #
sub editdatedisp
{
	# �J�����_�[�\��\�ҏW���
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# �\���N���̐ݒ�i�p�����[�^�Ŏw�肳�ꂽ�N�����j
	my $dispyear  = $cedityear;
	my $dispmonth = $ceditmonth;
	my $dispday   = $ceditday;

	# ���R�[�h�쐬�t�H�[���̕\��
	print qq|<p class="title">�\\\�����͂��āA�u���̓��̃f�[�^��ۑ��v�{�^�����N���b�N���ĉ������B</p>\n|;
	&editcalendardate($dispyear, $dispmonth, $dispday);

	# �����̃��b�Z�[�W
	print qq|<p><span class="note">|;
	if( $voidtags == 1 ) {
		# HTML�^�O�������̏ꍇ
		print qq|��HTML�^�O�̎g�p��<strong>������</strong>�ݒ肳��Ă��܂��B�^�O���L�q���Ă��A���̂܂ܕ\\\������܂��B<br>|;
	}
	else {
		# HTML�^�O���L���̏ꍇ
		print qq|��HTML�^�O�͂��ׂĎg�p�\\\�ł��B���p�́u&lt;�v��u&gt;�v��HTML�^�O�ƔF������܂��̂ŁA�����Ƃ��ĒP�Ƃœ��͂��Ȃ��ŉ������B�icalendar.pl�̐ݒ肩��AHTML�^�O�̎g�p�𖳌��ɐݒ肷�邱�Ƃ��ł��܂��B�j<br>|;
	}
	print qq|</span></p>\n|;

	print qq|<hr class="thin"><br>\n|;

	# ���ԗ\��\�J�����_�[�̕\���`�߂郊���N
	&makecommoncalendarparts($dispyear, $dispmonth, $calendarfile)

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------- #
# ���ԗ\��\�̕ۑ� #
# ---------------- #
sub calendarsave
{
	# �L�^��
	my $year  = $cedityear;
	my $month = $ceditmonth;
	my $day   = $ceditday;

	my @record;		# �L�^�p������̔z��
	my $recstring;	# �L�^�p������
	my $recdate;	# ���R�[�h�̓��t

	# �\����e1
	if( $ceschedule[0] ne "" ) {
		# �C�ӑ��ɕ����񂪂���΂�����L�^
		push( @record, "$ceschedule[0]<>" );
	}
	elsif( $ceseal[0] ne "" ) {
		# �I�𑤂ɕ����񂪂���΂�����L�^
		push( @record, "$ceseal[0]<>" );
	}

	# �\����e2
	if( $ceschedule[1] ne "" ) {
		# �C�ӑ��ɕ����񂪂���΂�����L�^
		push( @record, "$ceschedule[1]<>" );
	}
	elsif( $ceseal[1] ne "" ) {
		# �I�𑤂ɕ����񂪂���΂�����L�^
		push( @record, "$ceseal[1]<>" );
	}

	# ���l��
	# �\����e1
	if( $ceschedule[2] ne "" ) {
		# �����񂪂���΋L�^
		push( @record, "$ceschedule[2]<>" );
	}

	# �L�^�p������̐���
	$recdate   = "$year/$month/$day,";
	$recstring = $recdate . join( "", @record );
	# �r���̉��s���폜���Ė����ɉ��s��t��
	$recstring =~ s/\n//g;
	$recstring =~ s/\r//g;
	$recstring = $recstring . "\n";

	# �t�@�C����ǂ�
	open(IN,"$calendarfile") || &errorexit("���ԗ\\\��t�@�C�� $calendarfile ���ǂ߂܂���ł����B");
	my @allshcedule = <IN>;
	close(IN);

	# �������ݗp�z����쐬
	my @scheduleforwrite;
	foreach my $line (@allshcedule) {
		# �S�s���[�v
		unless( $line =~ m/$recdate/i ) {
			# ����̃f�[�^�Ɠ��t����v���Ȃ���Ώ�������
			push( @scheduleforwrite, $line );
		}
	}
	push( @scheduleforwrite, $recstring );

	# �t�@�C�����\�[�g
	my @sortedsw = sort { $a cmp $b } @scheduleforwrite;

	# ��������
	open(OUT,"> $calendarfile") || &errorexit("���ԗ\\\��t�@�C�� $calendarfile ���������݃��[�h�ŊJ���܂���ł����B");
	foreach my $line (@sortedsw) {
		# �S�s����������
		print OUT "$line";
	}
	close(OUT);

	# ���ʕ񍐉��
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	my $modifytime = &get_timestamp($calendarfile);
	print qq|<p class="endmsg">�ۑ����܂����B <span class="note">�y�X�V�����F $modifytime�z</span></p>|;

	print qq|<hr class="thin">\n|;

	# ���t�I���t�H�[���̕\��
	print qq|<p class="title">���̓��t��ҏW����ꍇ�͑I�����ĉ������B</p>\n|;
	&editcalendarrecorddisp($year, $month, $day+1);

	print qq|<hr class="thin">\n|;

	# ���ԗ\��\�J�����_�[�̕\���`�߂郊���N
	&makecommoncalendarparts($year, $month, $calendarfile)

	&loaddata('\[Foot\]','\[/Foot\]');
}

# -------------------------------------------------- #
# ���ԗ\��\�J�����_�[�`�߂郊���N�܂ŋ��ʕ����̐��� #
# -------------------------------------------------- #
sub makecommoncalendarparts
{
	my ($dispyear, $dispmonth, $calendarfile) = @_;

	# �J�����_�[�\���w���i�N,��,�\��t�@�C�����j
	#print "$dispyear �N $dispmonth ���̃J�����_�[<br>\n";
	&calendarpackage::makecalendar($dispyear, $dispmonth, $calendarfile);

	# �߂郊���N
	print qq|<table><tr><td>|;
	&backlink("calender","���ԗ\\\��\\\TOP�֖߂�");
	print qq|</td><td>|;
	&backlink("home","");
	print qq|</td></tr></table>\n|;
}

# ---------------------------------------------------------- #
# ���ԗ\��\�i�J�����_�[�\��\�j�̃��R�[�h�쐬�t�H�[���̕\�� #
# ---------------------------------------------------------- #
sub editcalendardate
{
	my $dispyear = shift @_;
	my $dispmonth= shift @_;
	my $dispday  = shift @_;

	# �w����̗\��𓾂�
	&calendarpackage::loadcalendar( $dispyear, $dispmonth, $calendarfile );		# ��Ƀf�[�^�t�@�C����ǂ܂���
	my $alreadystring = &calendarpackage::getdayschedule( $dispyear, $dispmonth, $dispday );

	# �\��𕪉�
	my @yoteis;
	($yoteis[0], $yoteis[1], $yoteis[2]) = split(/<>/, $alreadystring);

	# �\��̒��g����HTML�^�O���f�R�[�h
	@yoteis = &decodehtmltags(@yoteis);

	# ���ԗ\��\�p�V�[��(��^��)�̓ǂݍ���
	&loadseals();

	# �R���\�[���t�H�[���̕\��
	&loaddata('\[FormTop\]','\[/FormTop\]');
	print qq|<input type="hidden" name="mode" value="recorddate">\n|;
	print qq|<input type="hidden" name="edityear"  value="$dispyear">\n|;
	print qq|<input type="hidden" name="editmonth" value="$dispmonth">\n|;
	print qq|<input type="hidden" name="editday" value="$dispday">\n|;

	print qq|<table class="inputtable">\n|;
	print qq|<tr><th colspan="2">$dispyear�N $dispmonth�� $dispday�� �̗\\\��</th></tr>|;

	print qq|<tr><td>�\\\����e1</td><td>\n|;
	print qq|���ށF<select name="seal1">|; &showseals(); print qq|</select><br>\n|;
	print qq|���e�F<input type="text" name="schedule1" value="$yoteis[0]" style="width: 21em;"><br>\n|;
	print qq|�����F<input type="time" name="timestart1" value="$timestart[0]"> �` <input type="time" name="timeend1" value="$timeend[0]"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|<tr><td>�\\\����e2</td><td>\n|;
	print qq|�I���F<select name="seal2">|; &showseals(); print qq|</select><br>\n|;
	print qq|�C�ӁF<input type="text" name="schedule2" value="$yoteis[1]" style="width: 21em;"><br>\n|;
	print qq|�����F<input type="time" name="timestart2" value="$timestart[1]"> �` <input type="time" name="timeend2" value="$timeend[1]"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|<tr><td>�\\\����e3</td><td>\n|;
	print qq|�I���F<select name="seal3">|; &showseals(); print qq|</select><br>\n|;
	print qq|�C�ӁF<input type="text" name="schedule3" value="$yoteis[2]" style="width: 21em;"><br>\n|;
	print qq|�����F<input type="time" name="timestart3" value="$timestart[2]"> �` <input type="time" name="timeend3" value="$timeend[2]"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|<tr><td>���l</td><td>\n|;
	print qq|�C�ӁF<input type="text" name="schedule3" value="$yoteis[3]" style="width: 21em;"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|</td></tr>\n|;
	print qq|</table><br>\n|;

	&closeform("���̓��̃f�[�^��ۑ�");
}

# ------------------------------------ #
# ���ԗ\��\�p�V�[��(��^��)�̓ǂݍ��� #
# ------------------------------------ #
sub loadseals
{
	# �t�@�C����ǂ�
	open(IN,"$scheduleseals") || return(-1);
	@seals = <IN>;
	close(IN);
}

# ------------------------------------------------------------ #
# ���ԗ\��\�p�V�[��(��^��)�\���p�v���_�E�����j���[���ڂ̐��� #
# ------------------------------------------------------------ #
sub showseals
{
	my @sealstrings = ("<option value=\"\"> </option>");

	foreach my $line (@seals) {
		# ���̎Q�Ƃ֕ϊ�(Ver2.20�ǉ�)
		$line =~ s/</&lt;/g;
		$line =~ s/>/&gt;/g;
		$line =~ s/"/&quot;/g;
		# �\���p�z��ɒǉ�
		push ( @sealstrings, qq|<option value="$line">$line</option>| );
	}

	print @sealstrings;
}

# ------------------------------------------------------ #
# ���ԗ\��\�i�J�����_�[�\��\�j�̓��t�I���t�H�[���̕\�� #
# ------------------------------------------------------ #
sub editcalendarrecorddisp
{
	my $dispyear = shift @_;
	my $dispmonth= shift @_;
	my $selected = shift @_;
	my @std;

	# �e���̍ŏI�����X�g�𓾂�
	my @lastdaylist = &calendarpackage::getlastdaylist($dispyear);

	# selected�����̑}��
	if(( $selected > 0 ) && ( $selected <= $lastdaylist[$dispmonth-1] )) {
		# �w�肪�����
		$std[$selected-1] = " selected";
	}

	# �w�茎�̓��t���X�g���쐬
	my @selectdays;
	for( my $loop=1 ; $loop<=$lastdaylist[$dispmonth-1] ; $loop++ ) {
		# �w�茎�̓��t�����[�v
		push ( @selectdays , qq|<option value="$loop"$std[$loop-1]>$loop</option>| );
	}

	# �R���\�[���t�H�[���̕\��
	&loaddata('\[FormTop\]','\[/FormTop\]');
	print qq|<input type="hidden" name="mode" value="editcalendardate">\n|;
	print qq|<input type="hidden" name="edityear"  value="$dispyear">\n|;
	print qq|<input type="hidden" name="editmonth" value="$dispmonth">\n|;

	print qq|$dispyear�N $dispmonth��\n|;

	print qq|<select name="editday">|;
	print @selectdays;
	print qq|</select> ��\n|;

	&closeform("���̓��̃f�[�^��ҏW");

}

# ---------------------------------------------------------- #
# ���ԗ\��\�i�J�����_�[�\��\�j�̕\�����w��p�t�H�[���̐��� #
# ---------------------------------------------------------- #
sub showchangecalendarform
{
	my $dispyear = shift @_;
	my $dispmonth= shift @_;

	# �R���\�[���p�t�H�[���̐���
	my @selectyears;
	my @selectmonths;

	# �N�I�����̍쐬
	my @years = ( $dispyear-5,$dispyear-4,$dispyear-3,$dispyear-2,$dispyear-1,
				  $dispyear,
				  $dispyear+1,$dispyear+2,$dispyear+3,$dispyear+4,$dispyear+5 );
	push( @selectyears, qq|<option value="$years[0]">$years[0]</option>| );	# 5�N�O
	push( @selectyears, qq|<option value="$years[1]">$years[1]</option>| );	# 4�N�O
	push( @selectyears, qq|<option value="$years[2]">$years[2]</option>| );	# 3�N�O
	push( @selectyears, qq|<option value="$years[3]">$years[3]</option>| );	# 2�N�O
	push( @selectyears, qq|<option value="$years[4]">$years[4]</option>| );	# ��N
	push( @selectyears, qq|<option value="$years[5]" selected>$years[5]</option>| );	# ���N
	push( @selectyears, qq|<option value="$years[6]">$years[6]</option>| );	# ���N
	push( @selectyears, qq|<option value="$years[7]">$years[7]</option>| );	# �ė��N
	push( @selectyears, qq|<option value="$years[8]">$years[8]</option>| );	# 3�N��
	push( @selectyears, qq|<option value="$years[9]">$years[9]</option>| );	# 4�N��
	push( @selectyears, qq|<option value="$years[10]">$years[10]</option>| );	# 5�N��
	# ���I�����̍쐬
	my @months = ("","","","","","","","","","","","");
	$months[$dispmonth-1] = "selected";
	for( my $loop=1 ; $loop<=12 ; $loop++ ) {
		# 12������
		push ( @selectmonths , qq|<option value="$loop" $months[$loop-1]>$loop</option>| );
	}

	# �R���\�[���t�H�[���̕\��
	&loaddata('\[FormTop\]','\[/FormTop\]');
	print qq|<input type="hidden" name="mode" value="editcalendar">\n|;
	print qq|<select name="edityear">|;
	print @selectyears;
	print qq|</select>\n|;
	print qq|<select name="editmonth">|;
	print @selectmonths;
	print qq|</select>\n|;
	&closeform("���̌��̃f�[�^��ҏW");

}

# ---------------------------------------- #
# ���ԗ\��\�i�J�����_�[�\��\�j�̈ꊇ�폜 #
# ---------------------------------------- #
sub calendardelete
{
	# ���ԗ\��\�̈ꊇ�폜�i�挎�܂ł̑S�f�[�^���폜�j
	my $year  = $cedityear;
	my $month = $ceditmonth;

	my $delcount=0;

	# �t�@�C����ǂ�
	open(IN,"$calendarfile") || &errorexit("���ԗ\\\��t�@�C�� $calendarfile ���ǂ߂܂���ł����B");
	my @allshcedule = <IN>;
	close(IN);

	# "�挎"�̐��l�𐶐�
	my $lastmonth = $year * 12 + $month - 1;

	# ��������
	open(OUT,"> $calendarfile") || &errorexit("���ԗ\\\��t�@�C�� $calendarfile ���������݃��[�h�ŊJ���܂���ł����B");
	foreach my $line (@allshcedule) {
		# �f�[�^�𕪊�
		my ( $ry,$rm,undef ) = split(/\//, ((split(/,/, $line))[0]) );
		# ���̃f�[�^�̌��̐��l�𐶐�
		my $thismonth = $ry * 12 + $rm;

		# �������r
		if( $lastmonth < $thismonth ) {
			# �폜�Ώۍs�łȂ���Ώ���
			print OUT "$line";
		}
		else {
			# �폜�����J�E���g
			$delcount++;
		}
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>$delcount�̍��ڂ��폜���܂����B</p>|;

	# �߂�t�H�[����\��
	&backlink("calender","���ԗ\\\��\\\�ɖ߂�");

	&loaddata('\[Foot\]','\[/Foot\]');

}






# ---------------------- #
# �t�@�C���X�V������Ԃ� #
# ---------------------- #
sub get_timestamp
{
	my $filename = shift @_;

	# �t�@�C���X�V�����𓾂�
	my $writetime = (stat($filename))[9];

	# �����v�f�ɕ�������
	my ($sec,$min,$hour,$mday,$month,$year) = (localtime($writetime))[0,1,2,3,4,5];
	$year  = $year + 1900;
	$month = $month + 1;

	# �������Ԃ�
	return ("$year/$month/$mday $hour:$min:$sec");
}

# ---------------------------- #
# �X�N���v�g���f�[�^�̓ǂݏo�� #
# ---------------------------- #
sub loaddata
{
	my $starttag = shift @_;
	my $endtag = shift @_;

	my $insflag = 0;

	foreach my $line(@datahtml) {

		# 1�s���T��
		if( $line =~ m/^$endtag/i ) {
			# �I���_��������o�͒��~
			$insflag = 0;
			# ���[�v�����������
			last;
		}

		if( $insflag == 1 ) {
			# �Y���f�[�^�Ȃ�o�́i�u���L�[���[�h��ϊ����Ă���o�́j
			print &replacekeys($line);
		}
		if( $line =~ m/^$starttag/i ) {
			# �J�n�_��������o�͊J�n
			$insflag = 1;
		}
	}
}

sub replacekeys
{
	my $line = shift @_;

	$encusrpw = qq|<input type="hidden" name="encpw" value="$encupw">|;

	my $modifyweekly   = &get_timestamp($weeklyfile);
	my $modifycalendar = &get_timestamp($calendarfile);
	my $modifylongly   = &get_timestamp($longfile);

	$line =~ s/CSSFILENAME/$cssfile/;
	$line =~ s/CGINAME/$thiscgi/;
	$line =~ s/DEMONSTRATIONMESSAGE/$demomsg/;
	$line =~ s/LOGINMESSAGES/$loginmsg/;
	$line =~ s/ENCORDEDUSERPASSWORD/$encusrpw/;

	$line =~ s/MODIFYTIME-WEEKLY/$modifyweekly/;
	$line =~ s/MODIFYTIME-CALENDAR/$modifycalendar/;
	$line =~ s/MODIFYTIME-LONGLY/$modifylongly/;

	return $line;
}

# ---------------- #
# �߂郊���N���쐬 #
# ---------------- #
sub backlink
{
	my $linkto = shift @_;
	my $button = shift @_;

	# ���w�肾������f�t�H���g����
	if( $linkto eq "" ) {	$linkto = "";	}
	if( $button eq "" ) {	$button = "��ƃ��j���[�ɖ߂�";	}

	# �\��
	print qq|<form action="$thiscgi" method="POST">\n|;
	print qq|$encusrpw\n|;
	print qq|<input type="hidden" name="mode" value="$linkto">\n|;
	print qq|<input type="submit" value="$button">\n|;
	print qq|</form>\n|;
}

# -------------- #
# ����t�H�[�� #
# -------------- #
sub closeform
{
	my $button = shift @_;

	# ���w�肾������f�t�H���g����
	if( $button eq "" ) {	$button = "���s";	}

	# �\��
	print qq|$encusrpw\n|;
	print qq|<input type="submit" value="$button">\n|;
	print qq|</form>\n|;
}

# -------------------------------------- #
# �z�񒆂̑S�����񂩂�HTML�^�O���f�R�[�h #
# -------------------------------------- #
sub decodehtmltags
{
	foreach my $line (@_) {
		# HTML�^�O���f�R�[�h
		$line =~ s/</&lt;/g;
		$line =~ s/>/&gt;/g;
		$line =~ s/\"/&quot;/g;
		# ���s������
		$line =~ s/\r//g;
		$line =~ s/\n//g;
	}

	return @_;
}









# ------------------------------ #
# �v���I�ł͂Ȃ��G���[���b�Z�[�W #
# ------------------------------ #
sub errorback
{
	my $msg = shift @_;

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	print qq|<p><span class="error">$msg</p>\n|;
	print qq|<form><input type="button" value="���O�̉�ʂɖ߂�" onClick="history.back();"></form>|;
	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------- #
# �G���[���b�Z�[�W #
# ---------------- #
sub errorexit
{
	$msg = shift @_;

	print qq|<html lang="ja"><head><title>Fumy Teacher's Schedule Board ERROR</title></head><body>\n|;
	print qq|<div style="background-color:red; color:#fffff0; font-weight:bold; font-family:Arial,sans-serif; padding:1px;">Fumy Teacher's Schedule Board CGI Error! </div><br>\n|;
	print qq|<div style="font-size: smaller;">�G���[���e�F</div>\n|;
	print qq|<div style="border:1px dotted blue; padding:1em;">$msg</div>\n|;
	print qq|<div style="text-align: right;"><form><input type="button" value="�߂�" onClick="history.back();"></form></div>|;
	print qq|</body></html>\n|;

	exit;
}



exit;

__END__

[Head]
<!DOCTYPE html>
<html lang="ja">
<head>
	<meta http-equiv="Content-Type"	content="text/html; charset=Shift_JIS">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>���h�c�\��\ - ADMIN MODE</title>
	<link rel="stylesheet" type="text/css" href="CSSFILENAME">
</head>
[/Head]
[BodyTop]
<body>
<h1>�X�P�W���[���ҏW�p�l�� <span class="appname"> - ���h�c�\��\ (Ver 2.3.0)</span></h1>
<div class="main">
DEMONSTRATIONMESSAGE
[/BodyTop]
[FormTop]
<form action="CGINAME" method="POST">
[/FormTop]
[FormBottom]
	ENCORDEDUSERPASSWORD
	<input type="submit" value="�ҏW���e��ۑ�">
	<input type="button" value="�ۑ������ɖ߂�" onClick="history.back();">
</form>
[/FormBottom]
[Login]
<p class="login">LOGINMESSAGES</p>
<div class="login">
	<form action="CGINAME" method="POST">
		<input type="password" name="pw">
		<input type="hidden" name="mode" value="home">
		<input type="submit" value="���O�C��">
	</form>
	<p class="notice">�p�X���[�h��Y�ꂽ�ꍇ�F</p>
	<ul class="notice">
		<li>�y�p�X���[�h�Œ�Őݒu�����ꍇ�zCGI�̃\�[�X��`���΃p�X���[�h��������܂��B</li>
		<li>�y�p�X���[�h�ύX�\�Őݒu�����ꍇ�z�p�X���[�h�i�[�t�@�C���̒��g������ۂɂ��ăA�b�v���[�h���������ƂŁA�V�����p�X���[�h����邱�Ƃ��ł��܂��B</li>
	</ul>
</div>
[/Login]
[Foot]
</div>
</body>
</html>
[/Foot]
�����p�x

��p�x��
[First]
<p class="title">��Ɠ��e��I�����ĉ������B</p>
<form action="CGINAME" method="POST">
	<table class="menudesign">
	<tr><td><input type="radio" name="mode" value="weekly"   id="mw"><label for="mw">1�T�Ԃ̔ėp�\��\��ҏW</label></td><td><span class="note">�i�ŏI�X�V�F MODIFYTIME-WEEKLY�j</span></td></tr>
	<tr><td><input type="radio" name="mode" value="calender" id="cd" checked><label for="cd">���ԗ\��\�i�J�����_�[�\��\�j��ҏW</label></td><td><span class="note">�i�ŏI�X�V�F MODIFYTIME-CALENDAR�j</span></td></tr>
	<tr><td><input type="radio" name="mode" value="long"     id="lg"><label for="lg">�����\���ҏW</label></td><td><span class="note">�i�ŏI�X�V�F MODIFYTIME-LONGLY�j</span></td></tr>
	<tr><td><input type="radio" name="mode" value="cpw"      id="cp"><label for="cp">�p�X���[�h��ύX</label></td><td></td></tr>
	</table>
	<br>
	ENCORDEDUSERPASSWORD
	<input type="submit" value="�I��������Ƃ����s">
</form>
[/First]

[ChangePW]
<p class="title">�p�X���[�h��ύX���܂��B���݂̃p�X���[�h�ƁA��]����V�����p�X���[�h����͂��ĉ������B</p>
<form action="CGINAME" method="POST">
	<input type="hidden" name="mode" value="dochangepw">
	<table class="menudesign">
		<tr><td>���݂̃p�X���[�h�F</td><td><input type="password" name="nowpw"></td></tr>
		<tr><td>�V�����p�X���[�h�F</td><td><input type="password" name="newpw"></td></tr>
	</table>
	<br>
	<input type="submit" value="�p�X���[�h��ύX">
	<input type="button" value="�߂�" onClick="history.back();">
	</table>
	ENCORDEDUSERPASSWORD
</form>
<p><span class="note">���p�X���[�h�͈Í������ĕۑ�����܂��B�Ǘ��҂ɂ���ǂ͂ł��܂���̂ŁA�Y��Ȃ��悤�ɒ��ӂ��ĉ������B</span></p>
[/ChangePW]

[MakePW]
<p class="title">�悤�����AFumy Teacher's Schedule Board�ցI<br>�܂��A<strong>���O�C���p�̃p�X���[�h��ݒ�(�o�^)</strong>���܂��B��]����p�X���[�h�����L�ɓ��͂��ĉ������B</p>
<form action="CGINAME" method="POST">
	<input type="hidden" name="mode" value="dochangepw">
	��]����p�X���[�h�F</td><td><input type="password" name="newpw"><br>
	<br>
	<input type="submit" value="�p�X���[�h��o�^">
</form>
<p><span class="note">���p�X���[�h�͈Í������ĕۑ�����܂��B�Ǘ��҂ɂ���ǂ͂ł��܂���̂ŁA�Y��Ȃ��悤�ɒ��ӂ��ĉ������B<br>���p�X���[�h��0�����ɂ͂ł��܂���B</span></p>
[/MakePW]
