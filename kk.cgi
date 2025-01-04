#!/usr/local/bin/perl
use CGI;

require 'dbAccess.pl';

my $IsAdmin = false;
$DIR		= './resheet/';		#�摜�ۑ��t�H���_
$FILE		= './kaikei.dat';	#�����ۑ��t�@�C��
$MAX		= 50;				#�ۑ������i�����E�摜�j
$VIEW		= 10;				#�P�y�[�W�̕\������
$IMGMAX		= 20 * 1000;		#�摜�T�C�Y����(�o�C�g)
$TEXTMAX	= 1000;				#�{�������������i�S�p�j
$NAMEMAX	= 10;				#���O�����������i�S�p�j
$TITLEMAX	= 20;				#�薼�����������i�S�p�j
$PASSWORD	= '1234';			#�폜�p�p�X���[�h
$time		= time;
$RunMode	= "";


# ���t�@�C����
$configfile = "config.txt";

# �c�����i�[�t�@�C����
$memberfile = "member.txt";

my $FORM;
my $startym = "";	# �\���J�n�N���̕ێ�
my $gCurYY = "";	# �\���N�̕ێ�
my $gCurMM = "";	# �\�����̕ێ�
my $recno;			# ���R�[�h�ԍ�
my $gNendo = "";	# �\���N�N�x�̕ێ�
my $DebugReq;

# ���t�@�C�����J��
open(IN,"$configfile") || &errorexit("���t�@�C�����ǂ߂܂���B\n");
my @records = <IN>;
close(IN);
my $Hanmei = @records[0];

#�t�H�[���f�[�^��荞��
if($ENV{'REQUEST_METHOD'} eq 'POST') {
	splitPost();	#�X�V�v��
}
else {
	splitGet();		#�y�[�W�؂�ւ�
}

#�N�b�L�[����p�X���[�h���擾
foreach $pair (split(/;\s*/, $ENV{'HTTP_COOKIE'})) {
    my    ($name, $cookie) = split(/=/, $pair);
    if(($name eq "syobopass") && ($cookie eq "kaikei")) {
		$IsAdmin = true;
		last;
	}
}


if($RunMode eq "NewKaikei") {
	NewKaikei();
}
elsif($RunMode eq "ShowKaikei") {
	ShowKaikei();
}
elsif($RunMode eq "EditKaikei") {
	EditKaikei();
}
elsif($RunMode eq "write") {
	writeData();
}
elsif($RunMode eq "delete") {
	writeData();
}
else {
	ShowDetail();
}

