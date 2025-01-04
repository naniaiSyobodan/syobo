#! /usr/bin/perl
use lib qw(./);
use DBI;
use CGI;


##############################require 'syobo_setting.pl';

#vデータベース接続
my $server = "localhost";
my $userName = "kyum";
my $password = "k1lt7Ovl";
my $dbName = "kyum";
my $dbConnect = "DBI:mysql:" . $dbName . ":" . $server;


#対象となる班の指定
my	$HAN_CNT = 11;
my	$gHanNo = "";
my	@HanList = ("分団本部","１区","２区","３区","４区","５区","６区","７区","８区","９区","１０区");	# 分類リスト

my	$gCurYY,$gCurMM;	# 処理対象の年月
my	$gNendo;			# 処理対象の年度(１~３月は年-１となる)
my	$gHanmei = "";

# データベース接続
$dbHandle = DBI->connect($dbConnect, $userName, $password);

# DBに登録されている最少/最大年度を取得する
#サブルーチンの呼び出し側でも意識してリファレンス（例: \$val）を渡す
#my $NendoMin,$NendoMax;
#&GetNenMaxMin(\$NendoMin,\$NendoMax);  # 呼び出し側ではリファレンスを渡す
sub GetNenMaxMin
{
	my $sth = $dbHandle->prepare("select max(Nendo), min(Nendo) from sybo_taisei;");
	my $rv	= $sth->execute;
	@ary = $sth->fetchrow_array;
	
	@_[0] = $ary[1];
	@_[1] = $ary[0];

	$sth->finish;
}

#西暦年月から年度内であるかを判定
#	引数："YYYY-MM-DD"形式年月
sub	isNendIn
{
	my $startym = shift @_;			# 表示年 
	my $startyear	= substr($startym,0,4);
	my $startmonth	= substr($startym,5,2);		# 表示開始年月を分割
	if($startmonth lt "04") {	# ４月前ならば前年度とする
		$startyear--;
	}
	if($gCurYY eq $startyear) {
		return TRUE;
	}
	return FALSE;
}

########################################



# 体制編集用JS

# 環境ファイル名
$configfile = "config.txt";

# 団員名格納ファイル名
$memberfile = "member.txt";

my	$gCurYY,$gCurMM;
my	$query,$mode;

#フォームデータ取り込み
if($ENV{'REQUEST_METHOD'} eq 'POST') {

	$query = new CGI;
	$mode = $query->param('mode');	# 表示モード
	$pmYear	= $query->param('rdYear');	# 年
	
	$gHanNo	= $query->param('hanno');	# 年
	if($gHanNo > 10) {	#範囲外ならば３区とする
		$gHanNo = 3;		
	}
	else {	#指定の本部または班の指定
		$HanBit = 1 << $gHanNo;
		$TargetCheck = "and (TargetFlags & $HanBit) > 0";
		#print qq|DEBUG Select HanNo = $value , $HanBit , $TargetCheck , $Hanmei<br>|;
	}
}
else {
	# パラメータの分解
	# 結合
	my $querybuffer = $ENV{'QUERY_STRING'};

	# 分解
	my @pairs = split(/&/,$querybuffer);
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);
		# 分解
		if( $name eq "start" ) {
			my @ymd = split(/-/,$value);
			$gNendo = $ymd[0];	# 表示開始年月
		}
		if( $name eq "mode" ) {
			$mode = $value;		# 表示モード
		}
		if( $name eq "HanNo" ) {
			$gHanNo = $value;	# 班番号
		}
	}
}


# 内容チェック
if(( $gNendo eq "" ) || ($gNendo !~ m/^\d\d\d\d$/ )) {
	# localtime は　($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)に分解される
	($gCurMM,$gCurYY) = (localtime(time))[4,5];	
	$gCurYY = sprintf("%04d",$gCurYY + 1900);
	$gCurMM = sprintf("%02d",$gCurMM + 1);
	
	$gNendo = $gCurYY;
	if($gCurMM < "04") {
		$gNendo--;
	}
}

