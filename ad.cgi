#!/usr/local/bin/perl

#�Ǘ��җp�̃p�X���[�h	
$HancyoPassw = 'hancyo';	# �ǒ��p
$KaikeiPassw = 'kaikei';	# ��v�p
$ClearPassw = 'clear';		# �Ǘ��҃��[�h���N���A
my $inpPass;
my $IsDebug = false;

# ���͗�����n���ꂽ�l������Γǂݍ���
my $querybuffer = $ENV{'QUERY_STRING'};
my @pairs = split(/&/,$querybuffer);
foreach $pair (@pairs) {
	my ($name, $value) = split(/=/, $pair);
	#if( $name eq "chkdebug" ) {
	#	$IsDebug = true;
	#}
	if( $name eq "syobodan" ) {
		$inpPass = $value;	# �\���J�n�N��
		if($inpPass eq $HancyoPassw) {
			&PasswdOk(0);
		}
		elsif($inpPass eq $KaikeiPassw) {
			&PasswdOk(1);
		} 
		elsif($inpPass eq $ClearPassw) {
			&PasswdOk(9);
		} 
	}
}

#�p�X���[�h���͉��
print qq|Content-type: text/html\n\n\n|;
print qq|<!DOCTYPE html><html lang="ja"><head>\n|;
print qq|<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">\n|;
print qq|<meta name="viewport" content="width=device-width, initial-scale=1">|;
print qq|<TITLE>�Ǘ��җp�p�X���[�h����</TITLE>\n|;
print qq|</HEAD><BODY>�Ǘ��Ґؑփp�X���[�h����͂��Ă��������B<br>�p�X���[�h�̗L�����Ԃ͂P���Ԃł��B<br>\n|;
print qq|<FORM action="">\n|;

#cookie�Ƀf�o�b�O�t���O���������܂�Ă��邩�𔻒�
my $chkDebug = false;
foreach $pair (split(/;\s*/, $ENV{'HTTP_COOKIE'})) {
    my    ($name, $cookie) = split(/=/, $pair);
    if(($name eq "syobodebug") && ($cookie eq "on")) {
		$chkDebug = true;
	}
}
#if($chkDebug eq false) {
#	print qq|<input type="checkbox" name="chkdebug" value="1" >Debug mode|;
#}
#else {
#	print qq|<input type="checkbox" name="chkdebug" value="1" checked="checked">Debug mode|;
#}
print qq|<br><INPUT size="20" type="text" maxlength="20" name="syobodan">\n|;

print qq|<INPUT type="submit" value="���s">\n|;
print qq|</FORM></BODY></HTML>\n|;

exit;



#�摜��\������ׂ̃T�u���[�`��
sub PasswdOk
{
	my $type = shift @_;			# �\���N 

	($secg, $ming, $hourg, $mdayg, $mong, $yearg, $wdayg) = gmtime(time + 3600);
	@mons = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');
	@week = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
	$dt= sprintf("%s\, %02d-%s-%04d %02d:%02d:%02d GMT", $week[$wdayg], $mdayg, $mons[$mong], $yearg+1900, $hourg, $ming, $secg);
	$cpath="/";	#path=$cpath\; 
	#�Ǘ��҃��[�h�̃p�X���[�h��������
	print "Set-Cookie: syobopass=$inpPass; expires=$dt;";
	
	#if($IsDebug eq true) {
	#	#�f�o�b�OON�̃N�b�L�[����������
	#	print "Set-Cookie: syobodebug=on; expires=Tue, 30-Dec-2025 00:00:00 GMT;";
	#}
	#else {
	#	#�f�o�b�OOFF�Ƃ��邽�߂ɉߋ����t�̃N�b�L�[����������
	#	print "Set-Cookie: syobodebug=off; expires=Tue, 29-Dec-2020 00:00:00 GMT;";
	#}	
	print qq|Content-type: text/html\n\n\n|;
	print qq|<!DOCTYPE html><html lang="ja"><head>\n|;
	print qq|<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">\n|;
	print qq|<meta name="viewport" content="width=device-width, initial-scale=1">|;
	
	if(($type eq 0) || ($type eq 9)) {
		$headStr = "�ǒ�";
		if($type eq 9) {
			$headStr = "�ʏ�";
		}
		print qq|<TITLE>$headStr���[�h�ڍs</TITLE>\n|;
		print qq|</HEAD><BODY>$headStr���[�h�ɐݒ肳��܂����B<br>\n|;
		print qq|Date:$dt <br><br>\n|;
		print qq|<a href="sc.cgi">�s���̒ǉ�/�ύX</a><br>\n|;
		print qq|<a href="mm.cgi">�̐��̒ǉ�/�ύX</a><br>\n|;
	}
	if($type eq 1) {
		print qq|<TITLE>��v���[�h�ڍs</TITLE>\n|;
		print qq|</HEAD><BODY>��v���[�h�ɐݒ肳��܂����B<br>\n|;
		print qq|Date:$dt <br><br>\n|;
		print qq|<a href="kk.cgi">����</a>����ǉ�/�ύX���\\�ƂȂ�܂��B\n|;
	}

	if($IsDebug eq true) {
		print qq|<br><br>Debug=ON\n|;
	}
	else {
		print qq|<br><br>Debug=OFF\n|;
	}

	print qq|</BODY></HTML>\n|;

	exit;
}
