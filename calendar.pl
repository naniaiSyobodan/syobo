#! /usr/bin/perl

use lib qw(./);
use DBI;

#vデータベース接続
#my $server = "localhost";
my $server = "mysql303.phy.lolipop.lan";
#my $userName = "kyum";
my $userName = "LAA1590428";
#my $password = "k1lt7Ovl";
my $password = "k1lt7Ovl";
#my $dbName = "kyum";
my $dbName = "LAA1590428-kyum";
my $dbConnect = "DBI:mysql:" . $dbName . ":" . $server;


# ================================================================== #
#  Fumy Teacher's Schedule Board   Ver 2.3.0   [calendar.pl]         #
# ================================================================== #
#  Copyright (C) Fumihiro Nishimura.(Nishishi) 2004-2016.            #
#                                                                    #
#  スケジュール表示フリーCGIです。(このファイルは補助CGI)            #
#  著作権は、西村文宏(にしし)にあります。                            #
#  このCGIは誰でも自由にご使用頂けます。商用・非商用を問いません。   #
#  著作権表示を削除・改変せずにご使用下さい。                        #
#                                                                    #
#  http://www.nishishi.com/                                          #
# ================================================================== #

package calendarpackage;

use Time::Local;

# ================ #
#  ▼ユーザ設定▼  #
# ================ #

# 祝日ファイル名
my $holidaysfile = "holidays.txt";

# 曜日の表記（日曜日～土曜日まで）
my $sunday    = '日';
my $monday    = '月';
my $tuesday   = '火';
my $wednesday = '水';
my $thursday  = '木';
my $friday    = '金';
my $saturday  = '土';

# HTMLタグの無効化（1=無効化する／0=無効化しない）
$voidtags = 0;

# ======================== #
#  ▲ユーザ設定ここまで▲  # ※ここから下を書き換える必要はありません。
# ======================== #

# 変数
$calendarfile = "calendar.txt";		# デフォルトの月間予定ファイル名
@calendardata;	# 月間予定ファイルの中身

#&makecalendar("2020","03","yotei.txt");

# ---------------- #
# 月間予定表の生成 #　（外部から呼び出すサブルーチンはこれ。）
# ---------------- #
sub makecalendar
{
	# カレンダー生成
	my $calendaryear 	= shift @_;	# 表示年
	my $calendarmonth	= shift @_;	# 表示月
	my $TargetCheck		= shift @_;	# 班絞り込みのためのSQL文の一部

	# カレンダーを表示
	&showcalendar( $calendaryear, $calendarmonth,$TargetCheck);
}

# 予定表ファイルを読んで必要な予定だけを抜き出す処理
sub loadcalendar
{
	my $calendaryear = shift @_;	# 表示年
	my $calendarmonth= shift @_;	# 表示月
	my $calendarfile = shift @_;	# 月間予定ファイル名

	# ファイルを読む
	open(IN,"$calendarfile") || return(-1);
	my @allshcedule = <IN>;
	close(IN);

	# 全予定から特定月の予定だけを抜き出す
	my $seachstring = "$calendaryear$calendarmonth";
	foreach my $rec ( @allshcedule ) {
		if( $rec =~ m/^$seachstring/i ) {
			# 指定月の予定なら配列にコピー
			push(@calendardata,$rec);
		}
	}
}