# ヘッダ
print qq|
<!DOCTYPE html>
<html lang="ja">

<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>環境設定</title>
<script type="text/javascript" src="mm.js"></script>
<script type="text/javascript" src="sc.js"></script>
<link rel="stylesheet" type="text/css" href="schedule.css">
|;

if(($gHanNo eq "") || ($gHanNo > 10)) {
	$gHanNo = 0;	# 班番号
}
$gHanmei = $HanList[$gHanNo];

if($mode eq "editTaisei") {
	print qq|</head><body><h1>$Hanmei の体制</h1>|;
}
else {
	print qq|</head><body><h1>環境設定</h1>|;
}

if($mode eq "editTaisei") {
	&editTaisei();
}
elsif($mode eq "saveTaisei") {
	&saveTaisei();
}
else {
	&statPage();
}
$dbHandle->disconnect;

print qq|	
	<a href="mm.cgi?mode=editConfig">班情報登録</a><br>
	<a href="mm.cgi?mode=editTaisei">体制登録</a><br>
	<a href="sc.cgi">スケジュール\表\示へ</a><br>
	<a href="kk.cgi">会計\表\示へ</a><br>
	<a href="ad.cgi">管理パスワード入力</a><br>
	<p class="back"><a href="mm.cgi">HOMEへ戻る</a></p>
</body>
</html>
|;

sub showNendoCombo()
{
	my $NendoMin,$NendoMax;
	&GetNenMaxMin($NendoMin,$NendoMax);
	$NendoMax++;
	
	#print qq|returnd .. NendoMin=[$NendoMin],NendoMax=[$NendoMax]	|;
	
	print qq|
	<form name="form1" id="id_form1" action="mm.cgi" method="POST">
	<div class="selectbox color">
	<select id="cmbYear" name="rdYear" onchange="location.href=value;">
	|;
	my $ix = 0;
	my $sel_ix = 0;
	$chkYY = $gNendo;
	for (my $outNendo = $NendoMin;$outNendo le $NendoMax;$outNendo++) {
		my $linkUrl = "mm.cgi?HanNo=$gHanNo&mode=$mode&start=" . $outNendo . "-01-01";
		print qq|\t\t<option value="$linkUrl">$outNendo</option>\n|;
		if($chkYY eq $outNendo) {
			$sel_ix = $ix;
		}
		$ix++;
	}
	print qq|\t</select>年度|;
	#指定された年度をディフォルトとして選択する
	print qq|
		<script>
			var obj = document.getElementById("cmbYear");
			obj.selectedIndex = $sel_ix;
		</script>\n
	|;
}

sub showHanCombo()
{
	print qq|
	<select id="cmbHanNo" name="HanNo" onchange="location.href=value;">
	|;
	#班の選択用ドロップダウンを作成
	my	$ix=0,$sel_ix = 0;
	foreach my $HanName (@HanList){
		my $linkUrl = "mm.cgi?HanNo=$ix&mode=$mode&start=" . $gNendo . "-01-01&mode=$mode&hanchange=1";
		print qq|\t\t<option value="$linkUrl">$HanName</option>\n|;
		if($ix eq $gHanNo) {
			$sel_ix = $ix;
		}
		$ix++;
	}
	print qq|\t</select>\n|;
	#指定された班をディフォルトとして選択する
	print qq|<script>var obj = document.getElementById("cmbHanNo");|;
	print qq|obj.selectedIndex = $sel_ix;</script>\n|;
}

