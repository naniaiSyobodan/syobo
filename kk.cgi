#!/usr/local/bin/perl
use CGI;

require 'dbAccess.pl';

my $IsAdmin = false;
$DIR		= './resheet/';		#画像保存フォルダ
$FILE		= './kaikei.dat';	#書込保存ファイル
$MAX		= 50;				#保存件数（書込・画像）
$VIEW		= 10;				#１ページの表示件数
$IMGMAX		= 20 * 1000;		#画像サイズ制限(バイト)
$TEXTMAX	= 1000;				#本文文字数制限（全角）
$NAMEMAX	= 10;				#名前文字数制限（全角）
$TITLEMAX	= 20;				#題名文字数制限（全角）
$PASSWORD	= '1234';			#削除用パスワード
$time		= time;
$RunMode	= "";


# 環境ファイル名
$configfile = "config.txt";

# 団員名格納ファイル名
$memberfile = "member.txt";

my $FORM;
my $startym = "";	# 表示開始年月の保持
my $gCurYY = "";	# 表示年の保持
my $gCurMM = "";	# 表示月の保持
my $recno;			# レコード番号
my $gNendo = "";	# 表示年年度の保持
my $DebugReq;

# 環境ファイルを開く
open(IN,"$configfile") || &errorexit("環境ファイルが読めません。\n");
my @records = <IN>;
close(IN);
my $Hanmei = @records[0];

#フォームデータ取り込み
if($ENV{'REQUEST_METHOD'} eq 'POST') {
	splitPost();	#更新要求
}
else {
	splitGet();		#ページ切り替え
}

#クッキーからパスワードを取得
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
    print qq|<a href="kk.cgi?&mode=NewKaikei">新規追加</a><br>\n|;
}
print <<END;                                #HTML出力
    <a href="kk.cgi">本年度会計一覧</a><br>\n
    </body>
    </html>
END

exit;


#会計の新規追加
sub NewKaikei {
	HeaderOut("会計新規登録");
	InputKaikei();	#新規登録
}

#会計の新規追加
sub EditKaikei {
	HeaderOut("会計情報変更");
	InputKaikei();	#新規登録
}

#西暦年月から年度内であるかを判定
#	引数："YYYYMM"形式年月
sub	isNendIn
{
	my $startym = shift @_;			# 表示年 
	my $startyear	= substr($startym,0,4);
	my $startmonth	= substr($startym,4,2);		# 表示開始年月を分割
	if($startmonth lt "04") {	# ４月前ならば前年度とする
		$startyear--;
	}
	if($gCurYY eq $startyear) {
		return TRUE;
	}
	return FALSE;
}

#明細表示
sub ShowDetail {

	HeaderOut("年間会計報告");

	#年度のドロップダウン作成
	open(IN,"$memberfile") || &errorexit("メンバーファイルが読めません。\n");
	my @members = <IN>;
	close(IN);

	#$gNendo年度
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
	print qq|</select>年度の会計\n<br><hr>|;
	print qq|</form>|;


	# ファイルを開く
	open(IN,"$FILE") || &errorexit("会計ファイルが読めません。\n");
	@records = <IN>;
	close(IN);

	@records = sort {$a <=> $b} @records;
	my $InSum = 0,$OutSum = 0,$Zankin = 0;

	# HTML表示(TABLE HEAD)
	print qq|<table border=1><tr><td>日付</td><td>項目</td><td>収入</td><td>支出</td><td>残金</td></tr>\n|;

	# 内容別に分割
	foreach $record (@records) {
		# 改行を削除
		$record =~ s/\r//g;
		$record =~ s/\n//g;
		
		#要素分割
		my ($rdDate, $rdNo, $rdKubun, $rdGaku, $rdTitle , $rdMemo) = split(/<>/, $record);
		if($rdDate eq "") {
			next;
		}
		if(isNendIn($rdDate) eq TRUE) {
			# 年度内ならば表示する
			my $rdYear	= substr($rdDate,0,4);
			my $rdMonth= substr($rdDate,4,2);
			my $rdDay= substr($rdDate,6,2);
			print qq|<tr><td>$rdYear/$rdMonth/$rdDay</td><td><a href="kk.cgi?&mode=ShowKaikei&start=$rdYear$rdMonth&recno=$rdNo">$rdTitle</a></td>|;
			if($rdKubun eq "1") {	#収入側
				$InSum = $InSum + $rdGaku;
				$Zankin = $Zankin + $rdGaku;
				$prtGak = $rdGaku;	$prtGak =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				$prtZan = $Zankin;	$prtZan =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<td align="right">$prtGak</td><td>　</td><td align="right">$prtZan</td></tr>\n|;
			}
			else {	#支出側
				$OutSum = $OutSum + $rdGaku;
				$Zankin = $Zankin - $rdGaku;
				$prtGak = $rdGaku;	$prtGak =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				$prtZan = $Zankin;	$prtZan =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<td>　</td><td align="right">$prtGak</td><td align="right">$prtZan</td></tr>\n|;
			}
		}
	}
	#もう計算しないので直接編集
	$InSum	=~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
	$OutSum	=~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
	$Zankin	=~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
	print qq|<tr><td>　</td><td><b>合計</b></td><td><b>$InSum</b></td><td><b>$OutSum</b></td><td><b>$Zankin</b></td></tr></table><br>\n|;
}

