#!/usr/local/bin/perl

#管理者用のパスワード	
$HancyoPassw = 'hancyo';	# 班長用
$KaikeiPassw = 'kaikei';	# 会計用
$ClearPassw = 'clear';		# 管理者モードをクリア
my $inpPass;
my $IsDebug = false;

# 入力欄から渡された値があれば読み込む
my $querybuffer = $ENV{'QUERY_STRING'};
my @pairs = split(/&/,$querybuffer);
foreach $pair (@pairs) {
	my ($name, $value) = split(/=/, $pair);
	#if( $name eq "chkdebug" ) {
	#	$IsDebug = true;
	#}
	if( $name eq "syobodan" ) {
		$inpPass = $value;	# 表示開始年月
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

#パスワード入力画面
print qq|Content-type: text/html\n\n\n|;
print qq|<!DOCTYPE html><html lang="ja"><head>\n|;
print qq|<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">\n|;
print qq|<meta name="viewport" content="width=device-width, initial-scale=1">|;
print qq|<TITLE>管理者用パスワード入力</TITLE>\n|;
print qq|</HEAD><BODY>管理者切替パスワードを入力してください。<br>パスワードの有効時間は１時間です。<br>\n|;
print qq|<FORM action="">\n|;

#cookieにデバッグフラグが書き込まれているかを判定
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

print qq|<INPUT type="submit" value="実行">\n|;
print qq|</FORM></BODY></HTML>\n|;

exit;



#画像を表示する為のサブルーチン
sub PasswdOk
{
	my $type = shift @_;			# 表示年 

	($secg, $ming, $hourg, $mdayg, $mong, $yearg, $wdayg) = gmtime(time + 3600);
	@mons = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');
	@week = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
	$dt= sprintf("%s\, %02d-%s-%04d %02d:%02d:%02d GMT", $week[$wdayg], $mdayg, $mons[$mong], $yearg+1900, $hourg, $ming, $secg);
	$cpath="/";	#path=$cpath\; 
	#管理者モードのパスワード書き込み
	print "Set-Cookie: syobopass=$inpPass; expires=$dt;";
	
	#if($IsDebug eq true) {
	#	#デバッグONのクッキーを書き込む
	#	print "Set-Cookie: syobodebug=on; expires=Tue, 30-Dec-2025 00:00:00 GMT;";
	#}
	#else {
	#	#デバッグOFFとするために過去日付のクッキーを書き込む
	#	print "Set-Cookie: syobodebug=off; expires=Tue, 29-Dec-2020 00:00:00 GMT;";
	#}	
	print qq|Content-type: text/html\n\n\n|;
	print qq|<!DOCTYPE html><html lang="ja"><head>\n|;
	print qq|<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">\n|;
	print qq|<meta name="viewport" content="width=device-width, initial-scale=1">|;
	
	if(($type eq 0) || ($type eq 9)) {
		$headStr = "班長";
		if($type eq 9) {
			$headStr = "通常";
		}
		print qq|<TITLE>$headStrモード移行</TITLE>\n|;
		print qq|</HEAD><BODY>$headStrモードに設定されました。<br>\n|;
		print qq|Date:$dt <br><br>\n|;
		print qq|<a href="sc.cgi">行事の追加/変更</a><br>\n|;
		print qq|<a href="mm.cgi">体制の追加/変更</a><br>\n|;
	}
	if($type eq 1) {
		print qq|<TITLE>会計モード移行</TITLE>\n|;
		print qq|</HEAD><BODY>会計モードに設定されました。<br>\n|;
		print qq|Date:$dt <br><br>\n|;
		print qq|<a href="kk.cgi">ここ</a>から追加/変更が可能\となります。\n|;
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