# -------------- #
# カレンダー表示 #
# -------------- #
sub showcalendar
{
	# カレンダー表示
	my $cyear = shift @_;	# 表示年
	my $cmonth= shift @_;	# 表示月
	my $TargetCheck	= shift @_;	# 班絞り込みのためのSQL文の一部
	my @lastdaylist;		# 各月の最終日リスト
	my @days;				# 表示月の全日リスト
	my @monthschedules;		# 表示月に限定した予定リスト

	# 表示月1日の曜日を得る（Sun=0,Mon=1,Tue=2...）
	$weekday = (localtime( timelocal(0, 0, 12, 1, $cmonth - 1, $cyear) ))[6];

	# 各月の最終日リスト
	@lastdaylist = &getlastdaylist($cyear);

	# 表示月の全日リスト
	for( my $loop=1 ; $loop<=$lastdaylist[$cmonth-1] ; $loop++ ) {
		# 1からその月の最終日までのリストを作る
		push( @days, $loop );
	}
	for( my $loop=0 ; $loop<$weekday ; $loop++ ) {
		# その月の1日の曜日まで空白を追加する（1日が日曜日なら0個、月曜日なら1個、土曜日なら6個追加する）
		unshift( @days, 0 );
	}

	# 必要な週の数を決める
	my $needcells;
	if( $#days < 35 ) {
		# 5週分で良ければ
		$needweeks = 5;
	}
	else {
		# 6週分必要なら
		$needweeks = 6;
	}

	# 全日リストの末尾に空白を加えておく（最大6個）
	@days = ( @days, 0, 0, 0, 0, 0, 0 );

	# Captionを作成
	#my $captionstring = "<a href=\"admin.cgi?mode=\"editcalendar\"&edityear=\"cyear\"&editmonth=\"cmonth\">$cyear年 $cmonth月</a>";	
	my $captionstring = "$cyear年 $cmonth月";	

	# 表形式のカレンダーを生成する
	# HTML
	print << "EOM";

<table class="monthly"><!--caption>$captionstring</caption-->
<tr>
	<th class="sunday">$sunday</th>
	<th class="weekdays">$monday</th>
	<th class="weekdays">$tuesday</th>
	<th class="weekdays">$wednesday</th>
	<th class="weekdays">$thursday</th>
	<th class="weekdays">$friday</th>
	<th class="saturday">$saturday</th>
</tr>
EOM

	my $furikaeflag = 0;		# 振り替え休日フラグ
	my $yesterdayholidayflag = 0;	# 前日が祝日な場合のフラグ
	my $nationalpeoplesdayflag = 0;	# 国民の休日フラグ（＝祝日と祝日に挟まれた日：ただし片方が日曜日・振り替え休日の場合は除く）

	#$startDate = "$cyear-$cmonth-01";
	#$lastDate = "$cyear-$cmonth-31";
	#where Date BETWEEN '$startDate' AND '$lastDate' $TargetCheck
	
	$destDate = "$cyear-$cmonth";

	my $sqlStr = << "EOS";	# Query文編集
	SELECT Date,GyojiMei,StartTime,EndTime,Sanka 
	FROM sybo_gyoji 
	where DATE_FORMAT(Date, '%Y-%m') = '$destDate' $TargetCheck
	order by Date,StartTime;
EOS

	my $bRowEnd = false;
	$db = DBI->connect($dbConnect, $userName, $password);
	$db->do("set names utf8");

	$sth = $db->prepare($sqlStr);
	my $rv = $sth->execute;

#print qq|calender [ $sqlStr ]rv=$rv<tr>|;

	my $hash_ref = $sth->fetchrow_hashref;	#先頭行事データ読込

	for( my $loopweeks=1 ; $loopweeks<=$needweeks ; $loopweeks++ ) {
		# 必要週分ループ（5週か6週か）
		print qq|<tr>|;

		for( my $loopdays=1 ; $loopdays<=7 ; $loopdays++ ) {
			# 7回ループ（1週間分）
			my $daynum = shift @days;	# 日付

			# ------------------------------ #
			# 日付セルの生成：曜日・祝日判定 #
			# ------------------------------ #
			print "\n";

			# 今日の祝日判定
			my $ih = &isholiday( $cyear, $cmonth, $daynum );

			# 国民の休日判定（※Ver2.20更新：祝日が3日連続する場合には中日を国民の休日とはしない）
			if( $yesterdayholidayflag == 1 ) {
				# 昨日が休日の場合は、翌日が祝日かどうかを調べる
				if( &isholiday( $cyear, $cmonth, $daynum+1 ) ne "NH" ) {
					# 翌日も祝日だったら、今日は国民の休日の可能性がある
					if( &isholiday( $cyear, $cmonth, $daynum ) eq "NH" ) {
						# 今日が元々祝日でなければ、今日は国民の休日
						# 国民の休日フラグを立てる
						$nationalpeoplesdayflag = 1;
						$ih = "国民の休日";
					}
					else {
						# 今日も祝日なら、国民の休日にはならず規定の祝日
					}
				}
				# "昨日が祝日"フラグを降ろす
				$yesterdayholidayflag = 0;
			}

			# 曜日・祝日別処理
			if( $ih ne "NH" ) {
				# 祝日
				print qq|<td class="holiday" valign="top">|;

				# 国民の休日関連処理
				if( $nationalpeoplesdayflag == 0 ) {
					# "国民の休日"以外の祝日の場合は、祝日フラグを立てる
					$yesterdayholidayflag = 1;
				}
				else {
					# 今日が"国民の休日"の場合は、国民の休日フラグを降ろす
					$nationalpeoplesdayflag = 0;
				}

				# 振り替え休日関連処理
				if( $loopdays == 1 ) {
					# 祝日が日曜日だったら振り替え休日処理フラグを立てる
					$furikaeflag = 1;
				}
				elsif( $furikaeflag == 1 ) {
					# 既に振り替え休日フラグが立っていたら降ろす（＝祝日の前日が祝日の場合、振り替えしない）
					# $furikaeflag = 0;
					# ※Ver2.20更新：振替休日は月曜日とは限らなくなったためこの処理は削除（日曜日以降の祝日ではない日が振替休日）
				}
			}
			elsif( $loopdays == 1 ) {
				# 日曜日
				print qq|<td class="sunday" valign="top">|;
			}
			elsif( $loopdays == 7 ) {
				# 土曜日
				print qq|<td class="saturday" valign="top">|;
			}
			else {
				# 平日
				if( $furikaeflag == 1 ) {
					# 振り替え休日だったら
					print qq|<td class="holiday" valign="top">|;
					$ih = "振り替え休日";
					# 振り替え休日フラグを降ろす
					$furikaeflag = 0;
				}
				else {
					# 平日なら
					print qq|<td class="weekdays" valign="top">|;
				}
			}
			# -------------------------------- #
			# 日付セルの生成：日付・予定を表示 #
			# -------------------------------- #
			# 1日分のセルを生成
			if( $daynum == 0 ) {
				# 存在しない日付なら空白にする
				print qq|&nbsp;<br>|;
			}
			else {
				# 日付を表示
				print qq|<b>$daynum</b>|;
				# 祝日名を表示
				if( $ih ne "NH" ) {
					print qq|<span class="holname">$ih</span>|;
				}
				
				my $curDate = sprintf("%04d-%02d-%02d",$cyear,$cmonth,$daynum);
				my $PicDate;
				
				if($bRowEnd eq false) {		# データが終了していたら何もしない
					# その日のデータを探す
					while( $bRowEnd eq false ) {

						# 次のレコードを取得
						if($hash_ref eq undef) {
							$bRowEnd = true;
						}
						else {
							my %row = %$hash_ref;
							if( $curDate  eq $row{Date} ) {
								print "<br>";		# 予定を表示
								$one = $row{GyojiMei};	# 行事取り出し
								print &exchangetohtml( $one );
							}
							elsif( $curDate lt $row{Date} ) {
								last;
							}
							#同じ日に複数行事があることもある
							$hash_ref = $sth->fetchrow_hashref;	#次の行事データ読込
						}
					}
				}
			}
			print qq|</td>|;

		}	# END OF FOR LOOP

		print qq|</tr>|;
	}

	print << "EOM";

</table>

EOM

}