#明細表示
sub ShowKaikei {


	# ファイルを開く
	open(IN,"$FILE") || &errorexit("会計ファイルが読めません。\n");
	@records = <IN>;
	close(IN);

	# 内容別に分割
	foreach $record (@records) {

		#要素分割
		my ($rdDate, $rdNo, $rdKubun, $rdGaku, $rdTitle , $rdMemo) = split(/<>/, $record);
		if($rdNo eq $recno) {

			# 該当データならば表示する
			my $rdYear	= substr($rdDate,0,4);
			my $rdMonth= substr($rdDate,4,2);
			my $rdDay= substr($rdDate,6,2);
			HeaderOut("会計明細");
			
			print qq|<table border=1>\n|;
			print qq|<tr><td>日付 :</td><td> $rdYear年 $rdMonth月 $rdDay日</td></tr>\n|;
			
			print qq|<tr><td>名目 :</td><td> $rdTitle</td></tr>\n|;
			if($rdKubun eq "1") {	#収入側
				$rdGaku =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<tr><td>収入 : </td><td>$rdGaku</td></tr>\n|;
			}
			else {	#支出側
				$rdGaku =~s/(\d{1,3})(?=(?:\d{3})+(?!\d))/$1,/g;
				print qq|<tr><td>支出 : </td><td>$rdGaku</td></tr>\n|;
			}
			print qq|<tr><td>Memo : </td><td>$rdMemo</td></tr>\n|;

			#イメージファイルの存在チェック
			my @exts = (".jpg",".jpeg",".gif",".png");
			foreach my $imgExt (@exts) {
				$InameName = $DIR . $rdNo . $imgExt;
				if (-e $InameName) {
					print qq|<tr><td>レシート</td><td><img src=$InameName alt="レシート画像" width="640" border="0"></td></tr>\n|;
					last;
				} 
			}
			print qq|</table><br>|;
			if($IsAdmin eq true) {
				print qq|<a href="kk.cgi?&mode=EditKaikei&start=$rdYear$rdMonth&recno=$rdNo">会計情報編集</a>|;
			}
		}
	}
}

