#!/usr/local/bin/perl
use lib qw(./);
use DBI;
use CGI;

#JustSizeでは「! /usr/bin/perl」としていた

use open qw/:utf8/;	#	ファイル一括読み込み

my $IsAdmin = false;
my $IsDebug = false;
my $ThisURI		= "kyum.chu.jp";
my $ThisScCgi	= "sc.cgi";

my $LinkDetail	= "ShowGyoji";

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

$IMGMAX		= 2 * 1000 * 1000;		#画像サイズ制限(バイト)

# ================ #
#  ▼ユーザ設定▼  #
# ================ #

# 環境ファイル名
my $configfile = "config.txt";
# 団員名格納ファイル名
my $memberfile = "member.txt";
# Newsのファイル名
my $NewsFileName = "./News.txt";

# 表示させる月数
my $wantshowmonth = 1;

# カレンダー表示用パッケージを呼ぶ
require 'calendar.pl';

# 日時入力用パッケージを呼ぶ
require '../cmn/datefuncs.pl';

my $mode;			# 動作モード
my $startym = "";	# 表示開始年月の保持
my $gCurYY	= "";	# 表示年の保持
my $gCurMM	= "";	# 表示月の保持
my $recno;			# レコード番号
my $gNendo	= "";	# 表示年年度の保持
my $NendoMax	= 0;
my $NendoMin	= 0;
my $cokHanNo	= -1;	# cookieから読み込んだ班番号
my $bHanChange	= false;
#対象となる班の指定
my $HAN_CNT = 11;
my @HanList = ("分団本部","１区","２区","３区","４区","５区","６区","７区","８区","９区","１０区");	# 分類リスト

# HanListの選択番号 未指定ならば３区,Bit2 が選択されているものとする
my $HanNo	= 3;
my $HanBit = 1;

my $HanSitei=false;	
my $TargetCheck = "and (TargetFlags & $HanBit) > 0";
my $Hanmei = @HanList[$HanNo];
my $HanAll = "七二会分団全";

#選択肢となる文字列の配列
my @seals = ("分団会議","分団活動","長野団行事","班活動","火災出動","訓練","警戒","広報車");	# 分類リスト
my @FukusoList = ("服装:自由","活動服","法被上着","乙種完全","その他");		# 服装リスト
my @AtamaList = ("頭：自由","ヘルメット","警帽","アポロキャップ","その他");	# 帽子リスト
my @ShoseList = ("靴:自由","長靴","編上靴","その他");	# 靴リスト
my $voidtags = $calendarpackage::voidtags;	# HTMLタグの無効化設定(calendar.plの値を使用)

my $rdCount=0;	#読込カウンタ .. 明細で旧データがあるかの判定で使用
my $rdNo=0;
my $rdDate="";
my $rdStartTime="";
my $rdEndTime="";
my $rdBunrui="";
my $rdGyojiMei="";
my $rdSanka="";
my $rdSyugo="";
my $rdAtama=0;
my $rdFukuso=0;
my $rdKutsu=0;
my $rdMemo="";
my $rdYear	= "";
my $rdMonth= "";
my $rdDay= "";
my $rdTargets=0;
my $SrcFile= "";
my $EditNewsText = "";

my $db;	#データベースアクセスクラス

# InputGyoji で使用する引数の規定値
use constant INPUT_MODE_NEW => 1;
use constant INPUT_MODE_UPDATE => 2;

use constant ENTRY_MODE_ADM => 1;
use constant ENTRY_MODE_HAN => 2;

#ShowNendolist で使用する引数の規定値
use constant SHOW_MODE_GYOJI => 0;
use constant SHOW_MODE_SANKA => 1;

use constant NENDO_SEL_LINK => 0;
use constant NENDO_SEL_INPUT => 1;

use constant TARGET_ALL_DATA => 2047;

#クッキーからパスワードを取得
foreach $pair (split(/;\s*/, $ENV{'HTTP_COOKIE'})) {
    my    ($name, $cookie) = split(/=/, $pair);
    if(($name eq "syobopass") && ($cookie eq "hancyo")) {
		$IsAdmin = true;
		$LinkDetail = "editgyoji";
	}
    if(($name eq "syobodebug") && ($cookie eq "on")) {
		$IsDebug = true;
	}
    if($name eq "hanno") {
		$cokHanNo	= $cookie;
	}
}

#フォームデータ取り込み
if($ENV{'REQUEST_METHOD'} eq 'POST') {
	&splitPost();	#ファイルUpload用
}
else {
	&splitGet();	# パラメータの分解
}


# ヘッダ
print "Content-type: text/html\n\n\n";

print qq|<!DOCTYPE html><html lang="ja">\n|;
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
print qq|<head>\n|;		# ■■■■■■ ＨＥＡＤ ■■■■■■
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
print qq|\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n|;
print qq|\t<meta name="viewport" content="width=device-width, initial-scale=1">\n|;

#Windows
#
#Windows 環境では、ActivePerl の Perl Package Manager からインストールします。
#1.スタートメニューから、Perl Package Manager を実行します。
#2.データベース・インターフェイス等、Movable Type に必要なモジュールをインストールします。
#3.モジュールのインストールが終了したら、exit コマンドを実行して終了します。
#
#モジュール名が不明の場合、search コマンドを実行して確認します。たとえば、MySQL を利用するために必要なモジュール DBI と DBD::MySQL は、次のようにインストールします。
# ┌─────────────────────────┐
# │ppm> install DBI			│
# │ppm> install DBD-mysql	│
# └─────────────────────────┘