sub statPage()
{
	showNendoCombo();
	showHanCombo();
	
	#班の団員リストを表示
	my @memlist;
	$SankaSql = << "EOS";		#	当年の団員名リストを読み込む
	select t.nendo,t.kaikyu,d.Name from 
		(select * from sybo_taisei where Nendo=$gNendo and KuNo=$gHanNo) t 
		join sybo_danin d ON t.DaninNo = d.No 
		where t.Nendo=$gNendo and d.KuNo=$gHanNo;
EOS
	$sth = $dbHandle->prepare($SankaSql);
	my $rv = $sth->execute;

	print qq|<input type="button" value="回転" onclick="RotaeMember();" /><br>\n|;
	foreach my $DaninName (@DaninList){
		print qq|<input type="text" name="rdDanin$ix" value="@memlist[$ix]" style="width: 20em;">\n|;
		$nxt = $ix+1;
		if(($ix<10) and (@memlist[$nxt] ne "")) {
			print qq|<input type="button" value="下と入替" onclick="SwapText('rdDanin$ix','rdDanin$nxt')" />\n|;
		}
		print qq|<br>\n|;
	}
	print qq|
	<input type="hidden" name="mode" value="saveTaisei">
	<input type="submit" value="　保存　"></form>
	|;
}
sub saveConfig()
{
	my $sth;
	my $pmHanmei = $query->param('rdHanmei');
	print OUT $pmHanmei . "\n";
	print qq|班名：$pmHanmei<br>\n|;

	my $DaninKey;
	my $pmData;
	for(my $ix=0;$ix<10;$ix++) {
		$DaninKey = "rdDanin" . $ix;
		$pmData = $query->param($DaninKey) . "<>";
		if($pmData ne "") {
			print OUT $pmData;
			print qq|No $ix：$pmData<br>\n|;
		}
	}
	print OUT "\n";

	print qq|更新完了<br>\n|;
}
sub editTaisei()
{
	showNendoCombo();
	showHanCombo();
	
	print qq|
	<script>
		//	上下の入れ替え
		function SwapText(ix1,ix2) {
			//	団員番号の入れ替え
			var txt1 = document.getElementsByName("rdDaninNo" + ix1);
			var txt2 = document.getElementsByName("rdDaninNo" + ix2);
			[txt1[0].value,txt2[0].value] = [txt2[0].value,txt1[0].value];

			//	団員名の入れ替え
			txt1 = document.getElementsByName("rdDaninName" + ix1);
			txt2 = document.getElementsByName("rdDaninName" + ix2);
			[txt1[0].value,txt2[0].value] = [txt2[0].value,txt1[0].value];
		}
		
		//	リストの回転
		function RotaeMember() {
			inpLast=0;
			var listDanin = new Array();

			//	団員番号をワイルドカードで取得	`input[type='text'][name='rdDaninNo']`
			//DaninNoList = document.querySelectorAll(`input[type='text']`);
			//DaninNoList = document.querySelectorAll(`input[name='rdDaninNo1']`);
			//DaninNoList = document.querySelectorAll(`input[type='text'][name='rdDaninNo1']`);
			DaninNoList = document.querySelectorAll(`input[name^='rdDaninNo']`);	//先頭一致
			//DaninNoList = document.querySelector('input[name="rdDaninNo*"]');
			DaninNameList = document.querySelectorAll(`input[name^='rdDaninName']`);	//先頭一致
			
			var cnt = DaninNoList.length;
			var DaninNo = DaninNoList[0].value;
			var DaninName = DaninNameList[0].value;
			//DaninList.forEach(function(item,index) {
			for(ix=1;ix<cnt;ix++) {
				//直前のデータにセット
				[DaninNoList[ix-1].value,DaninNameList[ix-1].value] =
					[DaninNoList[ix].value,DaninNameList[ix].value];
			}
			//最後の行に先頭の行にあったものをセット
			DaninNoList[cnt-1].value	= DaninNo;
			DaninNameList[cnt-1].value	= DaninName;
		}
	</script>
	
	<form name="form1" id="id_form1" action="mm.cgi" method="POST">
		<input type="hidden" name="pmNendo" value="$gNendo">
		<input type="hidden" name="pmHanNo" value="$gHanNo">
	|;

	#班の団員リストを表示
	my @memlist;
	$SankaSql = << "EOS";		#	当年の団員名リストを読み込む
	select t.nendo,t.kaikyu,t.DaninNo,d.Name from 
		(select * from sybo_taisei where Nendo=$gNendo and KuNo=$gHanNo) t 
		join sybo_danin d ON t.DaninNo = d.No 
		where t.Nendo=$gNendo and d.KuNo=$gHanNo
		order by t.TaiseiNo;
EOS
	$sth = $dbHandle->prepare($SankaSql);
	my $rv = $sth->execute;

	print qq|
		<input type="button" value="回転" onclick="RotaeMember();" /><br>
		|;

	#メンバーリスト見出しを作成
	$ix = 0;
	while ($hash_ref = $sth->fetchrow_hashref) {
		my %row = %$hash_ref;
		my $Kaikyu = $row{Kaikyu};
		my $DaninNo = $row{DaninNo};
		my $DaninName = $row{Name};

		$nxt = $ix+1;
		print qq|
			<input type="text" name="rdDaninNo$ix" value="$DaninNo" style="width: 3em;">
			<input type="text" name="rdKaikyu$ix" value="$Kaikyu" style="width: 5em;">
			<input type="text" name="rdDaninName$ix" value="$DaninName" style="width: 20em;" readonly>
			<input type="button" value="下と入替" onclick="SwapText($ix,$nxt)">
			<input type="checkbox" name="rdMemDel$ix" value="$ix">削除
			<br>
			|;
		$ix++;
	}
	print qq|
	<input type="hidden" name="mode" value="saveTaisei">
	<input type="submit" value="　保存　"></form>
	<div id="output"></div>
	|;
}
#920-0174
#石川県金沢市薬師町ハ1-27
#嶋田博克