sub HeaderOut 
{
my $title = shift @_;			# 見出し文字 
print qq(Content-type: text/html; charset=Shift_JIS\n\n);
print <<END;                                #HTML出力
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
	my $InOut = 0;	# 初期値は収入でも支出でもない状態とする
	my $CurRecord="";
	my $MaxRecno=0;
	
	# ファイルを開く
	open(IN,"$FILE") || &errorexit("会計ファイルが読めません。\n");
	@records = <IN>;
	close(IN);

	#読み込み要素
	my ($rdDate, $rdNo, $rdInOut, $rdGaku, $rdTitle , $rdMemo, $rdImg);

	# 内容別に分割
	foreach $record (@records) {
		#要素分割
		($rdDate, $rdNo, $rdInOut, $rdGaku, $rdTitle , $rdMemo, $rdImg) = split(/<>/, $record);
		if($recno eq "") {
			next;
		}
		if($rdNo eq $recno) {
			$MaxRecno = -1;
			last;
		}
		if($MaxRecno lt $rdNo) {
			$MaxRecno = $rdNo;	#新規用に最大レコード番号を取得
		}
	}
	if($MaxRecno >= 0) {	#見つからない場合は新規レコードとする
		# localtime は　($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)に分解される
		my ($NewDD,$NewMM,$NewYY) = (localtime(time))[3,4,5];	
		$NewYY   =	sprintf("%04d",$NewYY + 1900);
		$NewMM   =	sprintf("%02d",$NewMM + 1);
		$NewDD   =	sprintf("%02d",$NewDD);
		$rdDate  =	sprintf("%04d%02d%02d",$NewYY,$NewMM,$NewDD);
		$rdNo	 =	sprintf("%04d",$MaxRecno);
		$rdInOut =	"2";	#支出
		$rdGaku  =  0;
		$rdTitle =  "-------";
		$rdMemo  = 	"";
		$rdImg   = 	"";
	}
	my $rdYear	= substr($rdDate,0,4);
	my $rdMonth	= substr($rdDate,4,2);
	my $rdDay	= substr($rdDate,6,2);
	
	#*===========================*
	#	FORM作成
	#*===========================*
	print qq|<form action="$ENV{'SCRIPT_NAME'}" method="POST" enctype="multipart/form-data">\n|;
	#print qq|<form action="$ENV{'SCRIPT_NAME'}" method="POST">\n|;

	#年度のドロップダウン作成
	print qq|日付：<select id="rdYear" name="rdYear">|;
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
	print qq|</select>年\n |;

	#月度のドロップダウン作成
	#print qq|<input type="text" name="rdMonth" value="$rdMonth">月|;
	print qq|<select id="rdMonth" name="rdMonth">|;
	for( $ix=1;$ix<=12;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|<option value="$strTemp"|;
		if($rdMonth eq $strTemp) {
			print qq| selected|;
		}
		print qq|>$strTemp</option>|;
	}
	print qq|</select>月\n |;
	
	#日のドロップダウン作成
	#print qq|<input type="text" name="rdDay" value="$rdDay">日<br>|;
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
	print qq|</select>日<br><br>\n|;

	print qq|<input type="radio" name="InOut" value="1"\n|;
	if($rdInOut eq 1) {
		print qq| checked=\"checked\"\n|;
	};
	print qq|>収入　\n|;

	print qq|<input type="radio" name="InOut" value="2"\n|;
	if($rdInOut eq 2) {
		print qq| checked=\"checked\"\n|;
	};
	print qq|>支出<br>\n|;

	print qq|名目：<input type="text" name="title" size="50" maxlength="$TITLEMAX" value="$rdTitle"><br>\n|;

	print qq|金額：<input type="text" name="Kingaku" size="30" maxlength="6" value="$rdGaku"><br><br>\n|;
	print qq|レシート画像：<br><input type="file" name="img" value="" size="50"><br>\n|;
	print qq|<small>※ JPEG・GIFとPNGのみ（$IMGMAXバイト以内）</small><br>\n|;
	if(length($rdImg) < 4) {
		print qq|画像はアップされていません。<br><br>\n|;
	}
	else {
		print qq|「 $rdImg 」の画像がアップされています。<br><br>\n|;
	}
	
	my	$MemoEdit = $rdMemo;
	$MemoEdit	=~ s/<br>/\r\n/g;
	print qq|Memo：<br><textarea name="Memo" rows="10" cols="30">$MemoEdit</textarea><br>\n|;
	
	print qq|<input type="hidden" name="mode" value="write">\n|;
	print qq|<input type="hidden" name="recno" value="$recno">\n|;
	print qq|<input type="submit" value="　書き込み　"><br>\n|;
	print qq|</form>|;
}