# ------------------------ #
# 各月の最終日リストを得る #
# ------------------------ #
sub getlastdaylist
{
	my $cyear = shift @_;
	my @lastdaylist;

	# 各月の最終日リスト
	if( &checkleapyear($cyear) == 0 ) {
		# 閏年ではない場合
		@lastdaylist = ( 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 );
	}
	else {
		# 閏年な場合
		@lastdaylist = ( 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 );
	}

	return @lastdaylist;
}

# ------------ #
# 閏年チェック #　（戻り値： 0=閏年でない／1=閏年である）
# ------------ #
sub checkleapyear
{
	# うるう年チェック
	my $year = shift @_;

	# 400で割り切れるか？
	if( $year % 400 == 0 ) {
		# 閏年
		return 1;
	}

	# 100で割り切れるか？
	if( $year % 100 == 0 ) {
		# 閏年でない
		return 0;
	}

	# 4で割り切れるか？
	if( $year % 4 == 0 ) {
		# 閏年
		return 1;
	}

	# それ以外は閏年でない
	return 0;
}

# --------------------- #
# 1日の予定をHTMLに展開 #
# --------------------- #	Ver 2.20：HTMLタグの無効化オプションを追加
sub exchangetohtml
{
	# 1日の予定をHTMLに展開
	my $dayschedule = shift @_;

	# HTMLタグを無効化する場合は実体参照に置き換え
	if( $voidtags == 1 ) {
		$dayschedule =~ s/</&lt;/g;
		$dayschedule =~ s/>/&gt;/g;
		$dayschedule =~ s/"/&quot;/g;
	}

	# 改行タグを加える
	$dayschedule =~ s/<>/<br>/g;
	$dayschedule =~ s/&lt;&gt;/<br>/g;	# HTML無効化時用

	# 末尾の改行コードを削除
	$dayschedule =~ s/\n//g;
	$dayschedule =~ s/\r//g;

	return $dayschedule;
}

