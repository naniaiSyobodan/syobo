#! /usr/bin/perl

# ================================================================== #
#  Fumy Teacher's Schedule Board   Ver 2.3.0   [admin.cgi]           #
# ================================================================== #
#  Copyright (C) Fumihiro Nishimura.(Nishishi) 2004-2016.            #
#                                                                    #
#  スケジュール表示フリーCGIです。(このファイルは管理・編集用CGI)    #
#  著作権は、西村文宏(にしし)にあります。                            #
#  このCGIは誰でも自由にご使用頂けます。商用・非商用を問いません。   #
#  著作権表示を削除・改変せずにご使用下さい。                        #
#                                                                    #
#  http://www.nishishi.com/                                          #
# ================================================================== #
#  パスワード格納ファイルは、最初は中身を空っぽの状態でアップロード  #
#  して下さい。すると、このCGIにアクセスしたときに、パスワード作成   #
#  画面が出ます。パスワードを忘れてしまった場合も、パスワード格納フ  #
#  ァイルの中身を削除してアップロードすることで、リセットできます。  #
#  ※パスワードを「固定」に設定した場合は、パスワード格納ファイルは  #
#  使いません。                                                      #
# ================================================================== #

# ================ #
#  ▼ユーザ設定▼  #
# ================ #

# パスワード指定種別（ 0: 固定 ／ 1: 変更可能 ）
$passwordtype = 1;

# パスワード（固定の場合）
$password = "0000";

# パスワード格納ファイル名（変更可能な場合）　Webからアクセスできないディレクトリに置くのが安全です。
$pwfile = "upf.cgi";

# 1週間の汎用予定表格納ファイル名
$weeklyfile = "weekly.txt";

# カレンダー予定表格納ファイル名
$calendarfile = "calendar.txt";

# 長期予定格納ファイル名
$longfile = "long.txt";

# 予定表用 定型予定ファイル名
$scheduleseals = "seals.txt";

# スケジュール表示CGI名（デフォルトは schedule.cgi ）
$schedulecgi = "schedule.cgi";

# このCGIのファイル名
$thiscgi = "admin.cgi";

# CSS(スタイルシート)ファイル名
$cssfile = "admin.css";

# 暗号化キー（任意の2文字／※変更する必要はありません。変更したければしても構いません。）
$cryptkey = "fx";

# ======================== #
#  ▲ユーザ設定ここまで▲  # ※ここから下を書き換える必要はありません。
# ======================== #
my $demomode = 0;

use Time::Local;

# カレンダー表示用パッケージを呼ぶ
require 'calendar.pl';

# 変数初期化
$mode = "";		# 動作モード
$upw  = "";		# ユーザパスワード
$encupw = "";	# エンコード後のユーザパスワード
$loginmsg = "パスワードを入力して下さい。";	# ログイン画面メッセージ

$wscaption=""; @wsrow0=(); @wsrow1=(); @wsrow2=(); @wsrow3=(); @wsrow4=(); @wsrow5=(); @wsrow6=(); @wsrow7=();	# 1週間の汎用予定表用

my $voidtags = $calendarpackage::voidtags;	# HTMLタグの無効化設定(calendar.plの値を使用)

# DEMO
my $demomsg = "";
if( $demomode == 1 ) {
	$demomsg = qq|<p style="background-color: #ffeeee; border: 1px solid #ffdddd; border-radius: 1em; padding: 1em; margin: 0px; color:#cc0000;font-size:80%;"><span style="background-color:#cc0000;color:#fffff0; font-weight:bold;">■動作サンプル■</span><br>※ご自由にお試し頂けます。パスワードは <strong style="font-family:monospace;">guest</strong> です。<br>※HTMLタグの入力は無効に設定されていますが、実際に運営する際にはどんなHTMLタグも利用可能\\です。（無効に設定することもできます）</p>|;
}

# 内部HTMLのロード
@datahtml = <DATA>;

@seals;



# メイン処理開始
print "Content-type: text/html\n\n";

# パラメータ分解
&splitparam();

# パスワードチェック
$pwcheckresult = &checkpassword($upw,$encupw);
if( ($mode ne "") && ($mode ne $dochangepw) && ($pwcheckresult == 0) ) {
	# モードが「ログイン」でなく、「パスワード変更実行」でもなく、
	# パスワードが違う場合はログイン画面を再度表示
	$loginmsg = qq|<span class="error">パスワードが違います。再度入力して下さい。</span>|;
	$mode = "";
}
if( $pwcheckresult == 3 ) {
	# 初期パスワード設定モード
	if( $cpwnewpw eq "" ) {
		# 新パスワードの入力がまだなら入力フォームを表示
		&makepw();
		$mode = "makepw";
	}
	# 新パスワードの入力があれば、モードは dochangepw なのでそのまま実行
}

# 分岐
if( $mode eq "" ) {
	# ログイン画面
	&logindisp($loginmsg);
}
elsif( $mode eq "home" ) {
	# 初期画面
	&firstdisp();
}
elsif( $mode eq "calender" ) {
	# 月間予定表の編集(初期画面)
	&editcalendardisp();
}
elsif( $mode eq "editcalendar" ) {
	# 月間予定表の編集(特定の月の表示)
	&editonemonthdisp();
}
elsif( $mode eq "editcalendardate" ) {
	# 月間予定表の編集(特定の日の表示)
	&editdatedisp();
}
elsif( $mode eq "recorddate" ) {
	# 月間予定表の特定の日の予定を保存
	&calendarsave();
}
elsif( $mode eq "calendardelete" ) {
	# 月間予定表の特定の日の予定を保存
	&calendardelete();
}

elsif( $mode eq "weekly" ) {
	# 一週間の汎用予定表の編集
	&weeklydisp();
}
elsif( $mode eq "weeklysave" ) {
	# 一週間の汎用予定表の保存
	&weeklysave();
}
elsif( $mode eq "long" ) {
	# 長期予定の編集
	&longdisp();
}
elsif( $mode eq "longedit" ) {
	# 長期予定の選択編集(項目作成・変更)
	&longeditdisp();
}
elsif( $mode eq "longwrite" ) {
	# 長期予定の書き込み
	&longwrite();
}
elsif( $mode eq "longdelete" ) {
	# 長期予定の削除
	&longdelete();
}
elsif( $mode eq "longlistdelete" ) {
	# 長期予定の一括削除（昨日までの全データ項目を削除）
	&longlistdelete();
}