#==============================================================================書込・削除
sub    writeData
{
	# ファイルを開く
	open(IN,"$FILE") || &errorexit("書き込み　会計ファイルが読めません。\n");
	@records = <IN>;
	close(IN);

    my $img;
    my $TgtRecNo = $recno,$MaxRecNo,$FineLine=0;
	# 内容別に分割
	foreach $record (@records) {
		#要素分割
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

    if($RunMode eq 'write') {                    #データ追加　
        if($FORM{'Memo'} and length($FORM{'Memo'}) <= $TEXTMAX * 2
                 and length($FORM{'title'}) <= $TITLEMAX * 2    ) {

			$TgtRecNo = sprintf("%04d",$TgtRecNo);
			if($FORM{'img'}) {
				$img = writeImg($TgtRecNo);        #画像アップロード
			}
			#my ($rdDate, $rdNo, $rdKubun, $rdGaku, $rdTitle , $rdMemo) = split(/<>/, $record);
			# Memoは複数行なので改行コードを置き換える
			my $MemoEdit = $FORM{'Memo'};
			$MemoEdit =~ s/\n|\r\n|\r/<br>/g;

			@records[$FineLine] = "$FORM{'rdYear'}$FORM{'rdMonth'}$FORM{'rdDay'}<>$TgtRecNo<>$FORM{'InOut'}<>$FORM{'Kingaku'}<>$FORM{'title'}<>$MemoEdit<>$FORM{'img'}<>\n";
			opendir(DIR, $DIR) or errorexit("画像保存フォルダが開けません！！");
			my    @IMG = readdir(DIR);
			closedir(DIR);
		}
		else {
			errorexit("文字数オーバーまたは本文が空白です！！");
		}
    }
    elsif($FORM{'mode'} eq 'delete') {                #データ削除　
        if($TgtRecNo ne "") {
            if($FORM{'pass'} eq $PASSWORD) {
                deleteImg($TgtRecNo);        #画像削除
                splice @records , $FineLine, 1;    #書込削除
            }
            else {
                errorexit("削除パスワードが違います！！");
            }
        }
    }
    
	open(FILE, ">$FILE");                        #データ書き込み
	eval{ flock(FILE, 2) };
	print FILE @records;
	close FILE;

	# 更新/追加が完了したので内容を表示
	$recno = $TgtRecNo;
	ShowKaikei();
}

#==============================================================================画像書込
sub    writeImg
{
	my $RecNo = shift @_;			# レコード番号

	my	$SrcFile = $FORM{'img'};
	my	@filename    = split(/\./, $SrcFile);
	my	$fileExt = $filename[@filename - 1];
	$fileExt =~ tr/A-Z/a-z/;
	my	$PathName = $DIR . $RecNo . '.' . $fileExt;

	if(length($FORM{'img'}) > $IMGMAX) {
        errorexit("画像サイズオーバー！！　（" . length($FORM{'img'}) . "バイト）");
    }
    elsif($fileExt eq "jpg" or $fileExt eq "jpeg" or $fileExt eq "gif" or $fileExt eq "png") {
        open(OUT, ">$PathName") or errorexit("ファイル作成に失敗しました！！");
		binmode(OUT);
		while(read($SrcFile,$buffer,1024))
		{
			print OUT $buffer;
		}
		close(OUT);
        return $img;
    }
    else {
        errorexit("扱えないファイル形式です");
    }
}

#==============================================================================画像削除
sub    deleteImg
{
    my    ($tm, $name, $title, $text, $img) = split(/\t/, $DATA[$_[0]]);
    $img = $DIR . $img;
    if(-e $img) {
        unlink $img;                    
    }
}

# -------------------- #
# POSTパラメータの分解 #
# -------------------- #
sub splitPost
{
	$query = new CGI;
	$RunMode = $query->param('mode');	# 表示モード
	$recno = $query->param('recno');	# レコード番号
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
# GETパラメータの分解 #
# ------------------- #
sub splitGet
{
	# 結合
	my $querybuffer = $ENV{'QUERY_STRING'};

	# 分解
	my @pairs = split(/&/,$querybuffer);
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);
		# 分解
		if( $name eq "start" ) {
			$startym = $value;	# 表示開始年月
		}
		if( $name eq "mode" ) {
			$RunMode = $value;		# 表示モード
		}
		if( $name eq "recno" ) {
			$recno = $value;	# レコード番号
		}
	}
	# 内容チェック
	if( $startym eq "" ) {
		# localtime は　($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)に分解される
		($gCurMM,$gCurYY) = (localtime(time))[4,5];	
		$gCurYY = sprintf("%04d",$gCurYY + 1900);
		$gCurMM = sprintf("%02d",$gCurMM + 1);
		$startym = sprintf("%04d%02d",$gCurYY,$gCurMM);

		#print "省略日時 [$startym] [$gCurYY] [$gCurMM]<br>";
	}
	else {
		#if( $startym !~ m/^\d\d\d\d-1?\d$/ ) {
		if( $startym !~ m/^\d\d\d\d\d\d$/ ) {
			# 書式が違っていればエラー
			$startym = "";
			&errorexit("パラメータの書式にミスがあります。<br>「start=201503」のように、西暦4桁 + 月2桁)で指定して下さい。");
		}
		else{
			$gCurYY = substr($startym,0,4);
			$gCurMM = substr($startym,4,2);
			if(( $gCurMM lt "01" ) or ($gCurMM gt "12")) {
				&errorexit("パラメータの書式にミスがあります。月[$gCurYY]  は01～12の数値で指定して下さい。");
			}
		}
	}
	$gNendo = $gCurYY;
	if($gCurMM < "04") {
		$gNendo--;
	}
}

# ---------------- #
# エラーメッセージ #
# ---------------- #
sub errorexit
{
	HeaderOut("エラーでした");
	$msg = shift @_;
	
    print <<"    END";
		<div style="background-color:red; color:#fffff0; font-weight:bold; font-family:Arial,sans-serif; padding:1px;">うまく表示できなかったようです</div><br>\n
		<div style="font-size: smaller;">エラー内容：</div>\n
		<div style="border:1px dotted blue; padding:1em;">$msg</div>\n
		[$DebugReq]<br>
		<div style="text-align: right;"><form><input type="button" value="戻る" onClick="history.back();"></form></div>
		</body></html>
    END

	exit;
}