# ---------- #
# 祝日の判定 #	返り値： "NH" or "祝日名" （NH：Not a Holiday）
# ---------- #
sub isholiday
{
	# 祝日かどうかを判定
	my $year = shift @_;
	my $month= shift @_;
	my $date = shift @_;
	my $week;

	# 返り値
	my $retstring = "NH";

	# 祝日ファイルを読む
	open(IN,"$holidaysfile") || return($retstring);
	my @holidays = <IN>;
	close(IN);

	# 祝日リストから今月のものだけを抜き出す（ループ量削減のため）
	# ★祝日リストは昇順にソート済みであることが前提
	my @thismonthholidays;
	my $searchstring = "$month/";
	my $findflag = 0;
	foreach my $one (@holidays) {
		if( $one =~ m/^$searchstring/i ) {
			# 見つかったら配列にコピー
			push( @thismonthholidays, $one );
			$findflag = 1;
		}
		else {
			# 既に指定月を過ぎていたら、それ以降にはないと考え、ループ終了
			if( $findflag == 1 ) {
				last;
			}
		}
	}

	# 祝日かどうかの判定
	foreach my $onehol (@thismonthholidays) {
		# 日付と祝日名に分割
		my( $ohcal, $holidayname ) = split(/,/, $onehol );
		# 日付を月と日に分割
		my( $ohmon, $ohdate ) = split(/\//, $ohcal );

		# 曜日指定だったら日に展開
		if( $ohdate =~ m/M(\d)/i ) {
			$ohdate = &exchangeweektoday($year,$ohmon,$1);
		}

		# 春分の日・秋分の日だったら計算
		if( $ohcal =~ m/^(\d)\/S/i ) {
			$ohdate = &exchangevaequinox($year,$1);
		}

		# 現在調べようとしている日付と一致しているか判定
		if( $date == $ohdate ) {
			# 日が一致
			if( $month == $ohmon ) {
				# 月が一致
				# 祝日名を返してループ終了
				$retstring = $holidayname;
				last;
			}
		}
	}

	return $retstring;
}

sub exchangevaequinox
{
	# 春分の日・秋分の日だったら計算
	my $year = shift @_;	# 年
	my $month= shift @_;	# 月

	my $ret = -1;

	# 春分の日
	if( $month == 3 ) {
		$ret = int ( 20.8431 + 0.242194 * ( $year - 1980 ) - int (  ( $year - 1980 ) / 4 ) );
	}
	elsif( $month == 9 ) {
		$ret = int ( 23.2488 + 0.242194 * ( $year - 1980 ) - int (  ( $year - 1980 ) / 4 ) );
	}

	return $ret;
}

sub exchangeweektoday
{
	# 曜日での指定の場合、日付に展開
	my $year = shift @_;	# 年
	my $month= shift @_;	# 月
	my $week = shift @_;	# 週（第n週／n:1～5）

	my $ret;	# 変換後の「日」格納用

	# 表示月1日の曜日を得る（Sun=0,Mon=1,Tue=2...）
	$weekday = (localtime( timelocal(0, 0, 12, 1, $month - 1, $year) ))[6];

	# 月曜日群リスト
	my @mos = (1,8,15,22,29);	# 1日が月曜日の場合の月曜日群
	my @tus = (7,14,21,28);		# 1日が火曜日の場合の月曜日群
	my @wes = (6,13,20,27);		# 1日が水曜日の場合の月曜日群
	my @ths = (5,12,19,26);		# 1日が木曜日の場合の月曜日群
	my @frs = (4,11,18,25);		# 1日が金曜日の場合の月曜日群
	my @sas = (3,10,17,24,31);	# 1日が土曜日の場合の月曜日群
	my @sus = (2,9,16,23,30);	# 1日が日曜日の場合の月曜日群

	# 1日が日曜日
	if( $weekday == 0 )		{	$ret = $sus[$week-1];	}
	# 1日が月曜日
	elsif( $weekday == 1 )	{	$ret = $mos[$week-1];	}
	# 1日が火曜日
	elsif( $weekday == 2 )	{	$ret = $tus[$week-1];	}
	# 1日が水曜日
	elsif( $weekday == 3 )	{	$ret = $wes[$week-1];	}
	# 1日が木曜日
	elsif( $weekday == 4 )	{	$ret = $ths[$week-1];	}
	# 1日が金曜日
	elsif( $weekday == 5 )	{	$ret = $frs[$week-1];	}
	# 1日が土曜日
	elsif( $weekday == 6 )	{	$ret = $sas[$week-1];	}

	return $ret;
}





1;
