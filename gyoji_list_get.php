<?php

//データベース接続
$server = "localhost";
$userName = "kyum";
$password = "k1lt7Ovl";
$dbName = "kyum";

$mysqli = new mysqli($server, $userName, $password,$dbName);

if ($mysqli->connect_error){
    echo $mysqli->connect_error;
    exit();
}
else{
    $mysqli->set_charset("utf-8");
}
//	取得するデータタイプを求める
$ReqType　= "1";	//	1:NENDO_LIST_REQ , 2:GYOJI_DATA_REQ
if(isset($_GET["ReqType"])){
	$ReqType = $_GET["ReqType"];
}

//	年度を求める
$Mm = date("m");
$Nendo = date("Y");
if($Mm < 4) {
	$Nendo = $Nendo - 1;
}

if(isset($_GET["Nendo"])){
	$Nendo = $_GET["Nendo"];
}

//	班番号を求める
$HanNo = "99";
if(isset($_GET["HanNo"])){
	$HanNo = $_GET["HanNo"];
}

$TargetCheck = "";
if($HanNo != "99") {
	$HanBit = 1 << $HanNo;
	$TargetCheck = "(TargetFlags & $HanBit) > 0 and ";
}

$StartDay = $Nendo . "-04-01";
$EnDay    = ($Nendo + 1) . "-03-31";
$sql =	"SELECT No,Date,Bunrui,GyojiMei,StartTime,EndTime ".
		"FROM sybo_gyoji where $TargetCheck Date BETWEEN '$StartDay' AND '$EnDay' ".
		"order by Date,StartTime";

$result = $mysqli -> query($sql);

//クエリー失敗
if(!$result) {
    echo $mysqli->error;
    exit();
}

//レコード件数
$row_count = $result->num_rows;

//連想配列で取得
while($row = $result->fetch_array(MYSQLI_ASSOC)){
    $rows[] = $row;
}

//結果セットを解放
$result->free();

?>

<?php
	$bNext = 0;

	echo	'{' . "\r\n" . '"datas" : [' . "\r\n";
	foreach($rows as $row){
		if($bNext) {
			echo ',';
		}

		echo	'{ "gNo":"' . $row['No'] . '"';
		echo	', "gDate":"' . $row['Date'] . '"';
		echo	', "gStartTime":"' . sprintf("%02d:%02d",$row['StartTime'] / 100, $row['StartTime'] % 100)  . '"';
		echo	', "gEndTime":"' . sprintf("%02d:%02d",$row['EndTime'] / 100, $row['EndTime'] % 100) . '"';
		echo	', "gBunrui":"' . $row['Bunrui'] . '"';
		echo	', "gTitle":"' . $row['GyojiMei'] . '"';
		echo	'}' . "\r\n";

		$bNext = 1;
	}
	echo	']'. "\r\n" . '}';

	// データベース切断
	$mysqli->close();
?>