#体制ファイルの更新
sub saveTaisei()
{
	#my @paramlist = $query->param;
	my $pmYear = $query->param('pmNendo');
	my $pmHanNo = $query->param('pmHanNo');

	$SankaSql = << "EOS";		#	当年の団員名リストを読み込む
	select t.No, t.Nendo, t.Kuno, t.TaiseiNo, t.kaikyu, t.DaninNo, d.Name from 
		(select * from sybo_taisei where Nendo=$pmYear and KuNo=$pmHanNo) t 
		join sybo_danin d ON t.DaninNo = d.No 
		where t.Nendo=$pmYear and d.KuNo=$pmHanNo
		order by t.TaiseiNo;
EOS


	print qq|mode=[$mode] Year=[$pmYear]  pmHanNo=[$pmHanNo]<br>sql=[$SankaSql]<br>\n|;
	
	$sth = $dbHandle->prepare($SankaSql);
	my $rv = $sth->execute;
	
	$ix = 0;
	while ($hash_ref = $sth->fetchrow_hashref) {
		my %row = %$hash_ref;
		my $dtNo = $row{No};
		my $dtHanNo = $row{KuNo};

		my $sqlStr = "update sybo_taisei set ";		# UPDATEのためのSQL編集
		
		my $pmKaikyu = $query->param("rdKaikyu" . $ix);	# 階級
		if($pmKaikyu == "") {
			print qq|pmKaikyu is null<br>\n|;
			break:
		}
		$sqlStr .= "kaikyu='$pmKaikyu'";
		$sqlStr .= ",DaninNo = '" . $query->param("rdDaninNo" .$ix) . "' ";	# 団員番号
		$sqlStr .= "where No=$dtNo;";

		print qq|UPDATE SQL=[$sqlStr]<br>\n|;
		$ix++;
	}


	print qq|更新完了<br>\n|;
}

# ---------------- #
# エラーメッセージ #
# ---------------- #
sub errorexit
{
	$msg = shift @_;

	print qq|<html lang="ja"><head><title>更新できませんでした</title></head><body>\n|;
	print qq|<div style="background-color:red; color:#fffff0; font-weight:bold; font-family:Arial,sans-serif; padding:1px;">うまく\表\示できなかったようです</div><br>\n|;
	print qq|<div style="font-size: smaller;">エラー内容：</div>\n|;
	print qq|<div style="border:1px dotted blue; padding:1em;">$msg</div>\n|;
	print qq|<div style="text-align: right;"><form><input type="button" value="戻る" onClick="history.back();"></form></div>|;
	print qq|</body></html>\n|;

	exit;
}