print qq|
	<title>$Hanmeiのスケジュール</title>
	<script type="text/javascript" src="sc.js"></script>
	<link rel="stylesheet" type="text/css" href="schedule.css">
	<link href="https://use.fontawesome.com/releases/v5.15.1/css/all.css" rel="stylesheet">
	<style>
			/*ハンバーガーアイコン*/
		.btn-burger {
		  cursor: pointer;
		  display: block;
		  width: 56px;
		  height: 60px;
		  position: absolute;
		  top: 5px;
		  right: 10px;
		}

		/*ハンバーガーアイコンを作る三本線*/
		.top-icon, .top-icon:before, .top-icon:after {
		  position: absolute;	/* absolute:絶対位置への配置 */
		  top: 0;
		  right: 0;
		  left: 0;
		  bottom: 0;
		  height: 2px; /*線の太さ*/
		  width: 35px; /*線の長さ*/
		  background-color: #444;
		  border-radius: 2px;	/* 矩形で線モドキを書く */
		  display: block;
		  content: '';
		  font-size: 0.85em;
		  cursor: pointer;
		  margin: auto;
		}

		/*三本線の間隔*/
		.top-icon:before {	/* top-icon スタイルが適用される直前の疑似要素 */
			content: 'MENU';
			/*top: 20px;*/
		}
		.top-icon:after {	/* top-icon スタイルが適用された直後の疑似要素 */
			content: '';
			top: -20px;
		}

		/*チェックボックス非表示*/
		.nav-toggle {
			display: none;
		}

		/*アイコンをクリックしたら*/
		.nav-toggle:checked ~ .btn-burger .top-icon {	/* '~'は一般兄弟結合子と言い、関連する要素を選択するときに使う。 */
														/* .btn-burger と .top-icon に対して checked されたら　  */
			background: transparent;					/* 線を消す */
			/*transform: rotate(25deg);					/* beforeの線を45°傾ける */
			border-radius: 10px;	/* 矩形で線モドキを書く */
		}
		.nav-toggle:checked ~ .btn-burger .top-icon:before {
			/*transform: rotate(-15deg);				/* beforeの線を45°傾ける */
			top: -20;									/* 線を中心線に重ねる */ 
			font-size: 0.8em;
			content: 'CLOSE';
			/*transform: rotate(0deg);					/* beforeの線を45°傾ける */
		}
		.nav-toggle:checked ~ .btn-burger .top-icon:after {
			/*transform: rotate(15deg);					/* afterの線を25°傾ける */
			/*transform: rotate(45deg);					/* afterの線を45°傾ける */
			top: -20;										/* 線を中心線に重ねる */ 
		}

		.top-icon,
		.top-icon:before,
		.top-icon:after {
			transition: all .8s;	/* 変化させる時間 */
		}

		/*中身*/
		.nav {
			background-color: #91b0b6;
			
		}
		.nav-list a {
			display: block;
			text-decoration: none;
			color: #fff;
		}

		.nav-list {
			list-style: none;
			display: none;
			margin: 0;
			padding-left: 20px;
		}

		.nav-list li {
			margin: 0;
			padding: 10px;
		}

		.nav-toggle:checked ~ .nav .nav-list {
			display: block;
		}

		/*メインイメージ*/
		.top {
			height: 200px;
			margin-bottom: 50px;
			background-color: #f0f8ff;
		}

		/* --------------------------------------------------
		  幅768px以上のスタイル指定 ここから
		-------------------------------------------------- */
		@media screen and (min-width: 768px) {

			.nav {
				background-color: #d4cd60;
				border: 3px inset #5ecafc;
			}

			/* ハンバーガーボタン */
			.btn-burger {
				display: none;  /*768px以上では使用しない */
			}
			header {
				padding: 30px 0 0;
			}
			.logo {
				width: auto;
				margin: 0 0 20px;
				padding: 0;
				text-align: center;
			}
			.nav-toggle:checked ~ .nav .nav-list {
				display: none;
			}
			.nav {
				height: 75px;
			}
			.nav-list {
				display: flex;
				justify-content: center;
				height: 75px;
				align-items: center;
			}
			/*.nav-list li:not(:last-child) { last-child指定は最後のメニューだけ別動作にしたいときに定義する */
			.nav-list li {
				color:  #11101f;
				background: #2e864d;
				background: -webkit-gradient(linear, left bottom, left top, color-stop(50%, #1b7e40), to(#20b958));
				border: 3px inset #728cc7;
				border-right: 1px solid #fff;
				border-radius: 1rem;
				margin-left: 2px;
			}
		}
		a.btn--upload {
			background-color: #61eb00;
		}
		
		
		/* [必須]マーク */
		.RequiredLabel:after {
			margin-left: 1.0em;
			padding: 0px 6px 0px 6px;
			border-radius: 4px;
			font-size: 0.6em;
			color: white;
			background-color: #C44;
			display: inline-block;
			_display: inline;
			white-space: nowrap;
			content: "必須";
		}		

		.cp_iptxt {
			position: relative;
			width: 80%;
			margin: 40px 3%;
		}
		.cp_iptxt input[type=text] {
			/*font: 15px/24px sans-serif;*/
			box-sizing: border-box;
			width: 100%;
			/*margin: 8px 0;*/
			padding: 0.3em;
			transition: 0.3s;
			border: 1px solid #1b2538;
			border-radius: 4px;
			outline: none;
		}
		.cp_iptxt input[type=text]:focus {
			border-color: #da3c41;
		}
		.cp_iptxt input[type=text] {
			padding-left: 4px;	/* 入力TEXTの開始位置 */
		}
		.cp_iptxt i {
			position: absolute;
			top: 8px;
			left: 0;
			padding: 9px 8px;
			transition: 0.3s;
			color: #aaaaaa;
		}
		.cp_iptxt input[type=text]:focus + i {
			color: #da3c41;
		}
		
		/* 基本のセレクトボックスのカスタマイズ */
		.date_sel {
			background: #cfce42;
			height: 2.2em;
			width: 4em;
			border-radius: 2px;
			position: relative;
			z-index: 1;
		}

		.date_sel::after {
			position: absolute;
			content: '';
			width: 2px;
			height: 2px;
			right: 10px;
			top: 50%;
			transform: translateY(-50%) rotate(45deg);
			border-bottom: 2px solid #fff;
			border-right: 2px solid #fff;
			z-index: -1;
		}

		date_sel {
			/* 初期化 */
			appearance: none;
			-moz-appearance: none;
			-webkit-appearance: none;
			background: none;
			border: none;
			color: #333;
			/*font-size: 16px;*/
			width: 100%;
			height: 100%;
			padding: 0 3px;
		}
		//	参加対象班のマーク
		.taiMaruHon {
			text-align: center;
		}
		.taiMaruHon::after {
			content: "部";
			color: #2040A0;
			font-size: 8px;
		}
		.taiMaruHan {
			text-align: center;
		}
		.taiMaruHan::after {
			content: "区";
			color: #2040A0;
			font-size: 8px;
		}
		
		/* 新着情報リスト */
		.main-container {
		  margin: 0 auto;
		}
		.main-section {
		  max-width: 1200px;
		  margin: 0 auto;
		  padding: 35px 20px 40px;
		}

		/*=== お知らせ ===*/
		.info .main-section {
		  max-width: 740px;
		  line-height: 1.4;
		}
		.info > ul {
		  padding-left: 10px;
		}
		.info-head {
		  padding: 10px 15px;
		  color: #fff;
		  background-color: #ec6c00;
		  border-radius: 16px 16px 0px 0px;
		}
		.info-ttl {
		  font-weight: bold;
		  font-size: 22px;
		}
		.info-cont {
		  padding: 10px 15px;
		  background-color: #faf8f0;
		}
		.info-area {
		  height: 200px;
		  padding-right: 10px;
		  overflow: auto;
		}
		.info-area > li:not(:first-child) {	/* 行間の罫線 */
		  margin-top: 15px;
		  padding-top: 15px;
		  border-top: 1px solid #ddd;
		}
		.info-data {
		 font-size: 0.7em;
		 height: 0em;
		}
		.info-txt {
		 font-size: 1.2em;
		 color: #914b1a;
		 margin-bottom: 4px;
		}
		.info-list {
		  padding-left: 1em;
		  text-indent: 1em;
		}
		.info-list li {
		  /*margin-top: 5px;*/
		  padding-left: 0.4em;
		  text-indent: -1em;
		  list-style-type: none;
		}


		@media screen and (max-width: 768px) {
		  /*=== メインエリア ===*/
		  /*=== お知らせ ===*/
		  .info .main-section {
			padding: 40px 10px 0;
		  }
		  .info-head {
			padding: 8px 10px;
		  }
		  .info-ttl {
			font-size: 16px;
		  }
		  .info-cont {
			padding: 10px;
			font-size: 13px;
		  }
		  .info-area > li:not(:first-child) {
			margin-top: 10px;
			padding-top: 10px;
		  }
		}

	.pagetop {
		height: 50px;
		width: 50px;
		position: fixed;
		right: 30px;
		bottom: 30px;
		background: rgba(255, 255, 255, 0.5);
		border: solid 2px #000;
		border-radius: 50%;
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 2;
		box-shadow: 0 4px 6px rgb(0 0 0 / 30%);
	}

	.pagetop__arrow {
		height: 10px;
		width: 10px;
		border-top: 3px solid #000;
		border-right: 3px solid #000;
		transform: translateY(20%) rotate(-45deg);
	}
	@media (hover: hover) and (pointer: fine) {
		.pagetop:hover, .pagetop:hover .pagetop__arrow {
			border-color: #3293e7;
		}
	}	
	.group_box {
		position: relative;
		margin: 2em 0;
		padding: 0.5em 1em;
		border: solid 3px #75aacc;
		border-radius: 8px;
	}
	.group_box .box-title {
		position: absolute;
		display: inline-block;
		top: -13px;
		left: 10px;
		padding: 0 9px;
		line-height: 1;
		font-size: 19px;
		background: #EEEE88;
		color: #406060;
		font-weight: bold;
	}
	.group_box a {
		margin-top: 4px; 
		padding: 2px;
		color: #fff;
		background-color: #eb6100;
		border-bottom: 5px solid #b84c00;	
	}
	</style>

  
  
	<script>
		if (document.location.search.match(/type=embed/gi)) {
			window.parent.postMessage("resize", "*");
		}
	</script>|;

print qq|</head>\n|;
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
print qq|<body|;	# ■■■■■■ ＢＯＤＹ ■■■■■■
#print qq|<br>**************<br>IsAdmin=[$IsAdmin] , LinkDetail=[$LinkDetail] , IsDebug = [$IsDebug], cokHanNo=[$cokHanNo]<br>**************<br>|;;
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if(($mode eq "nendolist") or ($mode eq "nendoSanka")) {
	#行事リストまたは差bbカリストならば当月のリストまで移動
	my $linkid = substr($startym,5,2);
	print qq| onLoad=setTimeout("location.href='#ID_$linkid'",100)|;
}
print qq|>\n|;
if($IsAdmin eq true) {
	print qq|<center><font color=purple size=-2>管理者モード</font></center>|;
}

$url1 = $ENV{'HTTP_HOST'};
$url2 = $ENV{'REQUEST_URI'};
if($url1 ne $ThisURI) {
	print qq|
		<h2><center>七二会分団サイトは移転しました。<br>
		<a href="https://kyum.chu.jp/syobo/sc.cgi">https://kyum.chu.jp/syobo/sc.cgi</a></center><h2>
	|;
}

#テスト用
#$mode = "ShowGyoji";
#$recno=61;

my @HeadMenu = ("href=\"$ThisScCgi?hanno=$HanNo&mode=nendolist&start=$rdDate\">行事リスト" ,
				"href=\"$ThisScCgi?hanno=$HanNo&mode=nendoSanka&start=$rdDate\">参加リスト" ,
				"href=\"kk.cgi\">会計");
my $MenuIx = 3;
if($IsAdmin eq true) {
	$HeadMenu[3] = "href=\"$ThisScCgi?hanno=$HanNo&mode=newSchedule&start=$rdDate\">行事を追加";
	$MenuIx++;
}
$HeadMenu[$MenuIx] = "href=\"kf/katsudoufuku.html\">その他";

#第2階層のメニュー
my @SecondMenu = (	"href=\"https://kyum.chu.jp/syobo/okurenger.html\">長野市消防団 安否確認サービス" ,
					"href=\"http://nagano-bousai.jp/mail_service.html\">長野市防災メール登録" ,
					"href=\"https://www.shinshu-oenshop.net\">信州消防団員応援ショップ" ,
					"href=\"https://kyum.chu.jp/syobo/yousi.html\">各種用紙" ,
					"href=\"kf/katsudoufuku.html\">活動服サイズ表" ,
					"href=\"doc/nenmatukeikai.html\">年末警戒報告要領");


if($mode eq "nendolist") {
	&PageTitle("$Hanmei年間スケジュール");
	&ShowNendolist( SHOW_MODE_GYOJI, $gNendo );
}
elsif($mode eq "nendoSanka") {
	&PageTitle("$Hanmei年間参加者");
	&ShowNendolist( SHOW_MODE_SANKA, $gNendo );
}
elsif($mode eq "memberlist") {
	&PageTitle("$Hanmei団員リスト");
	&outputmemberlist( $gNendo );
}
elsif(	($mode eq "ShowGyoji")		or	($mode eq "editgyoji")		or 
		($mode eq "SaveGyojiAdm")	or	($mode eq "SaveGyojiHan")	or 
		($mode eq "SankaEdit") 		or	($mode eq "SankaYoteiEdit") or 
		($mode eq "SaveSanka")		or	($mode eq "ShowSankaYotei")		or
		($mode eq "UploadPdfSel") 	or	($mode eq "UploadPdfWrite")) {

	#	データベース接続は最初に行っておく
	$db = DBI->connect($dbConnect, $userName, $password);
	$db->do("set names utf8");
	my $sth;
	my $dbOpen = 0;

	#	活動の明細は recno が指定されるので先に読んでおく
	$rdCount = 0;	#読込カウンタクリア
	if($recno > 0) {	#データ番号が指定されているならば、そのデータがあるかをチェック
		my $sqlStr = "select * from sybo_gyoji where No = $recno $TargetCheck;";
		#print qq| NO=$rdNo($recno) ,$mode . 年月日＝ $rdYear / $rdMonth / $rdDay じゃ <br> $sqlStr<br>|;	
		eval {
			$sth	 = $db->prepare($sqlStr) or die(DBI::errstr);
			$rdCount = $sth->execute() or die(DBI::errstr);
			$dbOpen = 1;
		};
		if($@){
			print qq| error(".$@.")<br>\n|;
		}
		if($rdCount eq "0E0") {
			$rdCount = 0;	#	見つからなかった場合は 0 件に書き替える
		}
		#print qq|SQL end . count=$rdCount<br>|;	
	}

	if($rdCount > 0) {
		my $hash_ref = $sth->fetchrow_hashref;
		my %row = %$hash_ref;

		#読み込んだデータを格納
		$rdNo		= $row{No};
		$rdDate		= $row{Date};
		$rdStartTime= $row{StartTime};
		$rdEndTime	= $row{EndTime};
		$rdBunrui	= $row{Bunrui};
		$rdGyojiMei	= $row{GyojiMei};
		$rdSanka	= $row{Sanka};
		$rdSyugo	= $row{Syugo};
		$rdTargets	= $row{TargetFlags};
		$rdAtama	= $row{F_Atama};
		$rdFukuso	= $row{F_Fuku};
		$rdKutsu	= $row{F_Kutsu};
		$rdMemo		= $row{Memo};
		$rdSiryo	= $row{Siryo};

		# 同じレコード番号ならば表示する
		$rdYear	= substr($rdDate,0,4);
		$rdMonth= substr($rdDate,5,2);
		$rdDay	= substr($rdDate,8,2);
		$rdNendo	= $rdYear;
		if($rdMonth < 4) {
			$rdNendo--;
		}
		#$rdStartHH	= substr($rdStartTime,0,2);
		$rdStartHH	= int($rdStartTime / 100);
		#$rdStartMM	= substr($rdStartTime,2,2);
		$rdStartMM	= $rdStartTime % 100;
		#$rdEndHH	= substr($rdEndTime,0,2);
		$rdEndHH	= int($rdEndTime / 100);
		#$rdEndMM	= substr($rdEndTime,2,2);
		$rdEndMM	= $rdEndTime % 100;
		$rdWeek = &get_week($rdYear,$rdMonth,$rdDay);
	}
	if($dbOpen eq 1) {
		$sth->finish;
	}
	&GetNenMaxMin();

	if($mode eq "ShowGyoji") {
		&PageTitle("活動詳細");
		&outeditgyoji();
	}
	elsif($mode eq "editgyoji") {
		&PageTitle("活動編集");
		&outeditgyoji();
	}
	elsif(	($mode eq "SaveGyojiAdm") or ($mode eq "SaveGyojiHan")) {
		&PageTitle("活動保存");
		&SaveGyoji();
	}
	elsif($mode eq "SankaEdit") {
		&PageTitle("参加団員編集");
		&SankaEdit(0);
	}
	elsif($mode eq "SankaYoteiEdit") {
		&PageTitle("参加予定団員編集");
		&SankaEdit(1);
	}
	elsif($mode eq "SaveSanka") {
		&PageTitle("参加団員保存");
		&SaveSanka();
	}
	elsif($mode eq "ShowSankaYotei") {
		&PageTitle("参加予定団員表示");
		&ShowSankaYotei();
	}
	elsif($mode eq "UploadPdfSel") {
		&PageTitle("資料の登録/入替");
		&UploadPdfSel();
	}
	elsif($mode eq "UploadPdfWrite") {
		&PageTitle("資料の書き込み");
		&UploadPdfWrite();
	}

	$db->disconnect;
}
elsif($mode eq "DeleteGyoji") {
	&DeleteGyoji();
}
elsif(	($mode eq "newSchedule") or ($mode eq "newHanGyoji")){
	
	#	データベース接続
	$db = DBI->connect($dbConnect, $userName, $password);
	&GetNenMaxMin();
	if($mode eq "newHanGyoji") {
		#班の行事を追加
		&PageTitle("班行事の追加");
		&InputGyoji(INPUT_MODE_NEW,ENTRY_MODE_HAN);
	}
	else {
		#管理者としての行事を追加
		&PageTitle("行事の追加");
		&newSchedule();
	}
	$db->disconnect;
}


else {
	# カレンダー表示指示（年,月,予定ファイル名）
	&PageTitle("今月の活動予定");
	print qq|<center>\t<div class="selectbox color">\n|;
	&ShowHanCombo();
	print qq|</div></center>\n|;

	&outputcalendarlink( $wantshowmonth, $startym );
	&calendarpackage::makecalendar($gCurYY, $gCurMM, $TargetCheck);
}
print qq|	<br><hr>|;

if($IsAdmin eq true) {
	print qq|
	<a class="btn--orange" href="$ThisScCgi?hanno=$HanNo&mode=newSchedule&start=$rdDate">行事を追加</a><br>\n|;
}
if(($mode eq "") or ($mode == "NewsUpdate")) {	#トップページなら QRコードを表示
		#石坂電話帳登録<br><a href="mailto:mishizaka-0721kr@ezweb.ne.jp?subject=XX班&body=本文のテキスト"><img src="img/ishizakaQR.png"></a>|;
		#	<a href="mailto:mishizaka-0721kr@ezweb.ne.jp?subject=XX班のオレだが&amp;body=以上">
	print qq|
		<a class="btn--orange" href="$ThisScCgi?mode=newHanGyoji">班行事の追加</a>
		<a class="btn--orange" href="$ThisScCgi?hanno=$HanNo&mode=memberlist&start=$gCurYY-$gCurMM-01">団員リスト</a><br>\n|;
		
	if($v) {	#	Newsテキストの編集
		#	ファイルの一括読み込み
		#	１行づつ読み込み
		open(my $fh, "<:utf8", $NewsFileName) or die;
		while(my $fline = $fh) {
			$content .= $fline;
		}	
		print qq|
			<form name="EditNewsForm" method="POST">
				<input type="hidden" name="mode" value="NewsUpdate">
				<TextArea name="EditNewsText" rows=30 cols=120>' . $content . '</TextArea>
				<input type="submit" class="form-submit" value="更新" />
			<form>
		|;
	}
	else {
		if($mode eq "NewsUpdate") {
print "<br>NEWS update start";
			open(my $fh, ">", $NewsFileName) or die;
			print $fh $EditNewsText;
			close($fh);
print "<br>NEWS update finish";
		}

		#	１行づつ読み込み
		#open(my $fh, "<:utf8", $NewsFileName) or die;
		open(my $fh, "<", $NewsFileName) or die;
		my $hdlevel = 0;
		
		print qq|
          <div class="main-cont info">\n
            <section class="main-section">\n
              <div class="info-head">\n
                <h2 class="info-ttl">お知らせ</h2>\n
                <!--p class="info-lead">新着情報リスト</p-->\n
              </div>\n
              <div class="info-cont">\n
                <ul class="info-area">\n
		|;
		while(my $fline =  <$fh>) {

			if(trim($fline) eq ""){
				if($hdlevel > 1) {
					print qq|</ul>\n</li>
						|;
				}
				$hdlevel = 0;	#	空白なら次は日付となる
			}
			elsif($hdlevel eq 0) 
			{	#	hdlevel : 0	 日付
				$fline =~ s/\r\n$ | \n$ | \r$//;	#	末尾の 改行文字を取り去る
				print qq|<li>
							<p class="info-data"> $fline </p>\n|;
				$hdlevel = 1;	#	内容へ			
			}
			elsif($hdlevel eq 1) 
			{	#	hdlevel : 0	 見出し
				$fline =~ s/\r\n$ | \n$ | \r$//;	#	末尾の 改行文字を取り去る
				print qq|<p class="info-txt"> $fline </p>
							<ul class="info-list">
						|;
				$hdlevel = 2;	#	内容へ			
			}
			else 
			{	#	hdlevel : 2 以上	 内容
				$fline =~ s/\r\n/<br>/;	#str_replace("\r\n", "<br>", $fline);
				$fline =~ s/\r/<br>/; #str_replace("\r", "<br>", $fline);
				$fline =~ s/\n/<br>/; #str_replace("\n", "<br>", $fline);
				
				if(hdlevel == 2) {
					print	qq|
						<ul class="info-list">
					|;
				}
				print qq|<li>$fline</li>\n|;
				$hdlevel++;
			}
		}
		print qq|
							</ul>
						</div>
					</section>
				</div>
				|;
		if($IsAdmin eq true) {
			print '<a href=\"./company.php?mode=NewsEdit\" class=\"form-submit\" >編集</a>';
		}
	}
}
print qq|<br>\n|;
print qq|
	<a class="btn--orange" href="$ThisScCgi?hanno=$HanNo&mode=nendolist&start=$rdDate">行事リスト</a>
	<a class="btn--orange" href="$ThisScCgi?hanno=$HanNo&mode=nendoSanka&start=$rdDate">参加リスト</a>
	<a class="btn--orange" href="./qrcode.html">ＱＲコード</a>
	<a class="btn--orange" href="./okurenger.html">長野市消防団 安否確認サービス</a>
	<a class="pagetop" href="#"><div class="pagetop__arrow"></div></a>|;

#	<a class="btn--orange" href="kk.cgi">会計</a>\n|;

sub PageTitle() {
	print qq|\t<h2><a href="$ThisScCgi"><img src="./img/home_mark.png" class="home-icon"></a>$_[0]</h2>\n|;
	
    print qq|<div class="drawer">        
      <input type="checkbox" name="navToggle" id="navToggle" class="nav-toggle">
      <label for="navToggle" class="btn-burger">
        <span class="top-icon"></span>            
      </label>        
       
      <nav class="nav">                    
       <ul class="nav-list">            
        <li>ホーム $#HeadMenu</li>|;
		my $ix = 0;
		foreach my $hdMenu (@HeadMenu) {
			print qq|<li><a $hdMenu </a>|;
			if($ix < $#HeadMenu) {
				print qq|</li>\n|;
			}
			else {
				print qq|<ul class="second-level">|;
				foreach my $secMenu (@SecondMenu) {
					print qq|<li><a $secMenu </a></li>\n|;
				}
				print qq|</ul></li>\n|;
			}
			$ix++;
		}

		print qq|</ul>
      </nav>
    </div>|; 
}

sub get_week{
  my($y,$m,$d);
  if(@_ == 3){
    ($y,$m,$d) = @_;
  }elsif(@_ == 1){
    ($y,$m,$d) = split /-/, $_[0];
  }
  my @wdays = qw(日 月 火 水 木 金 土);
  if ($m < 3) {$y--; $m+=12;}
  my $w=($y+int($y/4)-int($y/100)+int($y/400)+int((13*$m+8)/5)+$d)%7;
  return $wdays[$w];
}
sub GetNenMaxMin {
	my $sth = $db->prepare("select max(Nendo), min(Nendo) from sybo_taisei;");
	my $rv = $sth->execute;
	@ary = $sth->fetchrow_array;
	$NendoMax = $ary[0] + 1;
	$NendoMin = $ary[1];
	$sth->finish;
}

# ---------------------- #
# 参加者のチェックを更新 #
# ---------------------- #
sub SankaEdit()
{
	my $IsYotei;
	$IsYotei = $_[0];

	my $sqlStr;

	#行事情報を読込
	$sqlStr = << "EOS";
	SELECT Date,GyojiMei,StartTime,EndTime,TargetFlags
	FROM sybo_gyoji
	where No = $recno;
EOS

	dbg_print( "DEBUG SankaEdit sqlStr = [$sqlStr] <br><hr>");
	$sth = $db->prepare($sqlStr);
	my $rv = $sth->execute;

	my $ary_ref = $sth->fetchrow_arrayref;
	my $rdDate = $ary_ref->[0];
	my $rdName = $ary_ref->[1];

	$rdYear	 = substr($rdDate,0,4);
	$rdMonth = substr($rdDate,5,2);
	if($rdMonth < 4) {
		$rdYear--;
	}
	$rdDay	 = substr($rdDate,8,2);
	#参加対象班で表示するリストを絞り込み
	my $drTargetFlags = $ary_ref->[4];
	if($HanNo > 0) {
		$ChkBit = (1 << $HanNo);
		if(($ChkBit and $drTargetFlags) ne 0) {
			$drTargetFlags = $ChkBit;
		}
	}
	
	#日付と行事名を読込
	print qq|
	<style>
	.HanName {
			background: none;
			border: none;
			color: #008030;
			font-size: 1.5rem;
			width: 100%;
			padding-left: 1rem;	
	}
	.HanGroup {
		background: #fff;
		border: 1px;
		color: #000;
		font-size: 1rem;
		width: 90%;
		padding-left: 1rem;	
		padding-top: 4px;
		padding-bottom: 4px;
	}
\@media (max-width: 768px) {
	.HanName {
		font-size: 1.0rem;
	}
}
	.DaninLine0 {
		background: #CCC;
		width: 96%;
	}
	.DaninLine1 {
		background: #AAA;
		width: 96%;
	}
	.DaninName {
		display: inline-block;
		width: 6rem;
		padding-left: 1rem;	
	}
	</style>
	
	<br> $rdYear 年 $rdMonth 月 $rdDay 日　<br> $rdName 
	|;

	# HTML表示(TABLE BODIES)
	print qq|<form><br>|;
	print qq|<input type="hidden" name="hanno" value="$HanNo">|;
	print qq|<input type="hidden" name="Nendo" value="$rdYear">|;
	print qq|<input type="hidden" name="recno" value="$recno">|;
	print qq|<input type="hidden" name="IsYotei" value="$IsYotei">|;
	print qq|<input type="hidden" name="mode" value="SaveSanka">|;

	my $HanIx;
	my $HanBit=1;
	for($HanIx=0;$HanIx<$HAN_CNT;$HanIx++) {
		if(($drTargetFlags & $HanBit) ne 0) {

			#########参加対象班ならば#########
			print qq|
			<div class="HanName"> @HanList[$HanIx]</div>
			<div class="HanGroup">|;
			
			#①参加フラグを読込
			$sth = $db->prepare("select SankaStr from sybo_sanka where GyojiNo=$recno and KuNo=$HanIx and IsYotei=$IsYotei;");
			my $rv = $sth->execute;

			my $ary_ref = $sth->fetchrow_arrayref;
			my $rdMarks = $ary_ref->[0];


			#②団員名を読み込む
			$sqlStr = << "EOS";
			select t.Nendo,t.Kaikyu,d.Name
				from sybo_taisei t
				join (select * from sybo_danin d where KuNo=$HanIx) d ON t.DaninNo = d.No
				where t.Nendo=$rdYear and t.KuNo=$HanIx
				order by t.TaiseiNo;
EOS


			$sth = $db->prepare($sqlStr);
			$rv = $sth->execute;

			#print qq|member sqlStr = [$sqlStr] <br><hr>|;
			
			# HTML入力欄の追加
			#print qq|参加者の編集\n rdYear=$rdYear <br><hr><form>|;
			if($rdMarks eq "") {	
				#参加リストが空だった場合、参加実績ならば人数分の0(不参加)、参加予定ならば0(未定)を作る
				for(my $ix=0;$ix<$rv;$ix++) {
					$rdMarks .= "0#";
				}

				#余計に追加した # を除去
				$rdMarks = substr($rdMarks, 0, length($rdMarks) - 1);
			}
			my @rdFlsgs = split(/#/,$rdMarks);

			$ix = 1;
			my $str_ix; 
			my @YoteiStr =  ("未定", "参加", "欠席");
			while ($hash_ref = $sth->fetchrow_hashref) {
				my %t_row = %$hash_ref;
				$str_ix = sprintf("sk%02d%02d", $HanIx,$ix);
				if($IsYotei == 0) {
					#実績
					# チェックボックスの場合は、チェックされているものだけが submit先に通知される
					print qq|
					|;
					if(@rdFlsgs[$ix-1] eq 1) {
						print qq|<input type="checkbox" name="$str_ix" value="$ix" checked="checked">$t_row{kaikyu} $t_row{Name}<br>|;
					}
					else {
						print qq|<input type="checkbox" name="$str_ix" value="$ix" >$t_row{kaikyu} $t_row{Name}<br>|;
					}
				}
				else {
					#予定の場合は　0:未定,1:参加,2:不参加 の３択
					$ixLine = $ix % 2;
					print qq|
						<div class="DaninLine$ixLine">
							<span class="DaninName">$t_row{kaikyu} $t_row{Name}</span>|;
					for(my $SelIx=0;$SelIx<3;$SelIx++) {

						print qq|
						<Label>|;
						if(@rdFlsgs[$ix-1] eq $SelIx) {
							print qq|<input type="radio" name="$str_ix" value="$SelIx" checked="checked"">|;
						}
						else {
							print qq|<input type="radio" name="$str_ix" value="$SelIx" >|;
						}
						print qq|@YoteiStr[$SelIx]</Label>|;
					}
					print qq|
					</div>|;
				}
				$ix++;
			}
			$sth->finish;	#表示終了 HanGroup
			print qq|
			</div>|;
		}
		$HanBit *= 2;
	}	
		
	print qq|<input type="submit" value="保存"></form>|;
}

# ---------------------- #
# 参加フラグの保存       #
# ---------------------- #
sub SaveSanka()
{
	my $querybuffer = $ENV{'QUERY_STRING'};
	
	dbg_print("DEBUG - SaveSanka　Param[$querybuffer]<br>");
	
	my ($pmDate, $pmNo, $pmKind, $pmTitle, $pmTime,$pmSanka,$pmSyugo,$pmFukuso,$pmShose,$pmAtama,$pmComment);
	my ($pmYear,$pmMonth,$pmDay);
	my ($pmStartHH,$pmStartMM,$pmEndHH,$pmEndMM);

	# 分解
	my @pairs = split(/&/,$querybuffer);
	my $patern,@paterns;
	$rdNo = $recno;
	my $pmNendo,$IsYotei=0;
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);
		$value =~ s/\+/ /g;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg;
		$value =~ s/\t//g;

		#&jcode::convert(*value, 'sjis');	要らないらしい
		if( $name eq "Nendo" ) 		{	$pmNendo = $value;	}
		if( $name eq "recno" ) 		{	$pmcno = $value;	}
		if( $name eq "IsYotei" ) 	{	$IsYotei = $value;	}
		#skで始まる文字が参加順
		if( substr($name,0,2) eq "sk")	{
			# patern定義は後から出てくるため、読み取った値はテーブルに格納しておく
			my $HanIx = substr($name,2,2);	#対象班のIndexを @paternsに格納する
			push(@{$paterns[$HanIx]},$value);
		}
	}
	#foreach ( @paterns ){ print "( @$_ )\n"; } #paterns への pushは成功している


	my @patern;
	my $StartIx=0;
	my $LastIx=$HAN_CNT;
	if($HanNo > 0) {
		#本部以外は対象の班だけを更新する
		$StartIx=$HanNo;
		$LastIx=$HanNo+1;
	}
	for(my $ix=$StartIx;$ix<$LastIx;$ix++) {

		#団員数を求めて、参加パターン文字列(0#0#0#・・・)を編集
		my $sqlStr = "select count(DaninNo) from sybo_taisei where Nendo=$pmNendo and KuNo=$ix;";
		$sth = $db->prepare($sqlStr);
		my $rv = $sth->execute;
		
		#print qq|$sqlStr -> |;

		my $ary_ref = $sth->fetchrow_arrayref;
		my $rdCount = $ary_ref->[0];
		$sth->finish;	#読込終了


		$patern[$ix] = "";	#パターン文字列の編集
		#１　空のパターン文字列の編集
		for($pt_ix=0;$pt_ix<$rdCount;$pt_ix++) {
			$patern[$ix] = $patern[$ix] . "0#";
		}
		#print qq|DEBUG 1. cnt=$rdCount ___ $patern[$ix] -> |;
		

		#１　パラメータ値をパターンに埋め込み
		my @ChkNo = @paterns[$ix];
		
		my $pos_no;
		my $ChkCnt = @{@paterns[$ix]};

		if($IsYotei == 0) {
			#参加実績はチェックの入っているものだけが通知される
			for (my $pos_ix = 0; $pos_ix < $ChkCnt; $pos_ix++){
				
				$pos_no = (@paterns[$ix]->[$pos_ix] - 1 ) * 2; 
				$patern[$ix] = substr($patern[$ix],0, $pos_no) . "1" . substr($patern[$ix],$pos_no+1);
			}
		}
		else {
			#参加予定はRadioButtonの値が通知される
			for (my $pos_ix = 0; $pos_ix < $ChkCnt; $pos_ix++){
				
				$pos_no = $pos_ix * 2;
				$val = @paterns[$ix]->[$pos_ix]; 
				$patern[$ix] = substr($patern[$ix],0, $pos_no) . $val . substr($patern[$ix],$pos_no+1);
			}
		}


		#参加データが存在するかをチェック
		$sqlStr = "select SankaStr from sybo_sanka where GyojiNo=$recno and KuNo=$ix and IsYotei=$IsYotei;";
		$sth = $db->prepare($sqlStr);
		my $rv = $sth->execute;
		$sth->finish;	#読込終了
		if($rv > 0) {
			#	データがある場合はUPDATEとする
			$sqlStr = "UPDATE sybo_sanka SET SankaStr='$patern[$ix]' where GyojiNo=$recno and KuNo=$ix  and IsYotei=$IsYotei;";
		}
		else {
			#	無い場合はINSERTとする
			$sqlStr = "INSERT INTO sybo_sanka SET SankaStr='$patern[$ix]',GyojiNo=$recno,KuNo=$ix, IsYotei=$IsYotei,Memo='$pmComment';";
		}
		
		#print qq|DEBUG SaveSanka sqlStr[$sqlStr]<br>|;
		
		$sth = $db->prepare($sqlStr);
		$rv = $sth->execute;
		$sth->finish;	#表示終了
	}

	print qq|参加者更新完了|;
	print qq|<div class="selectbox color">|;
	&ShowHanCombo();
	print qq|</div>|;
}


# ---------------------- #
# 参加予定リストの表示       #
# ---------------------- #
sub ShowSankaYotei()
{
	my $IsYotei=1;
	
	my $sqlStr;

	#行事情報を読込
	$sqlStr = << "EOS";
	SELECT Date,GyojiMei,StartTime,EndTime,TargetFlags
	FROM sybo_gyoji
	where No = $recno;
EOS

	dbg_print( "DEBUG SankaEdit sqlStr = [$sqlStr] <br><hr>");
	$sth = $db->prepare($sqlStr);
	my $rv = $sth->execute;

	my $ary_ref = $sth->fetchrow_arrayref;
	my $rdDate = $ary_ref->[0];
	my $rdName = $ary_ref->[1];

	$rdYear	 = substr($rdDate,0,4);
	$rdMonth = substr($rdDate,5,2);
	if($rdMonth < 4) {
		$rdYear--;
	}
	$rdDay	 = substr($rdDate,8,2);
	#参加対象班で表示するリストを絞り込み
	my $drTargetFlags = $ary_ref->[4];
	if($HanNo > 0) {
		$ChkBit = (1 << $HanNo);
		if(($ChkBit and $drTargetFlags) ne 0) {
			$drTargetFlags = $ChkBit;
		}
	}
	
	#日付と行事名を読込
	print qq|
	<style>
	.HanName {
		background: none;
		border: none;
		color: #008030;
		font-size: 1.5rem;
		width: 100%;
		padding-left: 1rem;	
	}
	.HanGroup {
		background: #fff;
		border: 1px;
		color: #000;
		font-size: 1rem;
		width: 90%;
		padding-left: 1rem;	
		padding-top: 4px;
		padding-bottom: 4px;
	}
	.HanMemo {
		margin-left:2rem;
		line-height: 12px;
		font-size: 1.0rem;
		color: #44F;
	}
\@media (max-width: 768px) {
	.HanName {
		font-size: 1.0rem;
	}
}
	.DaninLine0 {
		background: #CCC;
		width: 96%;
	}
	.DaninLine1 {
		background: #AAA;
		width: 96%;
	}
	.SankaMitei {	/* 参加有無の表示 */
		Color: #408080;
		font-weight: bold;
		margin-left: 1rem;
	}
	.SankaOK {	/* 参加有無の表示 */
		Color: #4040A0;
		font-weight: bold;
		margin-left: 1rem;
	}
	.SankaNG {	/* 参加有無の表示 */
		Color: #A04040;
		font-weight: bold;
		margin-left: 1rem;
	}
	.DaninName {
		display: inline-block;
		width: 6rem;
		padding-left: 1rem;	
	}
	</style>
	
	<br> $rdYear 年 $rdMonth 月 $rdDay 日　<br> $rdName 
	|;
	# HTML表示(TABLE BODIES)
	print qq|<form><br>|;
	print qq|<input type="hidden" name="hanno" value="$HanNo">|;
	print qq|<input type="hidden" name="Nendo" value="$rdYear">|;
	print qq|<input type="hidden" name="recno" value="$recno">|;
	print qq|<input type="hidden" name="IsYotei" value="$IsYotei">|;
	print qq|<input type="hidden" name="mode" value="SaveSanka">|;

	my $HanIx;
	my $HanBit=1;
	my @TotalCnt = (0,0,0);
	for($HanIx=0;$HanIx<$HAN_CNT;$HanIx++) {
		if(($drTargetFlags & $HanBit) ne 0) {

			#########参加対象班ならば#########
			$OutStrHead = " \
			<details class=\"HanGroup\"> <summary class=\"HanName\">@HanList[$HanIx] ";
			$OutStrDetail = "</summary> \
			"; 
			
			#①参加フラグを読込
			$sqlStr = "select SankaStr,Memo from sybo_sanka where GyojiNo=$recno and KuNo=$HanIx and IsYotei=$IsYotei;";
			$sth = $db->prepare($sqlStr);
			my $rv = $sth->execute;

#$OutStrDetail .= "[ $sqlStr ]<br>";

			my $ary_ref = $sth->fetchrow_arrayref;
			my $rdMarks = $ary_ref->[0];
			my $rdMemo = $ary_ref->[1];


			#②団員名を読み込む
			$sqlStr = << "EOS";
			select t.Nendo,t.Kaikyu,d.Name
				from sybo_taisei t
				join (select * from sybo_danin d where KuNo=$HanIx) d ON t.DaninNo = d.No
				where t.Nendo=$rdYear and t.KuNo=$HanIx
				order by t.TaiseiNo;
EOS


			$sth = $db->prepare($sqlStr);
			$rv = $sth->execute;

			#print qq|member sqlStr = [$sqlStr] <br><hr>|;
			
			# HTML入力欄の追加
			#print qq|参加者の編集\n rdYear=$rdYear <br><hr><form>|;
			if($rdMarks eq "") {	
				#参加リストが空だった場合、参加実績ならば人数分の0(不参加)、参加予定ならば0(未定)を作る
				for(my $ix=0;$ix<$rv;$ix++) {
					$rdMarks .= "0#";
				}
			}
			my @rdFlsgs = split(/#/,$rdMarks);

#$OutStrDetail .= "[ $rdMarks ]<br>";

			$ix = 1;
			my @SankaCnt = (0,0,0);
			my $str_ix; 
			my @YoteiTbl =  ("未定", "参加", "欠席");
			my @YoteiClr =  ("SankaMitei", "SankaOK", "SankaNG");
			while ($hash_ref = $sth->fetchrow_hashref) {
				my %t_row = %$hash_ref;
				$str_ix = sprintf("sk%02d%02d", $HanIx,$ix);
				if($IsYotei == 0) {
					#実績
					if(@rdFlsgs[$ix-1] eq 1) {
						$OutStrDetail .= "参加";
						$SankaCnt[1]++;
					}
					else {
						$OutStrDetail .= "欠席";
						$SankaCnt[2]++;
					}
					$OutStrDetail .= "　$t_row{kaikyu} $t_row{Name}<br>";
				}
				else {
					#予定の場合は　0:未定,1:参加,2:不参加 の３択
					$ixLine = $ix % 2;
					$YoteiIx  = $rdFlsgs[$ix-1];
					$YoteiStr = $YoteiTbl[$YoteiIx];
					$YoteiColor = $YoteiClr[$YoteiIx];
					$SankaCnt[$YoteiIx]++;
					$TotalCnt[$YoteiIx]++;
					$OutStrDetail .= "	\
						<li class=\"DaninLine$ixLine\">	\	
							<span class=\"DaninName\">$t_row{kaikyu} $t_row{Name}</span> \
							<span class=\"$YoteiColor\"> $YoteiStr</span> \
						</li>";
				}
				$ix++;
			}
			$sth->finish;	#表示終了 HanGroup
			$OutStrHead .= "　　参加:$SankaCnt[1]　欠席:$SankaCnt[2]　未定:$SankaCnt[0]";
			if($rdMemo ne "") {
				#	メモ書きがある場合
				$rdMemo =~ s/\n/<br>/g;
				$OutStrHead .= "<br><span class=\"HanMemo\">$rdMemo</span>";
			}
			print "$OutStrHead $OutStrDetail \
			</details>	";
		}
		$HanBit *= 2;
	}	
	print "<div class=\"HanGroup\"><hr><span class=\"HanName\">合計　　　参加:$TotalCnt[1]　欠席:$TotalCnt[2]　未定:$TotalCnt[0]</span></div>";
}

# ---------------- #
# 行事の保存       #
# ---------------- #
sub SaveGyoji()
{
	my $querybuffer = $ENV{'QUERY_STRING'};
	
	dbg_print("DEBUG SaveGyoji Query[$querybuffer]<br>");
	
	my ($pmDate, $pmNo, $pmKind, $pmTitle, $pmTime,$pmSanka);
	my ($pmSyugo,$pmFukuso,$pmShose,$pmAtama,$pmComment);
	my ($pmYear,$pmMonth,$pmDay,$pmHanNoReq);
	my ($pmStartHH,$pmStartMM,$pmEndHH,$pmEndMM);
	my $pmTarget = 0;

	# 分解
	my @pairs = split(/&/,$querybuffer);
	if($recno > 0) {
		$rdNo = $recno;		#データ更新。KeyとなるNoを設定。
	}
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);
		$value =~ s/\+/ /g;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg;
		$value =~ s/\t//g;

		#&jcode::convert(*value, 'sjis');	要らないらしい
		if( $name eq "rdYear" )		{	$pmYear		= $value;	}
		if( $name eq "rdMonth" )	{	$pmMonth	= $value;	}
		if( $name eq "rdDay" )		{	$pmDay		= $value;	}
		if( $name eq "recno" ) 		{	$pmcno		= $value;	}
		if( $name eq "rdKind" )		{	$pmKind		= $value;	}
		if( $name eq "rdTitle" )	{	$pmTitle	= $value;	}
		if( $name eq "rdStartHH" )	{	$pmStartHH	= $value;	}
		if( $name eq "rdStartMM" )	{	$pmStartMM	= $value;	}
		if( $name eq "rdEndHH" )	{	$pmEndHH	= $value;	}
		if( $name eq "rdEndMM" )	{	$pmEndMM	= $value;	}
		if( $name eq "rdSanka" )	{	$pmSanka	= $value;	}
		if( $name eq "rdSyugo" )	{	$pmSyugo	= $value;	}
		if( $name eq "rdFukuso" )	{	$pmFukuso	= $value;	}
		if( $name eq "rdShose" )	{	$pmShose	= $value;	}
		if( $name eq "rdAtama" )	{	$pmAtama	= $value;	}
		if( $name eq "rdComment" )	{	$pmComment	= $value;	}

		if($mode eq "SaveGyojiHan") {
			#班の行事追加　
			if( $name eq "rdHanNoReq" )	{
				$pmTarget = 1 << $value;
			}
		}
		else {
			#SaveGyojiAdmならば tgで始まる文字が参加対象班
			if( substr($name,0,2) eq "tg")	{
				my $value = substr($name,2); # tg**の値を取得patern定義は後から出てくるため、読み取った値はテーブルに格納しておくpatern定義は後から出てくるため、読み取った値はテーブルに格納しておく
				$pmTarget += 1 << $value;
			}
		}
	}
	dbg_print("DEBUG Input check $pmYear/$pmMonth/$pmDay <br>");

	if(( $pmYear eq "" ) or ($pmMonth eq "")) {
		&errorexit("年月の指定がありません。");
	}
	if( $pmDay eq "" ) {
		$pmDay = "00";
	}
	if( $pmTitle eq "" ) {
		&errorexit("活動が未入力です。");
	}
	dbg_print("DEBUG Record[$SvRecord]<br>");

	# localtime は　($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)に分解される
	my ($curSec,$curMin,$curHour,$curMday,$curMon,$curYear,$curWday,$curYday,$curIsdst) = localtime(time);
	my	$EnterDate = sprintf("'%04d-%02d-%02d'",$curYear + 1900, $curMon + 1, $curMday );
	my	$pmDate = "$pmYear-$pmMonth-$pmDay";
	my	$startTm = $pmStartHH * 100 + $pmStartMM;
	my	$endTm = $pmEndHH * 100 + $pmEndDD;
	my	$sqlStr = "";

	if(($HanNo eq 0) or ($recno eq 0)) {
		#本部でのスケジュール追加/変更　または 追加の場合
		if($pmTarget eq 0) {
			#　変更で値が０となってしまった場合の書き換え	
			$pmTarget = 0xffff;
		}
		$TagetFlagUpdate = ", TargetFlags = $pmTarget ";
	}
	if($recno > 0) {
		#更新の場合
		$sqlStr = << "EOS";
		UPDATE sybo_gyoji SET
			EnterDate= $EnterDate, Date ='$pmDate',StartTime =$startTm,EndTime =$endTm,
			Bunrui ='$pmKind', GyojiMei ='$pmTitle', Sanka ='$pmSanka', Syugo ='$pmSyugo', 
			F_Atama = $pmAtama, F_Fuku =$pmFukuso, F_Kutsu =$pmShose,Memo = '$pmComment'
			$TagetFlagUpdate
			where No = $rdNo;
EOS
	}
	else {
		$sqlStr = "select No from sybo_gyoji where Date ='$pmDate' and GyojiMei = '$pmTitle';";
		$sth = $db->prepare($sqlStr);
		my $rv = $sth->execute;
		$sth->finish;
		dbg_print("DEBUG SaveGyoji Dup check -- sqlStr=「$sqlStr」<br>");
		if($rv > 0) {
			$sqlStr = "";	#戻るボタンで同じデータが登録された場合の対策
			#print qq|DEBUG SaveGyoji Dupulicated<br>\n|;
		}
		else {
			#print qq|DEBUG SaveGyoji　MaxNo Get<br>|;

			#データ追加。現在登録されている最大のNoを取得。
			$sth = $db->prepare("select max(No) from sybo_gyoji;");
			$rv = $sth->execute;
			@ary = $sth->fetchrow_array;
			$rdNo = $ary[0] + 1;
			$sth->finish;

			#print qq|DEBUG SaveGyoji　MaxNo = $rdNo<br>|;
			
			$sqlStr = << "EOS";
			INSERT into sybo_gyoji SET
				No = $rdNo, EnterDate = $EnterDate,
				Date ='$pmDate',StartTime =$startTm,EndTime =$endTm,
				Bunrui ='$pmKind', GyojiMei ='$pmTitle', Sanka ='$pmSanka', Syugo ='$pmSyugo', 
				F_Atama = $pmAtama, F_Fuku =$pmFukuso, F_Kutsu =$pmShose, 
				Memo = '$pmComment' $TagetFlagUpdate;
EOS
		}
	}

	dbg_print("DEBUG SaveGyoji -- sqlStr=「$sqlStr」<br>");

	if($sqlStr eq "") {
		print qq|$pmYear/$pmMonth/$pmDay 「$pmTitle」は既に登録されています<br>|;
	}
	else {
		my $sth = $db->prepare($sqlStr);
		my $rv = $sth->execute;
		$sth->finish;
		print qq|$pmYear/$pmMonth/$pmDay 「$pmTitle」追加完了<br>|;
	}
	print qq|<a href="$ThisScCgi?hanno=$HanNo&mode=SankaEdit&recno=$rdNo">参加団員編集</a><br>|;
}

