#! /usr/bin/perl

use lib qw(./);


#vデータベース接続
my $server = "localhost";
my $userName = "kyum";
my $password = "k1lt7Ovl";
my $dbName = "kyum";
my $dbConnect = "DBI:mysql:" . $dbName . ":" . $server;

#対象となる班の指定
my	$HAN_CNT = 11;
my	@HanList = ("分団本部","１区","２区","３区","４区","５区","６区","７区","８区","９区","１０区");	# 分類リスト
my	$Hanmei = @HanList[$HanNo];
my	$gCurYY,$gCurMM;	# 処理対象の年月
my	$gNendo;			# 処理対象の年度(１~３月は年-１となる)

# DBに登録されている最少/最大年度を取得する
#サブルーチンの呼び出し側でも意識してリファレンス（例: \$val）を渡す
#my $NendoMin,$NendoMax;
#&GetNenMaxMin(\$NendoMin,\$NendoMax);  # 呼び出し側ではリファレンスを渡す
sub GetNenMaxMin
{
	my $sth = $db->prepare("select max(Nendo), min(Nendo) from sybo_taisei;");
	my $rv	= $sth->execute;
	@ary = $sth->fetchrow_array;
	
    my($NendoMin) = @_[0];  # スカラ変数のリファレンスを受け取る
    $$NendoMin = $ary[1];    # デリファレンスして代入すると呼び出し元のスカラ変数を変更
	
    my($NendoMax) = @_[1];  # スカラ変数のリファレンスを受け取る
    $$NendoMax = $ary[0];    # デリファレンスして代入すると呼び出し元のスカラ変数を変更

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
