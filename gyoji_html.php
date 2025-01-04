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
}else{
    $mysqli->set_charset("utf-8");
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
$StartDay = $Nendo . "-04-01";
$EnDay    = ($Nendo + 1) . "-03-31";
$sql = "SELECT No,Date,GyojiMei,StartTime,EndTime FROM sybo_gyoji where Date BETWEEN '$StartDay' AND '$EnDay' order by Date,StartTime";
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

// データベース切断
$mysqli->close();

?>

<!DOCTYPE html>
<html>
<head>
<title>第四回チーム内スコアアタック結果</title>
<meta charset="utf-8">
</head>
<body>
<h1>第四回チーム内スコアアタック結果</h1>
<p>2018年4月17日更新</p>

レコード件数：<?php echo $row_count; $Nendo; $sql; ?>
<table border='1'>
	<tr>
		<th>チーム名</th>
		<th>名前</th>
		<th>ハンドルネーム</th>
		<th>曲名1</th>
		<th>曲名2</th>
		<th>曲名3</th>
		<th>合計</th>
		<th>備考</th>
	</tr>

<?php
foreach($rows as $row){
?>
<tr>
	<td><?php echo $row['Date']; ?></td>
	<td><?php echo sprintf("%02d:%02d",$row['StartTime'] / 100, $row['StartTime'] % 100); ?></td>
	<td><?php echo sprintf("%02d:%02d",$row['EndTime'] / 100, $row['EndTime'] % 100); ?></td>
	<td><?php echo $row['GyojiMei']; ?></td>
</tr>
<?php
}
?>

</table>

</body>
</html>