# -------------------- #
# POSTパラメータの分解 #
# -------------------- #
sub splitPost
{
	$query = new CGI;
	$mode	= $query->param('mode');	# 表示モード
	$recno	= $query->param('recno');	# レコード番号
	$HanNo	= $query->param('recno');	# 班番号
	$SrcFile= $query->param('pdf');
	$EditNewsText	= $query->param('EditNewsText');
}
# ---------------- #
# GETパラメータの分解 #
# ---------------- #
sub splitGet
{
	# 結合
	my $querybuffer = $ENV{'QUERY_STRING'};

	# 分解
	my @pairs = split(/&/,$querybuffer);
	foreach $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);
		# 分解
		if( $name eq "hanno" ) {
			$HanNo = $value;	# 班＝区番号
			if($HanNo eq 99) {	# 全行事指定
				$HanBit = TARGET_ALL_DATA;
				$TargetCheck = "";	#班の絞り込み無し
				$Hanmei = $HanAll;
				#print qq|DEBUG All HanNo = $value , $HanBit , $TargetCheck , $Hanmei<br>|;
			}
			elsif($HanNo > 10) {	#範囲外ならば本部とする
				$HanNo = 0;		
			}
			else {	#指定の本部または班の指定
				$HanBit = 1 << $HanNo;
				$TargetCheck = "and (TargetFlags & $HanBit) > 0";
				$Hanmei = $HanList[$HanNo];
				#print qq|DEBUG Select HanNo = $value , $HanBit , $TargetCheck , $Hanmei<br>|;
			}
			$HanSitei = true;
		}
		if( $name eq "start" ) {
			$startym = $value;	# 表示開始年月
		}
		if( $name eq "mode" ) {
			$mode = $value;		# 表示モード
		}
		if( $name eq "recno" ) {
			$recno = $value;	# レコード番号
		}
		if( $name eq "chkAllData" ) {
			$HanBit = TARGET_ALL_DATA;
			$TargetCheck = "";	#班の絞り込み無し
			$Hanmei = $HanAll;
		}
		if( $name eq "hanchange" ) {	
			$bHanChange = true;	# 班の切り替え指定があったら
		}
	}
	if(($HanSitei eq false) and ($cokHanNo >= 0)) {
		#班の指定が無く、クッキー指定がある場合
		$HanNo	= $cokHanNo;
		$HanBit = 1 << $HanNo;
		$TargetCheck = "and (TargetFlags & $HanBit) > 0";
		$Hanmei = $HanList[$HanNo];
	}
	
	# 内容チェック
	if( $startym eq "" ) {
		# 年が指定されなかった場合は、本日日付から表示年度を取得
		# localtime は　($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)に分解される
		($gCurMM,$gCurYY) = (localtime(time))[4,5];	
		$gCurYY = sprintf("%04d",$gCurYY + 1900);
		$gCurMM = sprintf("%02d",$gCurMM + 1);
		$gNendo	= $gCurYY;
		if($gCurMM < "04") {
			$gNendo--;
		}
		$startym = sprintf("%04d-%02d",$gCurYY,$gCurMM);

		#print "省略日時 [$startym] [$gCurYY] [$gCurMM]<br>";
	}
	else {
		#if( $startym !~ m/^\d\d\d\d-1?\d$/ ) {
		if( $startym !~ m/^\d\d\d\d-\d\d-\d\d$/ ) {
			# 書式が違っていればエラー
			$startym = "";
			&errorexit("パラメータの書式にミスがあります。<br>「start=2015-03」のように、西暦4桁 + 月2桁)で指定して下さい。");
		}
		else{
			$gCurYY = $gNendo = substr($startym,0,4);
			$gCurMM = substr($startym,5,2);
			$gCurDD = substr($startym,8,2);
			if(( $gCurMM lt "01" ) or ($gCurMM gt "12")) {
				&errorexit("パラメータの書式にミスがあります。月[$gCurYY]  は01～12の数値で指定して下さい。");
			}
			#if($gCurMM < "04") {	#行事リストの年度選択が前年になってしまったため、一旦コメントアウト
			#	$gNendo--;
			#}
		}
	}
	if($bHanChange eq true) {
		#班の切り替え指定があったら クッキー書き込み
		print "Set-Cookie: hanno=$HanNo; expires=Tue, 20-Dec-2025 00:00:00 GMT;";
	}
}