elsif( $mode eq "cpw" ) {
	# パスワードの変更
	&changepassword();
}
elsif( $mode eq "dochangepw" ) {
	# パスワードの変更を実行
	&dochangepw();
}




# ---------------- #
# パラメータの分解 #
# ---------------- #
sub splitparam()
{
	# 結合
	my $buffer = "";
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	}
#	my $querybuffer = $ENV{'QUERY_STRING'} . '&' . $buffer;
	my $querybuffer = $buffer;	# POSTのみ

	# 分解
	my @pairs = split(/&/,$querybuffer);
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);

		# 2バイト文字をデコード
		$value =~ s/\+/ /g;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

		# 分解
		if( $name eq "mode" ) {
			$mode = $value;		# スクリプト動作モード
		}
		elsif( $name eq "pw" ) {
			$upw = $value;		# パスワード
		}
		elsif( $name eq "encpw" ) {
			$encupw = $value;	# エンコード済みパスワード
		}

		# --- 1週間の汎用予定表用 ---
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

		# --- 月間予定表用 ---
		elsif( $name eq "edityear" ) {	$cedityear = $value;	}
		elsif( $name eq "editmonth" ) {	$ceditmonth = $value;	}
		elsif( $name eq "editday" ) {	$ceditday = $value;	}
		elsif( $name eq "schedule1" ) {	$ceschedule[0] = $value;	}
		elsif( $name eq "schedule2" ) {	$ceschedule[1] = $value;	}
		elsif( $name eq "schedule3" ) {	$ceschedule[2] = $value;	}
		elsif( $name eq "seal1" ) {	$ceseal[0] = $value;	}
		elsif( $name eq "seal2" ) {	$ceseal[1] = $value;	}

		# --- 長期予定表用 ---
		elsif( $name eq "editnum" ) {	$longeditnum = $value;	}
		elsif( $name eq "lwyear"  ) {	$longedityear  = $value;	}
		elsif( $name eq "lwmonth" ) {	$longeditmonth = $value;	}
		elsif( $name eq "lwday"   ) {	$longeditday   = $value;	}
		elsif( $name eq "ldata"   ) {	$longeditdata  = $value;	}
		elsif( $name eq "lvalue"  ) {	$longeditvalue = $value;	}

		# --- パスワード変更用 ---
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
# パスワードのチェック #
# -------------------- #
sub checkpassword
{
	my $recordedpass;
	my $thistimepass;

	# ユーザが入力したパスワード
	my $userpassword    = shift @_;
	my $encuserpassword = shift @_;

	# 記録されているパスワードを得る(recorded pass)
	if( $passwordtype == 0 ) {
		# 固定
		$recordedpass = crypt($password,$cryptkey);
	}
	elsif( $passwordtype == 1 ) {
		# ファイル
		open(IN,"$pwfile") || &errorexit("パスワード格納ファイルが読めない。<br><br>初回実行時は、中身を空っぽにしたパスワード格納ファイルをアップロードしておいて下さい。そうすると、パスワード作成画面が出ます。");
		$recordedpass = <IN>;
		close(IN);
		
		# パスワードが格納されているかどうか？
		if( $recordedpass eq "" ) {
			# 格納されていなければ初回実行時
			return 3;
		}
	}

	# ユーザが今回入力したパスワードを得る
	if( $encuserpassword ne "" ) {
		# 既にエンコード済みのパスワードがある場合はそれをそのまま使用
		$thistimepass = $encuserpassword;
	}
	else {
		# まだエンコードされてない場合はユーザが入力した生のパスワードをエンコードしてから使用
		$thistimepass = crypt($userpassword,$cryptkey);
	}

	# 一致を確認
	#<DEBUG>print "THIS TIME: $thistimepass<br>RECORDED: $recordedpass<br>\n";
	if( $thistimepass eq $recordedpass ) {
		# 一致したらOK
		$encupw = $thistimepass;	# エンコード後のユーザパスワードを今後の処理のために変数に格納
		return 1;
	}
	
	# 一致しなかったらエラー
	return 0;
}

# ------------------ #
# ログイン画面の表示 #
# ------------------ #
sub logindisp
{
	# ログイン画面の表示
	$loginmsg = shift @_;

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	&loaddata('\[Login\]','\[/Login\]');
	&loaddata('\[Foot\]','\[/Foot\]');
}

