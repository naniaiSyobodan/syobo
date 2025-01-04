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
    //if(isset($_GET["ReqType"])){
    $ReqType = filter_input(INPUT_GET,'ReqType',FILTER_VALIDATE_INT);
    if($ReqType == false) {
        $ReqType = 1;	//	1:NENDO_LIST_REQ , 2:GYOJI_DATA_REQ
    }

    //  行事データ番号(Uniqe Key)を指定
    //if(isset($_GET["ReqNo"])) {
    $ReqNo = filter_input(INPUT_GET,'ReqNo',FILTER_VALIDATE_INT);
    if($ReqNo == false) {
        $ReqNo = 1;
    }

    //	年度・月を求める
    //if(isset($_GET["Nendo"])){
    $Nendo = filter_input(INPUT_GET,'Nendo',FILTER_VALIDATE_INT);
    if($Nendo == false) {
        $Nendo = date("Y");
    }

    //	班番号を求める
    $HanNo = filter_input(INPUT_GET,'HanNo',FILTER_VALIDATE_INT);

    $HanBit = 1 << $HanNo;
    $TargetCheck = "(TargetFlags & $HanBit) > 0 and ";

    //■■■■■■■■■■■■■■■■■■■■■■■■
    //  行事情報を読込
    //■■■■■■■■■■■■■■■■■■■■■■■■
    $sql =	"SELECT G.No,G.Date,G.GyojiMei,G.Bunrui,G.Syugo,StartTime,EndTime,A.name AS Atama,F.name AS Fuku,K.name AS Kutsu,S.SankaStr ". 
                    "from sybo_gyoji G " .
                    "inner join sybo_atama_name A ON G.F_Atama = A.no " .
                    "inner join sybo_fuku_name F ON G.F_Fuku = F.no " .
                    "inner join sybo_kutsu_name K ON G.F_Kutsu = K.no " .
                    "left  join (select * from sybo_sanka where GyojiNo=$ReqNo and KuNo=$HanNo) S ON G.No = S.GyojiNo " .
                    "where G.No = '$ReqNo';";

    $GyojiResult = $mysqli -> query($sql);

    //クエリー失敗
    if(!$GyojiResult) {
        echo $mysqli->error;
        exit();
    }

    //レコード件数
    $GyojiCount = $GyojiResult->num_rows;

    //連想配列で取得
    $row = $GyojiResult->fetch_array(MYSQLI_ASSOC);

    //echo	"row_count =  $Nendo , $ReqNo , $HanNo -> $row_count ";
    echo	'{' . "\r\n";
    echo	' "gNo":"' . $row['No'] . '"';
    echo	', "gDate":"' . $row['Date'] . '"';
    echo	', "gStartTime":"' . sprintf("%02d:%02d",$row['StartTime'] / 100, $row['StartTime'] % 100)  . '"';
    echo	', "gEndTime":"' . sprintf("%02d:%02d",$row['EndTime'] / 100, $row['EndTime'] % 100) . '"';
    echo	', "gTitle":"'. $row['GyojiMei'] . '"';
    echo	', "gBunrui":"'. $row['Bunrui'] . '"';
    echo	', "gSyugo":"'. $row['Syugo'] . '"';
    echo	', "gAtama":"'. $row['Atama'] . '"';
    echo	', "gFuku":"'. $row['Fuku'] . '"';
    echo	', "gKutsu":"'. $row['Kutsu'] . '"';
    echo	', "gSankaStr":"' . $row['SankaStr'] . '"';

    //行事名を覚えておく
    $GyojiMei = $row['GyojiMei'];
    
    //結果セットを解放
    $GyojiResult->free();

    $IncHancyo = false;
    if(($HanNo == 0) and ($GyojiMei == "定例会議")) {
        $IncHancyo = true;
    }
    
    //■■■■■■■■■■■■■■■■■■■■■■■■
    //  参加情報を読込
    //■■■■■■■■■■■■■■■■■■■■■■■■
    echo	', "gSanka" : [' . "\r\n";	//	参加者グループ
    
    $sql =	"select t.Nendo,t.Kaikyu,d.Name " .
                    "from sybo_taisei t " .
                    "join (select * from sybo_danin d where KuNo=$HanNo) d ON t.DaninNo = d.No " .
                    "where t.Nendo=$Nendo and t.KuNo=$HanNo " .
                    "order by t.TaiseiNo;";
    
    $SankaResult = $mysqli -> query($sql);
    //クエリー失敗
    if(!$SankaResult) {
        echo $mysqli->error;
        exit();
    }

    //レコード件数
    $SankaCount = $SankaResult->num_rows;

    $rows = array();    //連想配列で取得
    while($row = $SankaResult->fetch_array(MYSQLI_ASSOC)){
        $rows[] = $row;
    }

    $bNext = 0;
    foreach($rows as $row){
        if($bNext) {
                echo ',' . "\r\n";
        }

        echo	'{ "gKaikyu":"' . $row['Kaikyu'] . '"';
        echo	', "gName":"' . $row['Name'] . '"';
        echo	' }';

        $bNext = 1;
    }
    //結果セットを解放
    $SankaResult->free();

    if($IncHancyo == true) {
        $sql =	"select t.Nendo,t.No,t.Kaikyu,d.Name " .
                    "from sybo_taisei t " .
                    "join sybo_danin d ON t.DaninNo = d.No and d.KuNo = t.KuNo " .
                    "where t.Nendo=2021 and t.TaiseiNo=20 " .
                    "order by t.KuNo;";

        $HancyoResult = $mysqli -> query($sql);
        //クエリー失敗
        if(!$HancyoResult) {
            echo $mysqli->error;
            exit();
        }

        $HanRows = array();    //連想配列で取得
        while($row = $HancyoResult->fetch_array(MYSQLI_ASSOC)){
            $HanRows[] = $row;
        }
        $HanIx=1;
        foreach($HanRows as $row){
            echo	',' . "\r\n" .'{ "gKaikyu":"' . $HanIx . "区" .  $row['Kaikyu'] . '"';
            echo	', "gName":"' . $row['Name'] . '"';
            echo	' }';
            $HanIx++;
        }
        //結果セットを解放
        $HancyoResult->free();
    }
    
    echo    ']' . "\r\n";
    echo    '}' . "\r\n";


    // データベース切断
    $mysqli->close();
?>