# ------------------------------ #	Ver 2.10 追加機能
# 次のカレンダーへのリンクを出力 #   [引数] 表示させる月数, 表示開始年月(省略可)
# ------------------------------ #
sub outputcalendarlink
{
	my $showmonths = shift @_;
	my $startym = shift @_;						# 表示開始年月：書式は「2007-1」・「2007-12」
	my $startyear	= substr($startym,0,4);
	my $startmonth	= substr($startym,5,2);		# 表示開始年月を分割

	#print qq|startym=[$startym] , startyear=[$startyear] ,startmonth=[$startmonth]\n|; 

	#前の月へのリンク
	my $befrstartyear = $startyear;
	my $befrstartmonth	= $startmonth - $showmonths;
	if( $befrstartmonth < 1 ) {	# 年の繰り下げ処理
		$befrstartyear += int( $befrstartmonth / 12 );
		$befrstartmonth += 12;
	}
	$befrstartmonth = sprintf("%02d",$befrstartmonth);

	#次の月へのリンク
	my $nextstartyear = $startyear;
	my $nextstartmonth	= $startmonth +  $showmonths;
	if( $nextstartmonth > 12 ) {	# 年の繰り上げ処理
		$nextstartyear += int( $nextstartmonth / 12 );
		$nextstartmonth -= 12;
	}
	$nextstartmonth = sprintf("%02d",$nextstartmonth);
	
	print "<center>";
	print qq|
		<a class="btn--allow" href="$ThisScCgi?hanno=$HanNo&start=$befrstartyear-$befrstartmonth-01">
			<i class="fas fa-arrow-circle-left fa-position-left"></i>
			$befrstartyear年$befrstartmonth月 
			</a>\n|;
	print "<calender-date>$startyear年$startmonth月</calender-date>\n";
	print qq|
		<a class="btn--allow" href="$ThisScCgi?hanno=$HanNo&start=$nextstartyear-$nextstartmonth-01">
			$nextstartyear年$nextstartmonth月
			<i class="fas fa-arrow-circle-right fa-position-right"></i>
			</a>\n|;
	print "</center>\n";
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

#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 区の選択ドロップダウンを表示する
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
sub ShowHanCombo 
{
	print qq|\t　<select id="cmbHanNo" name="rdHanNo" onchange="location.href=value;">\n|;
	my $ix = 0;
	my $SelHan;
	
	if($HanSitei eq true) {
		$SelHan = $HanNo;
		if(($SelHan < 0) or ($SelHan > 10)) {
			$SelHan = 99;	# 未指定ならば全リスト
		}
	}
	else {
		$SelHan = $cokHanNo;
	}
	#	現在のモードにより移行先を切り替え	
	my $NextMode = "";
	if(($mode eq "SankaEdit") or ($mode eq "SaveSanka")) {
		#対象班を切り替えて参加者登録を行う場合のパラメータを追加
		$NextMode = "mode=SankaEdit&recno=$recno";
	}elsif($mode eq "ShowGyoji") {
		$NextMode = "mode=ShowGyoji&recno=$recno";
	}elsif(($mode eq "nendolist") or ($mode eq "memberlist")) {
		$NextMode = "mode=$mode";
	}
	
	my	$sel_ix = 0;
	foreach my $HanName (@HanList){
		my $linkUrl = "$ThisScCgi?hanno=$ix&start=" . $gCurYY . "-" . $gCurMM . "-01&$NextMode&hanchange=1";
		print qq|\t\t<option value="$linkUrl">$HanName</option>\n|;
		if($ix eq $SelHan) {
			$sel_ix = $ix;
		}
		$ix++;
	}
	print qq|\t</select>\n|;
	#指定された班をディフォルトとして選択する
	print qq|<script>var obj = document.getElementById("cmbHanNo");|;
	print qq|obj.selectedIndex = $sel_ix;</script>\n|;
	
	return $SelHan;
}
	
#年間行事一覧を表示
sub	ShowNendolist
{
	my $showMode = shift @_;		# 表示タイプ 
	my $startym = shift @_;			# 表示年 
	my @records;
	my $record;
	my @weekdatas;
	my ($rdDate, $rdNo, $rdBunrui, $rdGyojiMei, $rdTime,$rdSanka);

	#print qq|DEBUG ShowNendolist showMode[$showMode]\n,startym[$startym]<br>\n |;

	#体制リストから表示可能な年度を読込み、ドロップダウンリストを作成する
	$db = DBI->connect($dbConnect, $userName, $password);
	$db->do("set names utf8");

	&GetNenMaxMin();
	
	print qq|\t<div class="selectbox color">\n|;
	print qq|\t<select id="cmbYear" name="rdYear" onchange="location.href=value;">\n|;
	my $ix = 0;
	my $sel_ix = 0;
	$chkYY = $startym;
	for (my $outNendo = $NendoMin;$outNendo le $NendoMax;$outNendo++) {
		my $linkUrl = "$ThisScCgi?hanno=$HanNo&mode=$mode&start=" . $outNendo . "-01-01";
		print qq|\t\t<option value="$linkUrl">$outNendo</option>\n|;
		if($chkYY eq $outNendo) {
			$sel_ix = $ix;
		}
		$ix++;
	}
	print qq|\t</select>年度|;
	#指定された年度をディフォルトとして選択する
	print qq|\t<script>var obj = document.getElementById("cmbYear");|;
	print qq|obj.selectedIndex = $sel_ix;</script>\n|;
	#print qq|</form>|;
	
	my $SelHan = &ShowHanCombo();	#	班の選択ドロップを表示
	print qq|　の活動リスト\n</div>|;
	
	print qq|
	<script type="text/javascript">
		function AllDataChecked(chkObj){ 
			if(chkObj.checked) {
				window.location.href = "$ThisScCgi?hanno=$HanNo&mode=$mode&start=$rdDate&chkAllData=1&hanchange=1";
			}
			else {
				window.location.href = "$ThisScCgi?hanno=$HanNo&mode=$mode&start=$rdDate&hanchange=1";
			}
		}
	</script>\n|;
	if($mode eq "nendolist") {
		if($HanBit eq TARGET_ALL_DATA) {
			print qq|<input type="checkbox" name="chkAllData" checked="checked"|;
		}
		else {
			print qq|<input type="checkbox" name="chkAllData"|;
		}
		print qq| onclick="AllDataChecked(this)"> 全班の行事<br>\n|;
		if($HanBit eq TARGET_ALL_DATA) {
			print qq|<script>
				var elm = document.getElementById('cmbHanNo');
				elm.disabled = true;
				var style = elm.style;
				style.color = 'green';
			</script>\n|;
		}
	}
	
	print qq|<div id="output"></div>|;

	my $NameCnt = 0;
	my $SankaSql;

	# HTML表示(TABLE HEAD)
	print qq|<table class="katsudo_hyo"><tr>|;

	if($mode eq "nendolist") {
		print qq|<th>日時</th><th>項目</th>|;
		if($HanNo eq 0) {
			print qq|<th>対象</th>|;
		}
	}
	elsif($mode eq "nendoSanka") {
		print qq|<th>日時<br>活動名</th>|;
		#$SankaSql = << "EOS";		#	当年の団員名リストを読み込む
		#select t.nendo,t.kaikyu,d.Name 
		#	from sybo_taisei t 
		#	join sybo_danin d ON t.DaninNo = d.No 
		#	where Nendo=$startym and KuNo=$HanNo;
		$SankaSql = << "EOS";		#	当年の団員名リストを読み込む
		select t.nendo,t.kaikyu,d.Name from 
			(select * from sybo_taisei where Nendo=$startym and KuNo=$HanNo) t 
			join sybo_danin d ON t.DaninNo = d.No 
			where t.Nendo=$startym and d.KuNo=$HanNo
			order by t.TaiseiNo;
EOS
		$sth = $db->prepare($SankaSql);
		my $rv = $sth->execute;

		#メンバーリスト見出しを作成
		while ($hash_ref = $sth->fetchrow_hashref) {
			my %row = %$hash_ref;
			my $Name = $row{Name};
			#$Name =~ s/\p{blank}/<br>/g;	# 全角SPACEを <br> タグに置き換え
			$Name =~ s/\s/<br>/g;			# SPACEを <br> タグに置き換え
			print qq|<th>$Name</th>\n|;
			$NameCnt++;
		}
		
	}
	print qq|</tr>\n|;

	# HTML表示(TABLE BODIES)
	$StartDay = "'$startym" . "-04-00'";
	$startym = $startym + 1;
	$EndDay    = "'$startym" . "-03-31'";
	#$sqlStr = << "EOS";
	#SELECT No,Date,GyojiMei,StartTime,EndTime,Sanka 
	#FROM sybo_gyoji
	#where Date BETWEEN $StartDay AND $EndDay $TargetCheck
	#order by Date;
	$sqlStr = << "EOS";		#	当年の団員名リストを読み込む
	SELECT g.No,g.Date,g.GyojiMei,g.StartTime,g.EndTime,g.TargetFlags,s.SankaStr 
		FROM sybo_gyoji g 
		LEFT JOIN (select * from sybo_sanka where KuNo=$HanNo and IsYotei=0) s on g.No = s.GyojiNo
		where g.Date BETWEEN $StartDay AND $EndDay $TargetCheck
		order by Date;
EOS

	dbg_print("DEBUG ShowNendolist SankaSql=[$SankaSql]<br>LIST[$sqlStr]\n");

	$sth = $db->prepare($sqlStr);
	my $rv = $sth->execute;
	
	my $scMitei;	#開催日未定行事
	my $CurMonthNo = "";
	my $CurMonthID = "";
	while (my $hash_ref = $sth->fetchrow_hashref) {
		my %row = %$hash_ref;
		my $recno	= $row{No};
		$rdDate 	= $row{Date};
		my $rdYear	= substr($rdDate,0,4);
		my $rdMonth	= substr($rdDate,5,2);
		my $rdDay	= substr($rdDate,8,2);
		my $week	= &get_week($rdYear,$rdMonth,$rdDay);
		my $rdTargets = $row{TargetFlags};
		my $timeStr = "$row{StartTime}";
		my $timeLen = length($timeStr);
		if($timeLen eq 3) {
			$timeStr = "0" . substr($row{StartTime},0,1) . ":" . substr($row{StartTime},1,2);
		}
		elsif($timeLen eq 4) {
			$timeStr = substr($row{StartTime},0,2) . ":" . substr($row{StartTime},2,2);
		}
		else {
			$timeStr = "--:--";
		}
		if($CurMonthNo ne $rdMonth) {
			$CurMonthID = q| id="ID_| . $rdMonth . q|"|;
			$CurMonthNo = $rdMonth;
		}
		else {
			$CurMonthID = "";
		}
		
		if($mode eq "nendolist") {
			print qq|<tr$CurMonthID><td>$rdYear/$rdMonth/$rdDay($week) $timeStr</td><td><a href="$ThisScCgi?hanno=$HanNo&mode=$LinkDetail&start=$rdDate&recno=$recno">$row{GyojiMei}</a></td>\n|;
			if($HanNo eq 0) {
				
				#本部ならば参加対象班を表示
				print qq|<td>|;
				if($rdTargets eq TARGET_ALL_DATA) {
					print qq|全班|;
				}
				else {	
				
					my $chkBit = 1;
					for (my $ix = 0; $ix < $HAN_CNT; $ix++) {
						# Bit値で参加対象班を判定
						if(($rdTargets & $chkBit) ne 0) {
							#print qq|$HanList[$ix],|;
							if($ix eq 0) {
								print qq|<span class="taiMaruHon">本</span>|;
							}
							else {
								print qq|<span class="taiMaruHan">$ix</span>|;
							}
						}
						$chkBit *= 2;
					}
				}
				print qq|</td>\n|;
			}
			print qq|</tr>\n|;
			if($rdDay eq "00") {	#開催日未定リストに追加
				$scMitei = $scMitei . $rdMonth . "月 " . $row{GyojiMei} . "<br>\n";
			}
		}
		elsif(($mode eq "nendoSanka") and ($rdDay ne "00")) {
			#日時とタイトル
			print qq|<tr$CurMonthID><td>$rdYear/$rdMonth/$rdDay $timeStr<br><a href="$ThisScCgi?hanno=$HanNo&mode=$LinkDetail&start=$rdDate&recno=$recno">$row{GyojiMei}</a></td>|;
			
			#参加マーク('●' or '-')を表示
			$rdSanka = $row{SankaStr};	#Gyoji=Sanka,sybo_sanka=SankaStr
			my @rdFlsgs = split(/#/,$rdSanka);
			for($ix=0;$ix<$NameCnt;$ix++) {
				if(@rdFlsgs[$ix] eq "1") {
					print qq|<td align="center">●</td>|;
					@Kaisu[$ix]++;
				}
				else {
					print qq|<td align="center">-</td>|;
				}
			}
			print qq|</tr>\n|;
		}
	}

	if($mode eq "nendoSanka") {		#参加リストならば回数合計欄を表示
		print qq|<tr><td>出動回数</td>|;
		for($ix=0;$ix<$NameCnt;$ix++) {
			print qq|<td>@Kaisu[$ix]</td>|;
		}
		print qq|</tr>\n|;
	}
	
	# HTML表示(TABLE BODY ,TABLE END)
	print qq|</tbody>\n</table>\n|;

	if($showMode eq SHOW_MODE_GYOJI and $scMitei ne "") {
		print qq|	<p class="notice">|;
		print qq|		---日付未定行事---<br>$scMitei |;
		print qq|	</p>|;
	}

	$sth->finish;
	
}


#新しい予定を入力
sub newSchedule
{
	&InputGyoji(INPUT_MODE_NEW,ENTRY_MODE_ADM);
}

#行事の表示
#新規追加の場合はデータレコードが空欄となる
#[保存]押下で &SaveGyoji() を呼ぶ
sub	ShowGyoji
{
	print qq|\t<div class="selectbox color">|;
	&ShowHanCombo();
	print qq|</div>|;
	

	if($rdMemo eq "") {	$rdMemo = "　";	}
	my $wkStartMM =  sprintf("%02d",$rdStartMM);
	my $wkEndMM =  sprintf("%02d",$rdEndMM);
	print qq|<table  class="gyoji_hyo"><br>|;
	print qq|<tr><th>日時</th><td>$rdYear 年  $rdMonth 月  $rdDay 日 ($rdWeek)  $rdStartHH:$wkStartMM ～ $rdEndHH:$wkEndMM</td></tr>\n|;
	print qq|<tr><th>分類</th><td>$rdBunrui </td></tr>\n|;
	print qq|<tr><th>活動名</th><td>$rdGyojiMei </td></tr>\n|;
	print qq|<tr><th>集合場所</th><td>$rdSyugo </td></tr>\n|;
	print qq|<tr><th>服装</th><td>$FukusoList[$rdFukuso] , $ShoseList[$rdKutsu] , $AtamaList[$rdAtama]</td></tr>\n|;
	$rdMemo =~ s/\n/<br>/g;
	print qq|<tr><td colspan=2>$rdMemo</td></tr>|;
	print qq|<tr><td colspan=2><a href="$ThisScCgi?mode=ShowSankaYotei&recno=$rdNo&HanNo=$HanNo">参加予定団員確認</a></td></tr>\n</table>|;

	my $PdfFile = "./doc/Sy$rdYear$rdMonth$rdDay"."*.*";
	@filelist = glob($PdfFile);
	my $filecnt = @filelist;
	#if(-f @list) {
		
	print qq|
		<div class="group_box">
			<span class="box-title">活動資料</span>|;

	my $cnt = 1;	
	my $bRepName;	
	foreach $PdfFile (@filelist){
		
		#	文書名を取得	
		$SqlStr	= "select BunsyoNo,BunsyoGyojiNo,BunsyoMotoName from sybo_bunsyo where " .
					"BunsyoFileName='$PdfFile'";
		my $sth = $db->prepare($SqlStr);
		my $rv = $sth->execute;
		my $hash_ref = $sth->fetchrow_hashref;
		my %row = %$hash_ref;
		$bRepName	= false;

		#print qq|SqlStr[$SqlStr] Cnt=$rv　　\n|;

		if($rv eq 1) {
			#読み込んだデータを格納
			$rdBunsyoNo			= $row{BunsyoNo};
			$rdBunsyoGyojiNo	= $row{BunsyoGyojiNo};
			$rdBunsyoMotoName	= $row{BunsyoMotoName};
		
			if($rdBunsyoGyojiNo eq $rdNo) {
				print qq|<a href="$PdfFile">$rdBunsyoMotoName</a><i class="fa-regular fa-file"></i><br>\n|;
			}
			# 違う行事のものは表示しない
			$bRepName	= true;
		}	
		$sth->finish;
		
		if($bRepName eq false) {
			my	@filename    = split(/\./, $PdfFile);
			my	$fileExt = $filename[@filename - 1];
			$fileExt =~ tr/A-Z/a-z/;
			print qq|<a href="$PdfFile">資料ファイル$cnt($fileExt)</a><i class="fa-regular fa-file"></i><br>\n|;
		}
		$cnt++;	
	}
	print qq|</div><br>\n|;
	
	if($rdSiryo ne "") {
		print qq|<a href="$rdSiryo">参考LINK</a><br>\n|;
	}
	print qq|<a class="btn--orange" href="$ThisScCgi?mode=UploadPdfSel&recno=$rdNo">資料の登録/入替</a><hr>|;
	#	参加予定団員の編集
	#	https://kyum.chu.jp/syobo/sc.cgi?mode=SankaYoteiEdit&recno=353&hanno=1
	if($HanNo eq 0) {	#分団の設定ならば参加対象とする班を表示
		print qq|<br><b>参加対象班:<br></b>|;
		dbg_print("flags = $rdTargets ,$HAN_CNT<br>");
		my $chkBit = 1;
		for (my $ix = 0; $ix < $HAN_CNT; $ix++) {
			# Bit値で参加対象班を判定
			if(($rdTargets & $chkBit) eq 0) {
				print qq|×$HanList[$ix]|;
			}
			else {
				print qq|〇$HanList[$ix]|;
			}
			if(($ix % 5) eq 0) {
				print "<br>";
			}
			else {
				print ",";
			}
			$chkBit *= 2;
		}
	}
	elsif($HanBit ne TARGET_ALL_DATA) {
		#班の設定ならば
		#班の単独行事であるかを判定
		my $chkBit = 1,$findCnt = 0;
		for (my $ix = 0; $ix < $HAN_CNT; $ix++) {
			if(($rdTargets & $chkBit) ne 0) {
				$findCnt++;
			}
			$chkBit *= 2;
		}
		#print qq|DEBUG HAN check HanBit[$HanBit]\n,findCnt[$findCnt]<br>\n |;
		
		if($findCnt eq 1) {
			#班単独の行事ならば、編集のリンクを表示  https://kyum.chu.jp/syobo/
			print qq|<button type=“button” onclick="location.href='$ThisScCgi?hanno=$HanNo&mode=editgyoji&recno=$rdNo'">行事の編集</button>　　　\n|;
			print qq|<button type=“button” onclick="location.href='$ThisScCgi?hanno=$HanNo&mode=SankaEdit&recno=$rdNo'">参加団員編集</button><br>\n|;
		}
	}
}


#行事の編集
#新規追加の場合はデータレコードが空欄となる
#[保存]押下で &SaveGyoji() を呼ぶ
sub	InputGyoji
{
	my $IsNewData  = shift @_;			# 新な行事の追加であるか 	INPUT_MODE_NEW / _UPDATE
	my $IsHanGyoji = shift @_;			# 班行事の追加であるか 	ENTRY_MODE_ADM / _HAN

	#・IsNewData = [$IsNewData],IsHanGyoji = [$IsHanGyoji]<br>
	
	print qq|
	
	<script type="text/javascript">
	function InputGyojiCheck(reqForm,reqMode){
		if(reqMode == 2) {
			if(reqForm.rdHanNoReq.selectedIndex < 1) {
				window.alert("班が指定されていません。");
				return false;
			}
		}
		if(reqForm.rdStartMM.selectedIndex < 1) {
			window.alert("月度が指定されていません。");
			return false;
		}
		if(reqForm.rdKind.selectedIndex < 1) {
			window.alert("分類が指定されていません。");
			return false;
		}
		if(reqForm.rdTitle.value == "") {
			window.alert("活動名が入力されていません。");
			return false;
		}
		if(reqForm.rdSyugo.value == "") {
			window.alert("集合場所が入力されていません。");
			return false;
		}
		if(reqForm.rdAtama.selectedIndex < 0) {
			window.alert("帽子が指定されていません。");
			return false;
		}
		if(window.confirm("登録して宜しいですか？")){
			return true;
		} else {
			//window.alert("戻るボタンを押して入力しなおしてください。");
			return false;
		}
	}
	</script>|;
	
	print qq|<form onsubmit="return InputGyojiCheck(this,$IsHanGyoji)">\n|;
	if($IsHanGyoji eq ENTRY_MODE_ADM) {
		#管理者モード
		print qq|<input type="hidden" name="hanno" value="$HanNo">|;
		print qq|<input type="hidden" name="mode" value="SaveGyojiAdm">\n|;
	}
	else {
		#班行事 ENTRY_MODE_HAN
		if($IsNewData eq INPUT_MODE_NEW) {
			my $ix = 0,$sel_ix = 3;
			print qq|\t　班：<select id="rdHanNoReq" name="rdHanNoReq">
							<option value="99"></option>\n|;
			foreach my $HanName (@HanList){
				print qq|\t\t<option value="$ix">$HanName</option>\n|;
				$ix++;
			}
			print qq|\t</select>\n|;
		}
		else {
			#$IsNewData eq INPUT_MODE_UPDATE) {
			print qq|<br>$HanList[$HanNo]\n|;
		}
		print qq|<br>\n|;
		print qq|<input type="hidden" name="mode" value="SaveGyojiHan">\n|;
	}
	print qq|<input type="hidden" name="recno" value="$rdNo">\n|;
	print qq|<input type="hidden" name="rdSanka" value="$rdSanka">\n|;

	my $ix = 0, $SelIx = 0;
	my $chkYY = $gCurYY;
	#if($gCurMM < 4) {
	#	$chkYY--;
	#}
	print qq|日付：|;
	#print qq|<SPAN class="RequiredLabel">|;
	print qq|<select class="date_sel" id="rdYear" name="rdYear">\n|;
	for (my $outNendo = $NendoMin;$outNendo le $NendoMax;$outNendo++) {
		# 登録や更新ならば数字だけを
		print qq|\t<option value="$outNendo">$outNendo</option>\n|;
		if($rdYear > 0) {
			if($rdYear eq $outNendo) {
				$SelIx = $ix;
			}
		}
		else {
			if($chkYY eq $outNendo) {
				$SelIx = $ix;
			}
		}
		$ix++;
	}
	print qq|</select>年　\n|;
	print qq|<script>
				var obj = document.getElementById("rdYear");
				obj.selectedIndex = $SelIx;
		</script>|;
	
	#月度のドロップダウン作成
	#print qq|<input type="text" name="rdMonth" value="$rdMonth">月|;
	#&datefuncs::SelectYY(rdKyYear,	$rdKyYear);	print "年 ";
	#&datefuncs::SelectMM("rdMonth",$rdMonth);	print "月 ";
	
	print qq|<select id="rdMonth" name="rdMonth">\n\t<option value=""></option>\n|;
	my $strTemp;
	for( $ix=1;$ix<=12;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|\t<option value="$strTemp">$strTemp</option>\n|;
		if($rdMonth eq $strTemp) {
			print qq|<script>var obj = document.getElementById("rdMonth");|;
			print qq|obj.selectedIndex = $ix;</script>|;
		}
	}
	print qq|</select>月 \n|;
	
	#日のドロップダウン作成
	#&datefuncs::SelectDD("rdDay",	$rdDay);	print "日 ";
	#print qq|<input type="text" name="rdDay" value="$rdDay">日<br>|;
	print qq|<select id="rdDay" name="rdDay">\n|;
	my $strTemp;
	for( $ix=0;$ix<=31;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|<option value="$strTemp">$strTemp</option>\n|;
		if($rdDay eq $strTemp) {
			print qq|<script>var obj = document.getElementById("rdDay");|;
			print qq|obj.selectedIndex = $ix;</script>|;
		}
	}
	print qq|</select>日 </SPAN>\n・・未定の場合は00日とする<br>\n|;

	#開始時間
	print qq|時間：<select id="rdStartHH" name="rdStartHH"><option value=""></option>\n|;
	my $strTemp;
	for( $ix=0;$ix<30;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|\t<option value="$strTemp">$strTemp</option>\n|;
		#if($rdStartHH eq $strTemp) {
		if($rdStartHH eq $ix) {
			print qq|<script>var obj = document.getElementById("rdStartHH");|;
			print qq|obj.selectedIndex = $ix + 1;</script>|;
		}
	}
	print qq|</select>：|;

	#print qq|<input type="text" name="rdMM" value="$rdMM"><br>|;
	print qq|<select id="rdStartMM" name="rdStartMM">\n\t<option value=""></option>\n|;
	my $selNo=0;
	for( $ix=0;$ix<=59;$ix+=5) {
		$selNo++;
		$strTemp = sprintf("%02d",$ix);
		print qq|\t<option value="$strTemp">$strTemp</option>\n|;
		#if($rdStartMM eq $strTemp) {
		if($rdStartMM eq $ix) {
			print qq|<script>var obj = document.getElementById("rdStartMM");|;
			print qq|obj.selectedIndex = $selNo;</script>|;
		}
	}
	print qq|</select>～|;

	#終了時間
	#print qq|<input type="text" name="rdHH" value="$rdHH">～|;
	print qq|<select id="rdEndHH" name="rdEndHH"><option value=""></option>|;
	my $strTemp;
	for( $ix=0;$ix<30;$ix++) {
		$strTemp = sprintf("%02d",$ix);
		print qq|<option value="$strTemp">$strTemp</option>|;
		#if($rdEndHH eq $strTemp) {
		if($rdEndHH eq $ix) {
			print qq|<script>var obj = document.getElementById("rdEndHH");|;
			print qq|obj.selectedIndex = $ix + 1;</script>|;
		}
	}
	print qq|</select>：|;

	print qq|<select id="rdEndMM" name="rdEndMM"><option value=""></option>|;
	my $selNo=0;
	for( $ix=0;$ix<=59;$ix+=5) {
		$selNo++;
		$strTemp = sprintf("%02d",$ix);
		print qq|<option value="$strTemp">$strTemp</option>|;
		#if($rdEndMM eq $strTemp) {
		if($rdEndMM eq $ix) {
			print qq|<script>var obj = document.getElementById("rdEndMM");|;
			print qq|obj.selectedIndex = $selNo;</script>|;
		}
	}
	print qq|</select><br>\n|;

	#print qq|<SPAN class="RequiredLabel>分類：\n<select id="rdKind" name="rdKind">\n\t<option value=""></option>\n|;
	print qq|分類：<select id="rdKind" name="rdKind">\n\t<option value=""></option>\n|;
	$ix = 1;
	foreach my $seal ( @seals ) {
		print qq|\t<option value="$seal">$seal</option>\n|;
		if($rdBunrui eq $seal) {
			print qq|<script>var obj = document.getElementById("rdKind");|;
			print qq|obj.selectedIndex = $ix;</script>|;
		}	
		$ix++;
	}
	print qq|</select>\n<BR>\n|;
	

	print qq|活動名：<SPAN class="RequiredLabel cp_iptxt">\n
			<input type="text" name="rdTitle" value="$rdGyojiMei" style="width: 20em;"></SPAN><br>\n|;

	print qq|集合場所：<SPAN class="RequiredLabel cp_iptxt">\n
			<input type="text" name="rdSyugo" value="$rdSyugo" style="width: 20em;"></SPAN><br>\n|;

	#頭・服装と靴は、とりあえず配列から読むことにする
	print qq|服装：<select id="rdFukuso" name="rdFukuso"></option>|;
	$ix = 0;
	foreach my $Fukuso ( @FukusoList ) {	# 服装リスト
		print qq|<option value="$ix">$Fukuso</option>|;
		if($rdFukuso eq $ix) {
			print qq|<script>var obj = document.getElementById("rdFukuso");|;
			print qq|obj.selectedIndex = $ix;</script>|;
		}	
		$ix++;
	}
	print qq|</select><br>\n|;

	print qq|帽子：<select id="rdAtama" name="rdAtama"></option>|;
	$ix = 0;
	foreach my $Atama ( @AtamaList ) {	# 帽子リスト
		print qq|<option value="$ix">$Atama</option>|;
		if($rdAtama eq $ix) {
			print qq|<script>var obj = document.getElementById("rdAtama");|;
			print qq|obj.selectedIndex = $ix;</script>|;
		}	
		$ix++;
	}
	print qq|</select><br>\n|;
	
	print qq|靴：<select id="rdShose" name="rdShose"></option>|;
	$ix = 0;
	foreach my $Shose ( @ShoseList ) {	# 靴リスト
		print qq|<option value="$ix">$Shose</option>|;
		if($rdKutsu eq $ix) {
			print qq|<script>var obj = document.getElementById("rdShose");|;
			print qq|obj.selectedIndex = $ix;</script>|;
		}	
		$ix++;
	}
	print qq|</select><br>|;

	if($IsHanGyoji eq ENTRY_MODE_HAN) {
		#班の行事登録ならば何もしない
	}
	elsif($HanNo eq 0)  {
		#分団の設定ならば参加対象とする班を選択
		print qq|参加対象班：<br>|;
		my $chkBit = 1;
		for (my $ix = 0; $ix < $HAN_CNT; $ix++) {
			# Bit値で参加対象班を指定
			if((($rdTargets & $chkBit) eq 0) and ($IsNewData eq INPUT_MODE_UPDATE)) {
				#更新ならばフラグ値でチェックON/OFFを切り替え
				print qq|<input type="checkbox" name="tg$ix" value="$ix" >$HanList[$ix]|;
			}
			else {
				#新規ならば全てのチェックをON
				print qq|<input type="checkbox" name="tg$ix" value="$ix" checked="checked">$HanList[$ix]|;
			}
			$chkBit *= 2;
			if(($ix % 5) eq 0) {
				print qq|<br>|;
			}
			else {
				print qq|,|;
			}
		}
	}
	else {
		print qq|<input type="hidden" name="tg$HanNo" value="$HanNo">|;
	}
	
	print qq|<br>コメント<br>
			<TextArea name="rdComment" rows=5 cols=38>$rdMemo</TextArea><br>|;
	
		#<TextArea name="EditNewsText" rows=30 cols=120>' . $content . '</TextArea>
		#<input type="text" name="rdComment" value="$rdMemo" style="width: 50em;"><br>|;

	print qq|<input type="submit" value="保存"></form></div>|;
}

#行事の編集
sub	outeditgyoji
{
	if($mode eq "ShowGyoji") {
		print qq|行事の表示 No.$recno\n|;
		&ShowGyoji();	#行事明細の表示画面
	}
	else {
		print qq|行事の編集 No.$recno\n<form>|;
		if($IsAdmin eq true) {	#行事明細の編集画面
			&InputGyoji(INPUT_MODE_UPDATE,ENTRY_MODE_ADM);
		}
		else {
			&InputGyoji(INPUT_MODE_UPDATE,ENTRY_MODE_HAN);
		}
	}

	#参加者フラグを読込
	$sqlStr = "select SankaStr from sybo_sanka where GyojiNo=$recno and KuNo=$HanNo and IsYotei=0;";
	$sth = $db->prepare($sqlStr);
	$rvFlag = $sth->execute;
	if($rvFlag > 0) {
		my $ary_ref = $sth->fetchrow_arrayref;
		$rdSanka	= $ary_ref->[0];
	}
	dbg_print("<br>DEBUG Sanka Flag SQL=[$sqlStr],Result=[$rdSanka]<br>");

	#参加者リストを読込
	$sqlStr = << "EOS";		#	団員名を読み込む
	select t.Nendo,t.Kaikyu,d.Name
		from sybo_taisei t
		join (select * from sybo_danin d where KuNo=$HanNo) d ON t.DaninNo = d.No
		where t.Nendo=$rdNendo and t.KuNo=$HanNo
		order by t.TaiseiNo;
EOS

	dbg_print("<br>DEBUG Sanka List=[$sqlStr]<br>");

	@rdFlags = split(/#/,$rdSanka);
	$sth = $db->prepare($sqlStr);
	$rv = $sth->execute;
	#$sth->finish;
	my $ix = 0;
	my $myKey = $rdDate . $rdNo;

	print qq|<br><b>参加者</b><br>|;
	while ($hash_ref = $sth->fetchrow_hashref) {
		my %t_row = %$hash_ref;
		my $member = $t_row{Name};

		my $rdFlag = $rdFlags[$ix];
		if($rdFlag == 1) {
			print qq|●　$ix. $member<br>|;
		}
		else {
			print qq|×　$ix. $member<br>|;
		}
		$ix++;
	}


	if($mode eq "ShowGyoji") {
		#表示のみならば、前後の予定を検索してリンクを作成
		#同じ日に複数の行事がある場合もあるため、年月日(10桁)+RecNo(4桁)で比較する
		my $BfrKey="0000-00-000000",$BfrRec="";
		my $NxtKey="9999-99-999999",$NxtRec="";
		my $rdKey;

		my $intvYear	= $rdYear;
		$StartDay = "'$intvYear" . "-04-00'";
		$intvYear = $intvYear + 1;
		$EndDay    = "'$intvYear" . "-03-31'";

		my $sqlStr = << "EOS";
		SELECT No,Date 
		FROM sybo_gyoji 
		where Date BETWEEN $StartDay AND $EndDay
		order by Date,StartTime;
EOS
		my $sth = $db->prepare($sqlStr);
		my $rv = $sth->execute;

		while (my $hash_ref = $sth->fetchrow_hashref) {
			my %row = %$hash_ref;
			my $rdDate 	= $row{Date};
			my $rdNo	= $row{No};

			$rdKey = $rdDate . $rdNo;
			#Before側の取得
			if(($rdKey lt $myKey) && ($rdKey gt $BfrKey)) { 
				$BfrKey = $rdKey;
				$BfrRec = $rdNo;
			}
			#Next側の取得
			if(($rdKey gt $myKey) && ($rdKey lt $NxtKey)) { 
				$NxtKey = $rdKey;
				$NxtRec = $rdNo;
			}
		}
		
		if($BfrRec eq "") {
			print qq|<hr><br>前の予定 |;
		}
		else {
			my $BfrDate = substr($BfrKey,0,10);
			my $BfrRecNo = substr($BfrKey,10,4);
			print qq|<hr><br><a href="$ThisScCgi?hanno=$HanNo&mode=ShowGyoji&start=$BfrDate&recno=$BfrRecNo">前の予定</a></td>|;
		}
		print qq| ←□□□→ |;
		if($NxtRec eq "") {
			print qq|次の予定 |;
		}
		else {
			my $NxtDate = substr($NxtKey,0,10);
			my $NxtRecNo = substr($NxtKey,10,4);
			print qq|<a href="$ThisScCgi?hanno=$HanNo&mode=ShowGyoji&start=$NxtDate&recno=$NxtRecNo">次の予定</a></td>|;
		}
	}
	else {
		
		# 参加団員の編集へ
		print qq|<form>|;
		print qq|<input type="hidden" name="hanno" value="$HanNo">|;
		print qq|<input type="hidden" name="recno" value="$rdNo">|;
		print qq|<input type="hidden" name="mode" value="SankaEdit">|;
		print qq|<input type="submit" value="参加団員編集">|;
		print qq|</form><br>\n|;


		print qq|
		<script type="text/javascript">
		function DeleteGyojiConfirm(reqForm){
			if(window.confirm("$rdGyojiMei を削除していいですか？")){
				return true;
			} else {
				//window.alert("戻るボタンを押して入力しなおしてください。");\n
				return false;
			}
		}
		</script>\n<br>\n|;
		
		print qq|<form onsubmit="return DeleteGyojiConfirm(this)">\n|;
		print qq|<input type="hidden" name="recno" value="$rdNo">\n|;
		print qq|<input type="hidden" name="mode" value="DeleteGyoji">\n|;
		print qq|<input type="submit" value="この行事を削除">\n|;
		#print qq|<br><br><a href="$ThisScCgi?mode=DeleteGyoji&recno=$rdNo">この行事を削除  </a></td>|;
		print qq|</form>|;
		
		print qq|</div>|;
	}
}

# spaceとTABの除去
sub trim {
	my $val = shift;
	$val =~ s/^\s*(.*?)\s*$/$1/;
	return $val;
}

#資料pdfの登録/入替
sub	UploadPdfSel{
	
	print qq|$rdYear 年  $rdMonth 月  $rdDay 日 ($rdWeek)<br>\n|;
	print qq|$rdGyojiMei の資料ファイル<br><div class="small">※PDF,jpeg,gifとpngが登録可能</div><br><br>\n|;
	
	print qq|<form action="$ENV{'SCRIPT_NAME'}" method="POST" enctype="multipart/form-data">\n|;
	print qq|資料ファイル：<br><input type="file" name="pdf" value="" size="50"><br>\n|;
	print qq|<input type="hidden" name="recno" value="$rdNo">|;
	print qq|<input type="hidden" name="hanno" value="$HanNo">|;
	print qq|<input type="hidden" name="mode" value="UploadPdfWrite">|;
	print qq|<input type="submit" value="登録"></form></div>|;
	print qq|</form>|;
}

sub UploadPdfWrite{
	#print qq| NO=$rdNo($recno):$rdCount ,$mode . 年月日＝ $rdYear / $rdMonth / $rdDay じゃ <br> $sqlStr<br>|;	

	print qq|$rdYear 年  $rdMonth 月  $rdDay 日 ($rdWeek)<br>\n|;
	print qq|$rdGyojiMei の資料ファイルをUpload中<br>\n|;

	#my	$SrcFile = $FORM{'pdf'};
	my	@filename    = split(/\./, $SrcFile);
	my	$fileExt = $filename[@filename - 1];
	$fileExt =~ tr/A-Z/a-z/;

	#print qq|[$SrcFile]->[$PathName]<br>\n|;
	
	if(length($SrcFile) > $IMGMAX) {
		errorexit("ファイル サイズ オーバー！！　（" . length($SrcFile) . "バイト）");
    }
    elsif(	$fileExt eq "pdf" or 
			$fileExt eq "xls" or 
			$fileExt eq "xlsx" or 
			$fileExt eq "doc" or 
			$fileExt eq "docx" or 
			$fileExt eq "txt" or 
			$fileExt eq "jpg" or 
			$fileExt eq "jpeg" or 
			$fileExt eq "gif" or 
			$fileExt eq "png") {

		# 既存ファイルがあれば連番を付与
		my $PdfFile = "./doc/Sy$rdYear$rdMonth$rdDay"."*.*";
		@filelist = glob($PdfFile);
		my $filecnt = @filelist;
		
		my $cnt = 1;	
		foreach $PdfFile (@filelist){
			my	@filename	= split(/\./, $PdfFile);
			my	$filehon	= $filename[1];	# なぜか１でなければダメ..(-_-;
			my	@splFile = split(/-/, $filehon);	# ハイフン以降があるかをチェック
			
			my	$fileto	= $splFile[0];
			
			if(@splFile > 1) {
				$cntNum = $splFile[1];
				$cnt = $cntNum+1;
			}
		}
		my	$DestFile = 'Sy' . $rdYear . $rdMonth . $rdDay . '-' . $cnt . '.' . $fileExt;
		my	$PathName = './doc/' . $DestFile;

		# 元ファイルと同じファイルが登録済であるかをチェック
		my $sql = "select BunsyoNo,BunsyoFileName from sybo_bunsyo " .
			"where BunsyoGyojiNo=$rdNo and BunsyoMotoName='$SrcFile';";
		my $sth = $db->prepare($sql);
			
		my $rv = $sth->execute;
		my @ary = $sth->fetchrow_array;

		my $cnt = @ary;
		if($cnt > 0) {
			#見つかった場合はファイルを上書きする
			$PathName = $ary[1];
			$sth->finish;
			
			my $sql = "delete from sybo_bunsyo where BunsyoGyojiNo=$rdNo and BunsyoMotoName='$SrcFile';";
			$sth = $db->prepare($sql);
			my $rv = $sth->execute;
			print qq|[$SrcFile]に上書き。<br>[$sql]<br>\n|;
		}
		else {
			print qq|[$SrcFile]に置きました。<br>\n|;
		}

		# 受信ファイルの書き込み
		open(OUT, ">$PathName") or errorexit("ファイル作成に失敗しました！！");
		binmode(OUT);
		while(read($SrcFile,$buffer,1024))
		{
			print OUT $buffer;
		}
		close(OUT);

		
		##	文書テーブル sybo_bunsyo の更新

		#	登録する文書番号を取得
		my $sth = $db->prepare("select max(BunsyoNo) from sybo_bunsyo;");
		my $rv = $sth->execute;
		@ary = $sth->fetchrow_array;
		$BunsyoNoMax = $ary[0] + 1;
		$sth->finish;

		my ($curSec,$curMin,$curHour,$curMday,$curMon,$curYear,$curWday,$curYday,$curIsdst) = localtime(time);
		my	$EnterDate = sprintf("'%04d-%02d-%02d'",$curYear + 1900, $curMon + 1, $curMday );

		#	ファイル名を記録
		$SqlStr	= "Insert into sybo_bunsyo set " .
					"BunsyoNo=$BunsyoNoMax,BunsyoGyojiNo=$rdNo," .
					"BunsyoFileName='$PathName'," .
					"BunsyoMotoName='$SrcFile'," .
					"BunsyoDate=$EnterDate";
		my $sth = $db->prepare($SqlStr);
		my $rv = $sth->execute;
		$sth->finish;
					
		print qq|[$SrcFile]のUploadが完了しました。<br>\n|;
	}
	else {
		errorexit("扱えないファイル形式です");
	}

	print qq|<button type=“button” onclick="location.href='$ThisScCgi?hanno=$HanNo&mode=ShowGyoji&recno=$rdNo'">行事詳細に戻る</button>|;

}

#行事の削除
#新規追加の場合はデータレコードが空欄となる
#[保存]押下で &SaveGyoji() を呼ぶ
sub	DeleteGyoji
{
	#	データベース接続
	$db = DBI->connect($dbConnect, $userName, $password);
	$db->do("set names utf8");
	my $sqlStr = "select Date,GyojiMei from sybo_gyoji where No = $recno;";

	$sth = $db->prepare($sqlStr);
	my $rv = $sth->execute;
	if($rv < 1) {
		print qq|<font size=+2 color=red>該当データがありません</font>|;
	}
	else {
		
		my $hash_ref = $sth->fetchrow_hashref;
		my %row = %$hash_ref;

		#読み込んだデータを格納
		$rdDate		= $row{Date};
		$rdGyojiMei	= $row{GyojiMei};
		
		$sqlStr = "delete from sybo_gyoji where No = $recno;";
		$sth = $db->prepare($sqlStr);
		my $rv = $sth->execute;
		
		$sqlStr = "delete from sybo_sanka where GyojiNo = $recno and IsYotei=0;";
		$sth = $db->prepare($sqlStr);
		my $rv = $sth->execute;
		
		print qq|<font size=+2 color=blue>$rdDate : $rdGyojiMei<br>削除完了</font>|;
	}
	$sth->finish;
	$db->disconnect;
}
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#	団員リストの表示
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
sub outputmemberlist{
	#my $reqNendo = shift @_;			# 表示年

	my $reqNendo = $gCurYY;			# 表示年
	if($gCurMM < 4) {
		$reqNendo--;
	}

	print qq|<br> $reqNendo 年度|;
	print qq|<div class="selectbox color"> |;
	&ShowHanCombo();
	print qq|の団員</div>|;
	my ($curSec,$curMin,$curHour,$curMday,$curMon,$curYear,$curWday,$curYday,$curIsdst) = localtime(time);
	$curYear += 1900;

	$sqlStr = << "EOS";		#	団員名を読み込む
	select t.Nendo,t.Kaikyu,d.Name,d.NyudanNen
		from sybo_taisei t
		join (select * from sybo_danin d where KuNo=$HanNo) d ON t.DaninNo = d.No
		where t.Nendo=$reqNendo and t.KuNo=$HanNo
		order by t.TaiseiNo;
EOS
	#print qq|DEBUG outputmemberlist sqlStr = [$sqlStr] <br>\n|;

	my $sth;
	my $rv;
	#	データベース接続
	$db = DBI->connect($dbConnect, $userName, $password);
	$db->do("set names utf8");
	$sth = $db->prepare($sqlStr)  or die(DBI::errstr);;
	$rv = $sth->execute  or die(DBI::errstr);
	if($@){
		#if(defined($dbh)){ $dbh->disconnect(); }
		print "error(".$@.")\n";
	}

	print qq|<table class="katsudo_hyo">
		<tr><th>階級</th><th>氏名</th><th>団員歴</th></tr>|;

	while ($hash_ref = $sth->fetchrow_hashref) {
		my %t_row = %$hash_ref;
		my $Danreki = $curYear - $t_row{NyudanNen};
		if($curMon > 3) {
			$Danreki++;
		}

		print qq|<tr><td>$t_row{Kaikyu}</td><td>$t_row{Name}</td><td><center>$Danreki</center></td></tr>\n|;
	}
	print qq|</table>|;

	$sth->finish;	#表示終了
	$db->disconnect;
}

sub dbg_print{
	my $msg = shift @_;			# 表示年
	if($IsDebug eq true) {
		print qq| $msg |;
	}
}

# -------------- #
# HTMLタグの処理 #
# -------------- #
sub safetytags {
	my $line = shift @_;

	if( $voidtags == 1 ) {
		# HTMLタグの無効化が設定されていれば実体参照に変換
		$line =~ s/</&lt;/g;
		$line =~ s/>/&gt;/g;
		$line =~ s/"/&quot;/g;
	}

	return $line;
}

# ---------------- #
# エラーメッセージ #
# ---------------- #
sub errorexit
{
	$msg = shift @_;

	print qq|<html lang="ja"><head><title>更新できませんでした</title>|;
	print qq|<meta http-equiv="Content-Type" content="text/html; charset=utf-8">|;
	print qq|</head><body>\n|;
	print qq|<div style="background-color:red; color:#fffff0; font-weight:bold; font-family:Arial,sans-serif; padding:1px;">うまく\表\示できなかったようです</div><br>\n|;
	print qq|<div style="font-size: smaller;">エラー内容：</div>\n|;
	print qq|<div style="border:1px dotted blue; padding:1em;">$msg</div>\n|;
	print qq|<div style="text-align: right;"><form><input type="button" value="戻る" onClick="history.back();"></form></div>|;
	print qq|</body></html>\n|;

	exit;
}