# -------------- #
# 初期画面の表示 #
# -------------- #
sub firstdisp
{
	# 初期画面の表示
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	&loaddata('\[First\]','\[/First\]');
	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------- #
# パスワードの変更 #
# ---------------- #
sub changepassword
{
	# パスワード変更画面
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	if( $passwordtype == 0 ) {
		# パスワードが固定モードなら変更不可
		print qq|<p><span class="error">このCGIの設定で、パスワードは固定されています。ユーザによるパスワードの変更はできません。</span></p>\n|;
		print qq|<p>パスワードを変更可能\\にするには、CGIのソ\\ースを開いて、パスワード指定を「固定」から「変更可能\\」に書き換えて下さい。この操作は、このCGIの管理者にしかできません。</p>\n|;
		print qq|<form><input type="button" value="戻る" onClick="history.back();"></form>|;
	}
	else {
		# パスワードが変更可能モードなら変更フォームを表示
		&loaddata('\[ChangePW\]','\[/ChangePW\]');
	}
	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------------- #
# パスワードの変更を実行 #
# ---------------------- #
sub dochangepw
{
	# パスワードの変更を実行
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# パスワードのチェック
	if( &checkpassword($cpwnowpw,"") == 0 ) {
		# パスワードが一致しなかった場合
		print qq|<p><span class="error">パスワードが一致しません。</span></p>\n|;
		print qq|<form><input type="button" value="戻る" onClick="history.back();"></form>|;
	}
	else {
		# パスワードが一致したら変更
		&workcpw($cpwnewpw);

		# メッセージ
		print qq|<p>パスワードを変更しました。今作成した新しいパスワードでログインし直して下さい。</p>\n|;
		# 戻るフォームを表示
		&backlink("","ログイン画面へ");
	}

	&loaddata('\[Foot\]','\[/Foot\]');
}

sub workcpw
{
	# パスワードをエンコードしてパスワードファイルに記録
	my $npw = shift @_;
	my $writestring = crypt($npw,$cryptkey);

	# パスワードファイルに書き込む
	open(OUT,"> $pwfile") || &errorexit("パスワード格納ファイルを書き込みモードで開けませんでした。書き込み禁止になっていないか確認して下さい。");
	print OUT "$writestring";
	close(OUT);
}

# ---------------------- #
# 初期パスワード設定画面 #
# ---------------------- #
sub makepw
{
	# パスワード変更画面
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	&loaddata('\[MakePW\]','\[/MakePW\]');
	&loaddata('\[Foot\]','\[/Foot\]');
}

# -------------------------------- #
# 一週間の汎用予定表編集画面の表示 #
# -------------------------------- #
sub weeklydisp
{
	# 一週間の汎用予定表編集画面
	my ( $caption, @rows , @row0, @row1, @row2, @row3, @row4, @row5, @row6, @row7 );

	# ファイルを読む
	open(IN,"$weeklyfile") || &errorexit("一週間の汎用予\\定表ファイル $weeklyfile が読めませんでした。");
	my @weekdata = <IN>;
	close(IN);

	# ファイルの全中身からHTMLタグをデコード
	@weekdata = &decodehtmltags(@weekdata);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# ファイルの中身を分解
	foreach my $line (@weekdata) {
		# 「＝」で分解
		my @val2;
		my ($name, $value, @val2) = split(/=/, $line);

		# ---ADD--- Ver 1.1 : 値に「=」が含まれているとカットされてしまうのを防ぐコード(応急措置)
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

	# 各項目に分割
	@row0 = split(/\|/, $rows[0]);
	@row1 = split(/\|/, $rows[1]);
	@row2 = split(/\|/, $rows[2]);
	@row3 = split(/\|/, $rows[3]);
	@row4 = split(/\|/, $rows[4]);
	@row5 = split(/\|/, $rows[5]);
	@row6 = split(/\|/, $rows[6]);
	@row7 = split(/\|/, $rows[7]);

	print qq|<h2>1週間の汎用予\\定表\\</h2>\n<p class="title">書き換えたい箇所を編集して下さい。最後に「保存」ボタンをクリックして下さい。</p>|;

	# フォームを表示
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

	# 末尾のメッセージ
	print qq|<p><span class="note">|;
	if( $voidtags == 1 ) {
		# HTMLタグが無効の場合
		print qq|※HTMLタグの使用は<strong>無効に</strong>設定されています。タグを記述しても、そのまま表\\示されます。<br>|;
	}
	else {
		# HTMLタグが有効の場合
		print qq|※項目内で改行させたい場合は、半角で <span class="code">&lt;br&gt;</span> と入力して下さい。その他のHTMLタグもすべて使用可能\\です。半角の「&lt;」や「&gt;」はHTMLタグと認識されますので、文字として単独で入力しないで下さい。表\\示が崩れて再編集できなくなる場合があります。（calendar.plの設定から、HTMLタグの使用を無効に設定することもできます。）<br>|;
	}
	print qq|※曜日欄も含めて、1行まるごと空欄にすれば、その行は表\\示されなくなります。</span></p>\n|;

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ------------------------ #
# 一週間の汎用予定表を保存 #
# ------------------------ #
sub weeklysave
{
	# 一週間の汎用予定表を編集

	# ファイルに書く
	open(OUT,"> $weeklyfile") || &errorexit("一週間の汎用予\\定表\\ファイル $weeklyfile を書き込みモードで開けませんでした。");

	print OUT "# ＜週間汎用スケジュール用データファイル＞\n";
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
	print qq|<p class="endmsg">保存しました。 <span class="note">【更新時刻： $modifytime】</span></p>|;

	# 戻るフォームを表示
	&backlink("home","");

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ------------------------ #
# 長期予定表編集画面の表示 #
# ------------------------ #
sub longdisp
{
	# 長期予定表編集画面

	# ファイルを読む
	open(IN,"$longfile") || &errorexit("長期予\\定ファイル $longfile が読めませんでした。");
	my @longdata = <IN>;
	close(IN);

	# ファイルの全中身からHTMLタグをデコード
	@longdata = &decodehtmltags(@longdata);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<h2>長期予\\定表\\</h2>\n<p class="title">新規に追加する場合は「新規作成」にチェックを入れて、既存の項目を書き換えたい場合は書き換えたい箇所にチェックを入れて、「上記の選択項目を編集」ボタンを押して下さい。<br><span class="note">※HTMLタグの使用を有効に設定している場合でも、下記の一覧にはHTMLタグがソ\\ースのまま表\\示されています。</span></p>|;

	# フォームを表示
	&loaddata('\[FormTop\]','\[/FormTop\]');

	print qq|<input type="hidden" name="mode" value="longedit">\n|;

	# ファイルの中身を分解して表示
	print qq|<table class="inputtable">\n|;
	print qq|<tr><th>No.</th><th>日付</th><th>内容</th></tr>\n|;
	my $counter=0;
	foreach my $line (@longdata) {
		# カンマで分解
		my ($lid, $ldata, $lvalue) = split(/,/, $line);
		# カウント(No.用に)
		$counter++;
		# レコードを表示
		print qq|<tr><td><input type="radio" name="editnum" value="$counter" id="eid$counter"><label for="eid$counter">$counter</label></td><td>$ldata</td><td>$lvalue</td></tr>|;
	}
	print qq|<tr><td colspan="3"><input type="radio" name="editnum" value="0" id="new" checked><label for="new">新規作成</label></td></tr>|;
	print qq|</table>\n|;
	print "<br>\n";

	# フォームを閉じる
	&closeform("上記の選択項目を編集");

	# 戻るフォームを表示
	&backlink("home","");

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------------------------- #
# 長期予定表項目の編集（追加・変更） #
# ---------------------------------- #
sub longeditdisp
{
	# 長期予定表編集画面
	my ($lid, $ldata, $lvalue);
	my ($mday,$month,$year);

	# ファイルを読む
	open(IN,"$longfile") || &errorexit("長期予\\定ファイル $longfile が読めませんでした。");
	my @longdata = <IN>;
	close(IN);

	# ファイルの全中身からHTMLタグをデコード
	@longdata = &decodehtmltags(@longdata);

	# 編集用既存データの読み出し
	if( $longeditnum > 0 ) {
		# 番号が指定されていれば（＝新規作成でなければ）
		($lid, $ldata, $lvalue) = split(/,/, $longdata[$longeditnum-1]);
		# 日付を分解
		($mday,$month,$year) = (localtime($lid))[3,4,5];
	}
	else {
		# 今の日付を得る
		($mday,$month,$year) = (localtime(time))[3,4,5];
		# 新規作成用に、配列の「最後の番号」の次を指定
		$longeditnum = $#longdata + 2;
	}

	# 日付を調整
	$year  = $year  + 1900;
	$month = $month + 1;

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<h2>長期予\\定 項目編集</h2>\n<p class="title">表\\示する日付と内容を入力して下さい。「編集内容を保存」ボタンを押すと保存されます。</p>\n|;

	# フォームを表示
	&loaddata('\[FormTop\]','\[/FormTop\]');

	print <<"EOM";
	<input type="hidden" name="mode" value="longwrite">
	<input type="hidden" name="editnum" value="$longeditnum">
	<table class="inputtable">
	<tr>
		<th colspan="2">No.$longeditnum</th>
	</tr>
	<tr>
		<td>表\\示期限</td>
		<td>
			<input type="text" name="lwyear"  value="$year"  style="width: 3em;">年
			<input type="text" name="lwmonth" value="$month" style="width: 2em;">月
			<input type="text" name="lwday"   value="$mday"  style="width: 2em;">日<br>
			<span class="note">※ここで指定した日付が、この項目の表\\示期限になります。（この日以降は表\\示されません。）</span><br>
		</td>
	</tr>
	<tr>
		<td>日付(文字列)</td>
		<td>
			<input type="text" name="ldata"  value="$ldata"  style="width: 24em;"><br>
			<span class="note">※ここに入力した内容が日付欄に表\\示されます。入力を省略すれば、上記の日付から自動的に文字列を生成します。</span><br>
		</td>
	</tr>
	<tr>
		<td>予\\定内容</td>
		<td>
			<input type="text" name="lvalue"  value="$lvalue"  style="width: 36em;">
		</td>
	</tr>
	</table>
	<br>
EOM

	&loaddata('\[FormBottom\]','\[/FormBottom\]');

	# 削除用ボタン
	unless( $longeditnum == $#longdata + 2 ) {
		# 新規データでなければ削除用ボタンを表示
		print qq|<table align="right" border="1" class="caution"><tr><td>\n|;
		&loaddata('\[FormTop\]','\[/FormTop\]');
		print qq|<input type="hidden" name="editnum" value="$longeditnum">\n|;
		print qq|<input type="hidden" name="mode" value="longdelete">\n|;
		&closeform("この項目を削除");
		print qq|</td></tr></table>|;
	}

	# 末尾のメッセージ
	print qq|<p><span class="note">|;
	if( $voidtags == 1 ) {
		# HTMLタグが無効の場合
		print qq|※HTMLタグの使用は<strong>無効に</strong>設定されています。タグを記述しても、そのまま表\\示されます。<br>|;
	}
	else {
		# HTMLタグが有効の場合
		print qq|※項目内で改行させたい場合は、半角で <span class="code">&lt;br&gt;</span> と入力して下さい。その他のHTMLタグもすべて使用可能\\です。（calendar.plの設定から、HTMLタグの使用を無効に設定することもできます。）<br>|;
	}
	print qq|</span></p>\n|;

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ------------------------ #
# 長期予定表項目の書き込み #
# ------------------------ #
sub longwrite
{
	# 長期予定表項目の書き込み

	# データのチェック
	unless( $longeditnum > 0 ) {
		# 1以上の数値でなければ
		&errorexit("longeditnum変数に不正な値が代入されています。1以上の整数でなければなりません。");
	}
	unless( $longedityear > 1970 && $longedityear < 2038 && $longeditmonth > 0 && $longeditmonth <= 12 && $longeditday > 0 && $longeditday <= 31 ) {
		# 日付の構成要素が不正な場合
		&errorback("日付の構\\成要素が不正です。正しい数値（半角）を入力して下さい。： $longedityear年 $longeditmonth月 $longeditday日");
	}

	# ファイルを読む
	open(IN,"$longfile") || &errorexit("長期予\\定ファイル $longfile が読めませんでした。");
	my @longdata = <IN>;
	close(IN);

	# 表示期限日のエポック秒を求める
	$limitdate = timelocal(0, 0, 12, $longeditday, $longeditmonth - 1, $longedityear);

	# 日付文字列が入力されていなければ生成する
	my $monthspace = " ";
	my $datespace  = " ";
	unless( $longeditmonth < 10 ) {	$monthspace = ""; }
	unless( $longeditday < 10 )   { $datespace  = ""; }
	if( $longeditdata eq "" ) {
		$longeditdata = "$longedityear年$monthspace$longeditmonth月$datespace$longeditday日";
	}

	# 行を作成
	my $writeline = "$limitdate,$longeditdata,$longeditvalue\n";

	# 作成した行を追加
	$longdata[$longeditnum-1] = $writeline;

	# 配列をソート
	my @sortedld = sort { $a cmp $b } @longdata;

	# 書き込み
	open(OUT,"> $longfile") || &errorexit("長期予\\定表\\ファイル $longfile を書き込みモードで開けませんでした。");
	foreach my $line (@sortedld) {
		# 全行に書き込み
		print OUT "$line";
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>書き込みました。</p>|;

	# 戻るフォームを表示
	&backlink("long","長期予\\定リストに戻る");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# -------------------- #
# 長期予定表項目の削除 #
# -------------------- #
sub longdelete
{
	# 長期予定表項目の削除
	my $count=0;

	# データのチェック
	unless( $longeditnum > 0 ) {
		# 1以上の数値でなければ
		&errorexit("longeditnum変数に不正な値が代入されています。1以上の整数でなければなりません。");
	}

	# ファイルを読む
	open(IN,"$longfile") || &errorexit("長期予\\定ファイル $longfile が読めませんでした。");
	my @longdata = <IN>;
	close(IN);

	# 書き込み
	open(OUT,"> $longfile") || &errorexit("長期予\\定表\\ファイル $longfile を書き込みモードで開けませんでした。");
	foreach my $line (@longdata) {
		# 全行ループ
		$count++;
		unless( $count == $longeditnum ) {
			# 削除対象行でなければ書く
			print OUT "$line";
		}
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>$longeditnum番目の項目を削除しました。</p>|;

	# 戻るフォームを表示
	&backlink("long","長期予\\定リストに戻る");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ------------------------ #
# 長期予定表項目の一括削除 #
# ------------------------ #
sub longlistdelete
{
	# 長期予定表項目の一括削除（昨日までの全データを削除）
	my $delcount=0;

	# ファイルを読む
	open(IN,"$longfile") || &errorexit("長期予\\定ファイル $longfile が読めませんでした。");
	my @longdata = <IN>;
	close(IN);

	# 現在から36時間前の時刻（エポック秒）を得る
	my $yesterday = (time) - (36*60*60);

	# 書き込み
	open(OUT,"> $longfile") || &errorexit("長期予\\定表\\ファイル $longfile を書き込みモードで開けませんでした。");
	foreach my $line (@longdata) {
		# データを分割
		($lid, undef, undef) = split(/,/, $line);
		# 時刻を比較
		if( $yesterday < $lid ) {
			# 削除対象行でなければ書く
			print OUT "$line";
		}
		else {
			# 削除個数をカウント
			$delcount++;
		}
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>$delcount個の項目を削除しました。</p>|;

	# 戻るフォームを表示
	&backlink("long","長期予\\定リストに戻る");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ---------------------------------------- #
# 月間予定表（カレンダー予定表）の編集画面 #
# ---------------------------------------- #
sub editcalendardisp
{
	# カレンダー予定表編集画面
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# 表示年月の設定
	my ($dispmonth,$dispyear) = (localtime(time))[4,5];
	$dispyear  = $dispyear + 1900;
	$dispmonth = $dispmonth + 1;

	print qq|<hr class="thin">\n|;

	# カレンダー表示指示（年,月,予定ファイル名）
	# 今月
	#print "<p>▼ $dispyear 年 $dispmonth 月のカレンダー<br></p>\n";
	&calendarpackage::makecalendar($dispyear, $dispmonth, $calendarfile);

	# 来月
	if( $dispmonth < 12 ) {
		# 11月までなら月に1を加える
		$dispmonth++;
	}
	else {
		# 12月なら、年に1を加えて月を1にする
		$dispyear++;
		$dispmonth = 1;
	}
	#print "<p>▼ $dispyear 年 $dispmonth 月のカレンダー<br></p>\n";
	&calendarpackage::makecalendar($dispyear, $dispmonth, $calendarfile);

	print qq|<br><hr class="thin"><br>\n|;

	# 戻るリンク
	&backlink("home","");

	&loaddata('\[Foot\]','\[/Foot\]');

}

# ---------------------------- #
# 月間予定表の特定月の編集画面 #
# ---------------------------- #
sub editonemonthdisp
{
	# カレンダー予定表編集画面
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# 表示年月の設定（パラメータで指定された年月）
	my $dispyear  = $cedityear;
	my $dispmonth = $ceditmonth;

	# 日付選択フォームの表示
	print qq|<p class="title">$dispyear年$dispmonth月のデータを編集・追加します。日付を選択して下さい。</p>\n|;
	&editcalendarrecorddisp($dispyear, $dispmonth);

	print qq|<hr class="thin">\n|;

	# 月間予定表カレンダーの表示～戻るリンク
	&makecommoncalendarparts($dispyear, $dispmonth, $calendarfile)

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------------------- #
# 月間予定表の特定日の編集画面 #
# ---------------------------- #
sub editdatedisp
{
	# カレンダー予定表編集画面
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	# 表示年月の設定（パラメータで指定された年月日）
	my $dispyear  = $cedityear;
	my $dispmonth = $ceditmonth;
	my $dispday   = $ceditday;

	# レコード作成フォームの表示
	print qq|<p class="title">予\\定を入力して、「この日のデータを保存」ボタンをクリックして下さい。</p>\n|;
	&editcalendardate($dispyear, $dispmonth, $dispday);

	# 末尾のメッセージ
	print qq|<p><span class="note">|;
	if( $voidtags == 1 ) {
		# HTMLタグが無効の場合
		print qq|※HTMLタグの使用は<strong>無効に</strong>設定されています。タグを記述しても、そのまま表\\示されます。<br>|;
	}
	else {
		# HTMLタグが有効の場合
		print qq|※HTMLタグはすべて使用可能\\です。半角の「&lt;」や「&gt;」はHTMLタグと認識されますので、文字として単独で入力しないで下さい。（calendar.plの設定から、HTMLタグの使用を無効に設定することもできます。）<br>|;
	}
	print qq|</span></p>\n|;

	print qq|<hr class="thin"><br>\n|;

	# 月間予定表カレンダーの表示～戻るリンク
	&makecommoncalendarparts($dispyear, $dispmonth, $calendarfile)

	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------- #
# 月間予定表の保存 #
# ---------------- #
sub calendarsave
{
	# 記録日
	my $year  = $cedityear;
	my $month = $ceditmonth;
	my $day   = $ceditday;

	my @record;		# 記録用文字列の配列
	my $recstring;	# 記録用文字列
	my $recdate;	# レコードの日付

	# 予定内容1
	if( $ceschedule[0] ne "" ) {
		# 任意側に文字列があればそれを記録
		push( @record, "$ceschedule[0]<>" );
	}
	elsif( $ceseal[0] ne "" ) {
		# 選択側に文字列があればそれを記録
		push( @record, "$ceseal[0]<>" );
	}

	# 予定内容2
	if( $ceschedule[1] ne "" ) {
		# 任意側に文字列があればそれを記録
		push( @record, "$ceschedule[1]<>" );
	}
	elsif( $ceseal[1] ne "" ) {
		# 選択側に文字列があればそれを記録
		push( @record, "$ceseal[1]<>" );
	}

	# 備考欄
	# 予定内容1
	if( $ceschedule[2] ne "" ) {
		# 文字列があれば記録
		push( @record, "$ceschedule[2]<>" );
	}

	# 記録用文字列の生成
	$recdate   = "$year/$month/$day,";
	$recstring = $recdate . join( "", @record );
	# 途中の改行を削除して末尾に改行を付加
	$recstring =~ s/\n//g;
	$recstring =~ s/\r//g;
	$recstring = $recstring . "\n";

	# ファイルを読む
	open(IN,"$calendarfile") || &errorexit("月間予\\定ファイル $calendarfile が読めませんでした。");
	my @allshcedule = <IN>;
	close(IN);

	# 書き込み用配列を作成
	my @scheduleforwrite;
	foreach my $line (@allshcedule) {
		# 全行ループ
		unless( $line =~ m/$recdate/i ) {
			# 今回のデータと日付が一致しなければ書き込み
			push( @scheduleforwrite, $line );
		}
	}
	push( @scheduleforwrite, $recstring );

	# ファイルをソート
	my @sortedsw = sort { $a cmp $b } @scheduleforwrite;

	# 書き込み
	open(OUT,"> $calendarfile") || &errorexit("月間予\\定ファイル $calendarfile を書き込みモードで開けませんでした。");
	foreach my $line (@sortedsw) {
		# 全行を書き込み
		print OUT "$line";
	}
	close(OUT);

	# 結果報告画面
	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	my $modifytime = &get_timestamp($calendarfile);
	print qq|<p class="endmsg">保存しました。 <span class="note">【更新時刻： $modifytime】</span></p>|;

	print qq|<hr class="thin">\n|;

	# 日付選択フォームの表示
	print qq|<p class="title">他の日付を編集する場合は選択して下さい。</p>\n|;
	&editcalendarrecorddisp($year, $month, $day+1);

	print qq|<hr class="thin">\n|;

	# 月間予定表カレンダーの表示～戻るリンク
	&makecommoncalendarparts($year, $month, $calendarfile)

	&loaddata('\[Foot\]','\[/Foot\]');
}

# -------------------------------------------------- #
# 月間予定表カレンダー～戻るリンクまで共通部分の生成 #
# -------------------------------------------------- #
sub makecommoncalendarparts
{
	my ($dispyear, $dispmonth, $calendarfile) = @_;

	# カレンダー表示指示（年,月,予定ファイル名）
	#print "$dispyear 年 $dispmonth 月のカレンダー<br>\n";
	&calendarpackage::makecalendar($dispyear, $dispmonth, $calendarfile);

	# 戻るリンク
	print qq|<table><tr><td>|;
	&backlink("calender","月間予\\定表\\TOPへ戻る");
	print qq|</td><td>|;
	&backlink("home","");
	print qq|</td></tr></table>\n|;
}

# ---------------------------------------------------------- #
# 月間予定表（カレンダー予定表）のレコード作成フォームの表示 #
# ---------------------------------------------------------- #
sub editcalendardate
{
	my $dispyear = shift @_;
	my $dispmonth= shift @_;
	my $dispday  = shift @_;

	# 指定日の予定を得る
	&calendarpackage::loadcalendar( $dispyear, $dispmonth, $calendarfile );		# 先にデータファイルを読ませる
	my $alreadystring = &calendarpackage::getdayschedule( $dispyear, $dispmonth, $dispday );

	# 予定を分解
	my @yoteis;
	($yoteis[0], $yoteis[1], $yoteis[2]) = split(/<>/, $alreadystring);

	# 予定の中身からHTMLタグをデコード
	@yoteis = &decodehtmltags(@yoteis);

	# 月間予定表用シール(定型文)の読み込み
	&loadseals();

	# コンソールフォームの表示
	&loaddata('\[FormTop\]','\[/FormTop\]');
	print qq|<input type="hidden" name="mode" value="recorddate">\n|;
	print qq|<input type="hidden" name="edityear"  value="$dispyear">\n|;
	print qq|<input type="hidden" name="editmonth" value="$dispmonth">\n|;
	print qq|<input type="hidden" name="editday" value="$dispday">\n|;

	print qq|<table class="inputtable">\n|;
	print qq|<tr><th colspan="2">$dispyear年 $dispmonth月 $dispday日 の予\\定</th></tr>|;

	print qq|<tr><td>予\\定内容1</td><td>\n|;
	print qq|分類：<select name="seal1">|; &showseals(); print qq|</select><br>\n|;
	print qq|内容：<input type="text" name="schedule1" value="$yoteis[0]" style="width: 21em;"><br>\n|;
	print qq|時刻：<input type="time" name="timestart1" value="$timestart[0]"> ～ <input type="time" name="timeend1" value="$timeend[0]"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|<tr><td>予\\定内容2</td><td>\n|;
	print qq|選択：<select name="seal2">|; &showseals(); print qq|</select><br>\n|;
	print qq|任意：<input type="text" name="schedule2" value="$yoteis[1]" style="width: 21em;"><br>\n|;
	print qq|時刻：<input type="time" name="timestart2" value="$timestart[1]"> ～ <input type="time" name="timeend2" value="$timeend[1]"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|<tr><td>予\\定内容3</td><td>\n|;
	print qq|選択：<select name="seal3">|; &showseals(); print qq|</select><br>\n|;
	print qq|任意：<input type="text" name="schedule3" value="$yoteis[2]" style="width: 21em;"><br>\n|;
	print qq|時刻：<input type="time" name="timestart3" value="$timestart[2]"> ～ <input type="time" name="timeend3" value="$timeend[2]"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|<tr><td>備考</td><td>\n|;
	print qq|任意：<input type="text" name="schedule3" value="$yoteis[3]" style="width: 21em;"><br>\n|;
	print qq|</td></tr>\n|;

	print qq|</td></tr>\n|;
	print qq|</table><br>\n|;

	&closeform("この日のデータを保存");
}

# ------------------------------------ #
# 月間予定表用シール(定型文)の読み込み #
# ------------------------------------ #
sub loadseals
{
	# ファイルを読む
	open(IN,"$scheduleseals") || return(-1);
	@seals = <IN>;
	close(IN);
}

# ------------------------------------------------------------ #
# 月間予定表用シール(定型文)表示用プルダウンメニュー項目の生成 #
# ------------------------------------------------------------ #
sub showseals
{
	my @sealstrings = ("<option value=\"\"> </option>");

	foreach my $line (@seals) {
		# 実体参照へ変換(Ver2.20追加)
		$line =~ s/</&lt;/g;
		$line =~ s/>/&gt;/g;
		$line =~ s/"/&quot;/g;
		# 表示用配列に追加
		push ( @sealstrings, qq|<option value="$line">$line</option>| );
	}

	print @sealstrings;
}

# ------------------------------------------------------ #
# 月間予定表（カレンダー予定表）の日付選択フォームの表示 #
# ------------------------------------------------------ #
sub editcalendarrecorddisp
{
	my $dispyear = shift @_;
	my $dispmonth= shift @_;
	my $selected = shift @_;
	my @std;

	# 各月の最終日リストを得る
	my @lastdaylist = &calendarpackage::getlastdaylist($dispyear);

	# selected属性の挿入
	if(( $selected > 0 ) && ( $selected <= $lastdaylist[$dispmonth-1] )) {
		# 指定があれば
		$std[$selected-1] = " selected";
	}

	# 指定月の日付リストを作成
	my @selectdays;
	for( my $loop=1 ; $loop<=$lastdaylist[$dispmonth-1] ; $loop++ ) {
		# 指定月の日付分ループ
		push ( @selectdays , qq|<option value="$loop"$std[$loop-1]>$loop</option>| );
	}

	# コンソールフォームの表示
	&loaddata('\[FormTop\]','\[/FormTop\]');
	print qq|<input type="hidden" name="mode" value="editcalendardate">\n|;
	print qq|<input type="hidden" name="edityear"  value="$dispyear">\n|;
	print qq|<input type="hidden" name="editmonth" value="$dispmonth">\n|;

	print qq|$dispyear年 $dispmonth月\n|;

	print qq|<select name="editday">|;
	print @selectdays;
	print qq|</select> 日\n|;

	&closeform("この日のデータを編集");

}

# ---------------------------------------------------------- #
# 月間予定表（カレンダー予定表）の表示月指定用フォームの生成 #
# ---------------------------------------------------------- #
sub showchangecalendarform
{
	my $dispyear = shift @_;
	my $dispmonth= shift @_;

	# コンソール用フォームの生成
	my @selectyears;
	my @selectmonths;

	# 年選択肢の作成
	my @years = ( $dispyear-5,$dispyear-4,$dispyear-3,$dispyear-2,$dispyear-1,
				  $dispyear,
				  $dispyear+1,$dispyear+2,$dispyear+3,$dispyear+4,$dispyear+5 );
	push( @selectyears, qq|<option value="$years[0]">$years[0]</option>| );	# 5年前
	push( @selectyears, qq|<option value="$years[1]">$years[1]</option>| );	# 4年前
	push( @selectyears, qq|<option value="$years[2]">$years[2]</option>| );	# 3年前
	push( @selectyears, qq|<option value="$years[3]">$years[3]</option>| );	# 2年前
	push( @selectyears, qq|<option value="$years[4]">$years[4]</option>| );	# 昨年
	push( @selectyears, qq|<option value="$years[5]" selected>$years[5]</option>| );	# 今年
	push( @selectyears, qq|<option value="$years[6]">$years[6]</option>| );	# 来年
	push( @selectyears, qq|<option value="$years[7]">$years[7]</option>| );	# 再来年
	push( @selectyears, qq|<option value="$years[8]">$years[8]</option>| );	# 3年後
	push( @selectyears, qq|<option value="$years[9]">$years[9]</option>| );	# 4年後
	push( @selectyears, qq|<option value="$years[10]">$years[10]</option>| );	# 5年後
	# 月選択肢の作成
	my @months = ("","","","","","","","","","","","");
	$months[$dispmonth-1] = "selected";
	for( my $loop=1 ; $loop<=12 ; $loop++ ) {
		# 12ヶ月分
		push ( @selectmonths , qq|<option value="$loop" $months[$loop-1]>$loop</option>| );
	}

	# コンソールフォームの表示
	&loaddata('\[FormTop\]','\[/FormTop\]');
	print qq|<input type="hidden" name="mode" value="editcalendar">\n|;
	print qq|<select name="edityear">|;
	print @selectyears;
	print qq|</select>\n|;
	print qq|<select name="editmonth">|;
	print @selectmonths;
	print qq|</select>\n|;
	&closeform("この月のデータを編集");

}

# ---------------------------------------- #
# 月間予定表（カレンダー予定表）の一括削除 #
# ---------------------------------------- #
sub calendardelete
{
	# 月間予定表の一括削除（先月までの全データを削除）
	my $year  = $cedityear;
	my $month = $ceditmonth;

	my $delcount=0;

	# ファイルを読む
	open(IN,"$calendarfile") || &errorexit("月間予\\定ファイル $calendarfile が読めませんでした。");
	my @allshcedule = <IN>;
	close(IN);

	# "先月"の数値を生成
	my $lastmonth = $year * 12 + $month - 1;

	# 書き込み
	open(OUT,"> $calendarfile") || &errorexit("月間予\\定ファイル $calendarfile を書き込みモードで開けませんでした。");
	foreach my $line (@allshcedule) {
		# データを分割
		my ( $ry,$rm,undef ) = split(/\//, ((split(/,/, $line))[0]) );
		# このデータの月の数値を生成
		my $thismonth = $ry * 12 + $rm;

		# 時刻を比較
		if( $lastmonth < $thismonth ) {
			# 削除対象行でなければ書く
			print OUT "$line";
		}
		else {
			# 削除個数をカウント
			$delcount++;
		}
	}
	close(OUT);

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');

	print qq|<p>$delcount個の項目を削除しました。</p>|;

	# 戻るフォームを表示
	&backlink("calender","月間予\\定表\\に戻る");

	&loaddata('\[Foot\]','\[/Foot\]');

}






# ---------------------- #
# ファイル更新時刻を返す #
# ---------------------- #
sub get_timestamp
{
	my $filename = shift @_;

	# ファイル更新時刻を得る
	my $writetime = (stat($filename))[9];

	# 時刻要素に分解する
	my ($sec,$min,$hour,$mday,$month,$year) = (localtime($writetime))[0,1,2,3,4,5];
	$year  = $year + 1900;
	$month = $month + 1;

	# 文字列を返す
	return ("$year/$month/$mday $hour:$min:$sec");
}

# ---------------------------- #
# スクリプト内データの読み出し #
# ---------------------------- #
sub loaddata
{
	my $starttag = shift @_;
	my $endtag = shift @_;

	my $insflag = 0;

	foreach my $line(@datahtml) {

		# 1行ずつ探す
		if( $line =~ m/^$endtag/i ) {
			# 終了点が来たら出力中止
			$insflag = 0;
			# ループからも抜ける
			last;
		}

		if( $insflag == 1 ) {
			# 該当データなら出力（置換キーワードを変換してから出力）
			print &replacekeys($line);
		}
		if( $line =~ m/^$starttag/i ) {
			# 開始点が来たら出力開始
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
# 戻るリンクを作成 #
# ---------------- #
sub backlink
{
	my $linkto = shift @_;
	my $button = shift @_;

	# 未指定だったらデフォルトを代入
	if( $linkto eq "" ) {	$linkto = "";	}
	if( $button eq "" ) {	$button = "作業メニューに戻る";	}

	# 表示
	print qq|<form action="$thiscgi" method="POST">\n|;
	print qq|$encusrpw\n|;
	print qq|<input type="hidden" name="mode" value="$linkto">\n|;
	print qq|<input type="submit" value="$button">\n|;
	print qq|</form>\n|;
}

# -------------- #
# 閉じるフォーム #
# -------------- #
sub closeform
{
	my $button = shift @_;

	# 未指定だったらデフォルトを代入
	if( $button eq "" ) {	$button = "実行";	}

	# 表示
	print qq|$encusrpw\n|;
	print qq|<input type="submit" value="$button">\n|;
	print qq|</form>\n|;
}

# -------------------------------------- #
# 配列中の全文字列からHTMLタグをデコード #
# -------------------------------------- #
sub decodehtmltags
{
	foreach my $line (@_) {
		# HTMLタグをデコード
		$line =~ s/</&lt;/g;
		$line =~ s/>/&gt;/g;
		$line =~ s/\"/&quot;/g;
		# 改行を除去
		$line =~ s/\r//g;
		$line =~ s/\n//g;
	}

	return @_;
}









# ------------------------------ #
# 致命的ではないエラーメッセージ #
# ------------------------------ #
sub errorback
{
	my $msg = shift @_;

	&loaddata('\[Head\]','\[/Head\]');
	&loaddata('\[BodyTop\]','\[/BodyTop\]');
	print qq|<p><span class="error">$msg</p>\n|;
	print qq|<form><input type="button" value="直前の画面に戻る" onClick="history.back();"></form>|;
	&loaddata('\[Foot\]','\[/Foot\]');
}

# ---------------- #
# エラーメッセージ #
# ---------------- #
sub errorexit
{
	$msg = shift @_;

	print qq|<html lang="ja"><head><title>Fumy Teacher's Schedule Board ERROR</title></head><body>\n|;
	print qq|<div style="background-color:red; color:#fffff0; font-weight:bold; font-family:Arial,sans-serif; padding:1px;">Fumy Teacher's Schedule Board CGI Error! </div><br>\n|;
	print qq|<div style="font-size: smaller;">エラー内容：</div>\n|;
	print qq|<div style="border:1px dotted blue; padding:1em;">$msg</div>\n|;
	print qq|<div style="text-align: right;"><form><input type="button" value="戻る" onClick="history.back();"></form></div>|;
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
	<title>消防団予定表 - ADMIN MODE</title>
	<link rel="stylesheet" type="text/css" href="CSSFILENAME">
</head>
[/Head]
[BodyTop]
<body>
<h1>スケジュール編集パネル <span class="appname"> - 消防団予定表 (Ver 2.3.0)</span></h1>
<div class="main">
DEMONSTRATIONMESSAGE
[/BodyTop]
[FormTop]
<form action="CGINAME" method="POST">
[/FormTop]
[FormBottom]
	ENCORDEDUSERPASSWORD
	<input type="submit" value="編集内容を保存">
	<input type="button" value="保存せずに戻る" onClick="history.back();">
</form>
[/FormBottom]
[Login]
<p class="login">LOGINMESSAGES</p>
<div class="login">
	<form action="CGINAME" method="POST">
		<input type="password" name="pw">
		<input type="hidden" name="mode" value="home">
		<input type="submit" value="ログイン">
	</form>
	<p class="notice">パスワードを忘れた場合：</p>
	<ul class="notice">
		<li>【パスワード固定で設置した場合】CGIのソースを覗けばパスワードが分かります。</li>
		<li>【パスワード変更可能で設置した場合】パスワード格納ファイルの中身を空っぽにしてアップロードし直すことで、新しくパスワードを作ることができます。</li>
	</ul>
</div>
[/Login]
[Foot]
</div>
</body>
</html>
[/Foot]
▲高頻度

低頻度▼
[First]
<p class="title">作業内容を選択して下さい。</p>
<form action="CGINAME" method="POST">
	<table class="menudesign">
	<tr><td><input type="radio" name="mode" value="weekly"   id="mw"><label for="mw">1週間の汎用予定表を編集</label></td><td><span class="note">（最終更新： MODIFYTIME-WEEKLY）</span></td></tr>
	<tr><td><input type="radio" name="mode" value="calender" id="cd" checked><label for="cd">月間予定表（カレンダー予定表）を編集</label></td><td><span class="note">（最終更新： MODIFYTIME-CALENDAR）</span></td></tr>
	<tr><td><input type="radio" name="mode" value="long"     id="lg"><label for="lg">長期予定を編集</label></td><td><span class="note">（最終更新： MODIFYTIME-LONGLY）</span></td></tr>
	<tr><td><input type="radio" name="mode" value="cpw"      id="cp"><label for="cp">パスワードを変更</label></td><td></td></tr>
	</table>
	<br>
	ENCORDEDUSERPASSWORD
	<input type="submit" value="選択した作業を実行">
</form>
[/First]

[ChangePW]
<p class="title">パスワードを変更します。現在のパスワードと、希望する新しいパスワードを入力して下さい。</p>
<form action="CGINAME" method="POST">
	<input type="hidden" name="mode" value="dochangepw">
	<table class="menudesign">
		<tr><td>現在のパスワード：</td><td><input type="password" name="nowpw"></td></tr>
		<tr><td>新しいパスワード：</td><td><input type="password" name="newpw"></td></tr>
	</table>
	<br>
	<input type="submit" value="パスワードを変更">
	<input type="button" value="戻る" onClick="history.back();">
	</table>
	ENCORDEDUSERPASSWORD
</form>
<p><span class="note">※パスワードは暗号化して保存されます。管理者にも解読はできませんので、忘れないように注意して下さい。</span></p>
[/ChangePW]

[MakePW]
<p class="title">ようこそ、Fumy Teacher's Schedule Boardへ！<br>まず、<strong>ログイン用のパスワードを設定(登録)</strong>します。希望するパスワードを下記に入力して下さい。</p>
<form action="CGINAME" method="POST">
	<input type="hidden" name="mode" value="dochangepw">
	希望するパスワード：</td><td><input type="password" name="newpw"><br>
	<br>
	<input type="submit" value="パスワードを登録">
</form>
<p><span class="note">※パスワードは暗号化して保存されます。管理者にも解読はできませんので、忘れないように注意して下さい。<br>※パスワードを0文字にはできません。</span></p>
[/MakePW]