print "<hr>";
if($IsAdmin eq true) {
    print qq|<a href="kk.cgi?&mode=NewKaikei">�V�K�ǉ�</a><br>\n|;
}
print <<END;                                #HTML�o��
    <a href="kk.cgi">�{�N�x��v�ꗗ</a><br>\n
    </body>
    </html>
END

exit;


#��v�̐V�K�ǉ�
sub NewKaikei {
	HeaderOut("��v�V�K�o�^");
	InputKaikei();	#�V�K�o�^
}

#��v�̐V�K�ǉ�
sub EditKaikei {
	HeaderOut("��v���ύX");
	InputKaikei();	#�V�K�o�^
}

#����N������N�x���ł��邩�𔻒�
#	�����F"YYYYMM"�`���N��
sub	isNendIn
{
	my $startym = shift @_;			# �\���N 
	my $startyear	= substr($startym,0,4);
	my $startmonth	= substr($startym,4,2);		# �\���J�n�N���𕪊�
	if($startmonth lt "04") {	# �S���O�Ȃ�ΑO�N�x�Ƃ���
		$startyear--;
	}
	if($gCurYY eq $startyear) {
		return TRUE;
	}
	return FALSE;
}

#���ו\��
sub ShowDetail {

	HeaderOut("�N�ԉ�v��");

	#�N�x�̃h���b�v�_�E���쐬
	open(IN,"$memberfile") || &errorexit("�����o�[�t�@�C�����ǂ߂܂���B\n");
	my @members = <IN>;
	close(IN);

	#$gNendo�N�x
	print qq|<form name="formNendoList" action="">|;
	print qq|<select id="cmbYear" name="rdYear" onchange="location.href=value;"></option>|;
	my $ix = 0;
	foreach my $member ( @members ) {
		my $rdNendo	=substr($member,0,4);
		my $linkUrl	= "kk.cgi?start=$rdNendo" . "01";
		print qq|<option value="$linkUrl">$rdNendo</option>|;
		if($gCurYY eq $rdNendo) {
			print qq|<script>var obj = document.getElementById("cmbYear");|;
			print qq|obj.selectedIndex = $ix;</script>|;
		}
		$ix++;
	}
	print qq|</select>�N�x�̉�v\n<br><hr>|;
	print qq|</form>|;


	# �t�@�C�����J��
	open(IN,"$FILE") || &errorexit("��v�t�@�C�����ǂ߂܂���B\n");
	@records = <IN>;
	close(IN);

	@records = sort {$a <=> $b} @records;
	my $InSum = 0,$OutSum = 0,$Zankin = 0;

	# HTML�\��(TABLE HEAD)
	print qq|<table border=1><tr><td>���t</td><td>����</td><td>����</td><td>�x�o</td><td>�c��</td></tr>\n|;

	# ���e�ʂɕ���
	foreach $record (@records) {
		# ���s���폜
		$record =~ s/\r//g;
		$record =~ s/\n//g;
		
		#�v�f����
		my ($rdDate, $rdNo, $rdKubun, $rdGaku, $rdTitle , $rdMemo) = split(/<>/, $record);
		if($rdDate eq "") {
			next;
		}
		if(isNendIn($rdDate) eq TRUE) {
			# �N�x���Ȃ�Ε\������
			my $rdYear	= substr($rdDate,0,4);
			my $rdMonth= substr($rdDate,4,2);
			my $rdDay= substr($rdDate,6,2);
			print qq|<tr><td>$rdYear/$rdMonth/$rdDay</td><td><a href="kk.cgi?&mode=ShowKaikei&start=$rdYear$rdMonth&recno=$rdNo">$rdTitle</a></td>|;
			if($rdKubun eq "1") {	#������
				$InSum = $InSum + $rdGaku;
				$Zankin = $Zankin + $rdGaku;
				$prtGak = $rdGaku;	$prtGak =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				$prtZan = $Zankin;	$prtZan =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<td align="right">$prtGak</td><td>�@</td><td align="right">$prtZan</td></tr>\n|;
			}
			else {	#�x�o��
				$OutSum = $OutSum + $rdGaku;
				$Zankin = $Zankin - $rdGaku;
				$prtGak = $rdGaku;	$prtGak =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				$prtZan = $Zankin;	$prtZan =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<td>�@</td><td align="right">$prtGak</td><td align="right">$prtZan</td></tr>\n|;
			}
		}
	}
	#�����v�Z���Ȃ��̂Œ��ڕҏW
	$InSum	=~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
	$OutSum	=~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
	$Zankin	=~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
	print qq|<tr><td>�@</td><td><b>���v</b></td><td><b>$InSum</b></td><td><b>$OutSum</b></td><td><b>$Zankin</b></td></tr></table><br>\n|;
}

#���ו\��
sub ShowKaikei {


	# �t�@�C�����J��
	open(IN,"$FILE") || &errorexit("��v�t�@�C�����ǂ߂܂���B\n");
	@records = <IN>;
	close(IN);

	# ���e�ʂɕ���
	foreach $record (@records) {

		#�v�f����
		my ($rdDate, $rdNo, $rdKubun, $rdGaku, $rdTitle , $rdMemo) = split(/<>/, $record);
		if($rdNo eq $recno) {

			# �Y���f�[�^�Ȃ�Ε\������
			my $rdYear	= substr($rdDate,0,4);
			my $rdMonth= substr($rdDate,4,2);
			my $rdDay= substr($rdDate,6,2);
			HeaderOut("��v����");
			
			print qq|<table border=1>\n|;
			print qq|<tr><td>���t :</td><td> $rdYear�N $rdMonth�� $rdDay��</td></tr>\n|;
			
			print qq|<tr><td>���� :</td><td> $rdTitle</td></tr>\n|;
			if($rdKubun eq "1") {	#������
				$rdGaku =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<tr><td>���� : </td><td>$rdGaku</td></tr>\n|;
			}
			else {	#�x�o��
				$rdGaku =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<tr><td>�x�o : </td><td>$rdGaku</td></tr>\n|;
			}
			print qq|<tr><td>Memo : </td><td>$rdMemo</td></tr>\n|;

			#�C���[�W�t�@�C���̑��݃`�F�b�N
			my @exts = (".jpg",".jpeg",".gif",".png");
			foreach my $imgExt (@exts) {
				$InameName = $DIR . $rdNo . $imgExt;
				if (-e $InameName) {
					print qq|<tr><td>���V�[�g</td><td><img src=$InameName alt="���V�[�g�摜" width="640" border="0"></td></tr>\n|;
					last;
				} 
			}
			print qq|</table><br>|;
			if($IsAdmin eq true) {
				print qq|<a href="kk.cgi?&mode=EditKaikei&start=$rdYear$rdMonth&recno=$rdNo">��v���ҏW</a>|;
			}
		}
	}
}

sub HeaderOut 
{
my $title = shift @_;			# ���o������ 
print qq(Content-type: text/html; charset=Shift_JIS\n\n);
print <<END;                                #HTML�o��
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
	<html>
	<head>
	<title>$title</title>
	<style type="text/css">
	<!-- 
		body        { padding:10px 5%; background:#efe }
		form        { margin:0px; text-align:left }
		h1        { margin:0px; font-size:20px }
		img        { margin:10px 20px }
		hr        { height:10px; color:#9c9; background:#9c9; border-top:2px solid #393 }
		textarea    { width:80% }
		.err        { color:#f33; font-weight:bolder; text-align:center }
	//-->
	</style>
	</head>
	<body>
	<h1>$title</h1>
	<hr>
END
}

sub InputKaikei
{
	my $InOut = 0;	# �����l�͎����ł��x�o�ł��Ȃ���ԂƂ���
	my $CurRecord="";
	my $MaxRecno=0;
	
	# �t�@�C�����J��
	open(IN,"$FILE") || &errorexit("��v�t�@�C�����ǂ߂܂���B\n");
	@records = <IN>;
	close(IN);

	#�ǂݍ��ݗv�f
	my ($rdDate, $rdNo, $rdInOut, $rdGaku, $rdTitle , $rdMemo, $rdImg);

	# ���e�ʂɕ���
	foreach $record (@records) {
		#�v�f����
		($rdDate, $rdNo, $rdInOut, $rdGaku, $rdTitle , $rdMemo, $rdImg) = split(/<>/, $record);
		if($recno eq "") {
			next;
		}
		if($rdNo eq $recno) {
			$MaxRecno = -1;
			last;
		}
		if($MaxRecno lt $rdNo) {
			$MaxRecno = $rdNo;	#�V�K�p�ɍő僌�R�[�h�ԍ����擾
		}
	}
	if($MaxRecno >= 0) {	#������Ȃ��ꍇ�͐V�K���R�[�h�Ƃ���
		# localtime �́@($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)�ɕ��������
		my ($NewDD,$NewMM,$NewYY) = (localtime(time))[3,4,5];	
		$NewYY   =	sprintf("%04d",$NewYY + 1900);
		$NewMM   =	sprintf("%02d",$NewMM + 1);
		$NewDD   =	sprintf("%02d",$NewDD);
		$rdDate  =	sprintf("%04d%02d%02d",$NewYY,$NewMM,$NewDD);
		$rdNo	 =	sprintf("%04d",$MaxRecno);
		$rdInOut =	"2";	#�x�o
		$rdGaku  =  0;
		$rdTitle =  "-------";
		$rdMemo  = 	"";
		$rdImg   = 	"";
	}
	my $rdYear	= substr($rdDate,0,4);
	my $rdMonth	= substr($rdDate,4,2);
	my $rdDay	= substr($rdDate,6,2);
	
	#*===========================*
	#	FORM�쐬
	#*===========================*
	print qq|<form action="$ENV{'SCRIPT_NAME'}" method="POST" enctype="multipart/form-data">\n|;
	#print qq|<form action="$ENV{'SCRIPT_NAME'}" method="POST">\n|;

	#�N�x�̃h���b�v�_�E���쐬
	print qq|���t�F<select id="rdYear" name="rdYear">|;
	my $ix = 1;
	my $strTemp;
	for( $ix=2017;$ix<=2029;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|<option value="$strTemp"|;
		if($rdYear eq $strTemp) {
			print qq| selected|;
		}
		print qq|>$strTemp</option>|;
	}
	print qq|</select>�N\n |;

	#���x�̃h���b�v�_�E���쐬
	#print qq|<input type="text" name="rdMonth" value="$rdMonth">��|;
	print qq|<select id="rdMonth" name="rdMonth">|;
	for( $ix=1;$ix<=12;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|<option value="$strTemp"|;
		if($rdMonth eq $strTemp) {
			print qq| selected|;
		}
		print qq|>$strTemp</option>|;
	}
	print qq|</select>��\n |;
	
	#���̃h���b�v�_�E���쐬
	#print qq|<input type="text" name="rdDay" value="$rdDay">��<br>|;
	print qq|<select id="rdDay" name="rdDay">|;
	my $strTemp;
	for( $ix=1;$ix<=31;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|<option value="$strTemp"|;
		if($rdDay eq $strTemp) {
			print qq| selected|;
		}
		print qq|>$strTemp</option>|;
	}
	print qq|</select>��<br><br>\n|;

	print qq|<input type="radio" name="InOut" value="1"\n|;
	if($rdInOut eq 1) {
		print qq| checked=\"checked\"\n|;
	};
	print qq|>�����@\n|;

	print qq|<input type="radio" name="InOut" value="2"\n|;
	if($rdInOut eq 2) {
		print qq| checked=\"checked\"\n|;
	};
	print qq|>�x�o<br>\n|;

	print qq|���ځF<input type="text" name="title" size="50" maxlength="$TITLEMAX" value="$rdTitle"><br>\n|;

	print qq|���z�F<input type="text" name="Kingaku" size="30" maxlength="6" value="$rdGaku"><br><br>\n|;
	print qq|���V�[�g�摜�F<br><input type="file" name="img" value="" size="50"><br>\n|;
	print qq|<small>�� JPEG�EGIF��PNG�̂݁i$IMGMAX�o�C�g�ȓ��j</small><br>\n|;
	if(length($rdImg) < 4) {
		print qq|�摜�̓A�b�v����Ă��܂���B<br><br>\n|;
	}
	else {
		print qq|�u $rdImg �v�̉摜���A�b�v����Ă��܂��B<br><br>\n|;
	}
	
	my	$MemoEdit = $rdMemo;
	$MemoEdit	=~ s/<br>/\r\n/g;
	print qq|Memo�F<br><textarea name="Memo" rows="10" cols="30">$MemoEdit</textarea><br>\n|;
	
	print qq|<input type="hidden" name="mode" value="write">\n|;
	print qq|<input type="hidden" name="recno" value="$recno">\n|;
	print qq|<input type="submit" value="�@�������݁@"><br>\n|;
	print qq|</form>|;
}

#==============================================================================�����E�폜
sub    writeData
{
	# �t�@�C�����J��
	open(IN,"$FILE") || &errorexit("�������݁@��v�t�@�C�����ǂ߂܂���B\n");
	@records = <IN>;
	close(IN);

    my $img;
    my $TgtRecNo = $recno,$MaxRecNo,$FineLine=0;
	# ���e�ʂɕ���
	foreach $record (@records) {
		#�v�f����
		my ($rdDate, $rdNo, $rdInOut) = split(/<>/, $record);
		if($TgtRecNo eq "") {
			if($MaxRecNo lt $rdNo) {
				$MaxRecNo = $rdNo;
			}
		}
		else {
			if($rdNo eq $TgtRecNo) {
				last;
			}
		}
		$FineLine = $FineLine + 1;
	}
	if($TgtRecNo eq "") {
		$TgtRecNo =	$MaxRecNo + 1;
	}

    if($RunMode eq 'write') {                    #�f�[�^�ǉ��@
        if($FORM{'Memo'} and length($FORM{'Memo'}) <= $TEXTMAX * 2
                 and length($FORM{'title'}) <= $TITLEMAX * 2    ) {

			$TgtRecNo = sprintf("%04d",$TgtRecNo);
			if($FORM{'img'}) {
				$img = writeImg($TgtRecNo);        #�摜�A�b�v���[�h
			}
			#my ($rdDate, $rdNo, $rdKubun, $rdGaku, $rdTitle , $rdMemo) = split(/<>/, $record);
			# Memo�͕����s�Ȃ̂ŉ��s�R�[�h��u��������
			my $MemoEdit = $FORM{'Memo'};
			$MemoEdit =~ s/\n|\r\n|\r/<br>/g;

			@records[$FineLine] = "$FORM{'rdYear'}$FORM{'rdMonth'}$FORM{'rdDay'}<>$TgtRecNo<>$FORM{'InOut'}<>$FORM{'Kingaku'}<>$FORM{'title'}<>$MemoEdit<>$FORM{'img'}<>\n";
			opendir(DIR, $DIR) or errorexit("�摜�ۑ��t�H���_���J���܂���I�I");
			my    @IMG = readdir(DIR);
			closedir(DIR);
		}
		else {
			errorexit("�������I�[�o�[�܂��͖{�����󔒂ł��I�I");
		}
    }
    elsif($FORM{'mode'} eq 'delete') {                #�f�[�^�폜�@
        if($TgtRecNo ne "") {
            if($FORM{'pass'} eq $PASSWORD) {
                deleteImg($TgtRecNo);        #�摜�폜
                splice @records , $FineLine, 1;    #�����폜
            }
            else {
                errorexit("�폜�p�X���[�h���Ⴂ�܂��I�I");
            }
        }
    }
    
	open(FILE, ">$FILE");                        #�f�[�^��������
	eval{ flock(FILE, 2) };
	print FILE @records;
	close FILE;

	# �X�V/�ǉ������������̂œ��e��\��
	$recno = $TgtRecNo;
	ShowKaikei();
}

#==============================================================================�摜����
sub    writeImg
{
	my $RecNo = shift @_;			# ���R�[�h�ԍ�

	my	$SrcFile = $FORM{'img'};
	my	@filename    = split(/\./, $SrcFile);
	my	$fileExt = $filename[@filename - 1];
	$fileExt =~ tr/A-Z/a-z/;
	my	$PathName = $DIR . $RecNo . '.' . $fileExt;

	if(length($FORM{'img'}) > $IMGMAX) {
        errorexit("�摜�T�C�Y�I�[�o�[�I�I�@�i" . length($FORM{'img'}) . "�o�C�g�j");
    }
    elsif($fileExt eq "jpg" or $fileExt eq "jpeg" or $fileExt eq "gif" or $fileExt eq "png") {
        open(OUT, ">$PathName") or errorexit("�t�@�C���쐬�Ɏ��s���܂����I�I");
		binmode(OUT);
		while(read($SrcFile,$buffer,1024))
		{
			print OUT $buffer;
		}
		close(OUT);
        return $img;
    }
    else {
        errorexit("�����Ȃ��t�@�C���`���ł�");
    }
}

#==============================================================================�摜�폜
sub    deleteImg
{
    my    ($tm, $name, $title, $text, $img) = split(/\t/, $DATA[$_[0]]);
    $img = $DIR . $img;
    if(-e $img) {
        unlink $img;                    
    }
}

# -------------------- #
# POST�p�����[�^�̕��� #
# -------------------- #
sub splitPost
{
	$query = new CGI;
	$RunMode = $query->param('mode');	# �\�����[�h
	$recno = $query->param('recno');	# ���R�[�h�ԍ�
	$FORM{'Memo'}		= $query->param('Memo');
	$FORM{'img'}		= $query->param('img');
	$FORM{'rdYear'}		= $query->param('rdYear');
	$FORM{'rdMonth'}	= $query->param('rdMonth');
	$FORM{'rdDay'}		= $query->param('rdDay');
	$FORM{'InOut'}		= $query->param('InOut');
	$FORM{'Kingaku'}	= $query->param('Kingaku');
	$FORM{'title'}		= $query->param('title');
}

# ------------------- #
# GET�p�����[�^�̕��� #
# ------------------- #
sub splitGet
{
	# ����
	my $querybuffer = $ENV{'QUERY_STRING'};

	# ����
	my @pairs = split(/&/,$querybuffer);
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);
		# ����
		if( $name eq "start" ) {
			$startym = $value;	# �\���J�n�N��
		}
		if( $name eq "mode" ) {
			$RunMode = $value;		# �\�����[�h
		}
		if( $name eq "recno" ) {
			$recno = $value;	# ���R�[�h�ԍ�
		}
	}
	# ���e�`�F�b�N
	if( $startym eq "" ) {
		# localtime �́@($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)�ɕ��������
		($gCurMM,$gCurYY) = (localtime(time))[4,5];	
		$gCurYY = sprintf("%04d",$gCurYY + 1900);
		$gCurMM = sprintf("%02d",$gCurMM + 1);
		$startym = sprintf("%04d%02d",$gCurYY,$gCurMM);

		#print "�ȗ����� [$startym] [$gCurYY] [$gCurMM]<br>";
	}
	else {
		#if( $startym !~ m/^\d\d\d\d-1?\d$/ ) {
		if( $startym !~ m/^\d\d\d\d\d\d$/ ) {
			# ����������Ă���΃G���[
			$startym = "";
			&errorexit("�p�����[�^�̏����Ƀ~�X������܂��B<br>�ustart=201503�v�̂悤�ɁA����4�� + ��2��)�Ŏw�肵�ĉ������B");
		}
		else{
			$gCurYY = substr($startym,0,4);
			$gCurMM = substr($startym,4,2);
			if(( $gCurMM lt "01" ) or ($gCurMM gt "12")) {
				&errorexit("�p�����[�^�̏����Ƀ~�X������܂��B��[$gCurYY]  ��01�`12�̐��l�Ŏw�肵�ĉ������B");
			}
		}
	}
	$gNendo = $gCurYY;
	if($gCurMM < "04") {
		$gNendo--;
	}
}

# ---------------- #
# �G���[���b�Z�[�W #
# ---------------- #
sub errorexit
{
	HeaderOut("�G���[�ł���");
	$msg = shift @_;
	
    print <<"    END";
		<div style="background-color:red; color:#fffff0; font-weight:bold; font-family:Arial,sans-serif; padding:1px;">���܂��\���ł��Ȃ������悤�ł�</div><br>\n
		<div style="font-size: smaller;">�G���[���e�F</div>\n
		<div style="border:1px dotted blue; padding:1em;">$msg</div>\n
		[$DebugReq]<br>
		<div style="text-align: right;"><form><input type="button" value="�߂�" onClick="history.back();"></form></div>
		</body></html>
    END

	exit;
}
