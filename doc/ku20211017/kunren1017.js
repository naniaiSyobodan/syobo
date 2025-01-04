var map;
var marker = [];
var infoWindow = [];
var markerData = [ // マーカーを立てる場所名・緯度・経度
	{
		name: '元ポンプ',
		lat: 36.6153703,
		lng: 138.0853078,
		icon: 'ic1.png'
	}, {
		name: '第１ポンプ',
		lat: 36.616595,
		lng: 138.083983,
		icon: 'ic2.png'
	}, {
		name: '第２ポンプ',
		lat: 36.6173756,
		lng: 138.0834085,
		icon: 'ic2.png'
	}, {
		name: '第３ポンプ',
		lat: 36.61808121219397, 
		lng: 138.08300029667345,
		icon: 'ic2.png'
	}, {
		name: '第４ポンプ',
		lat: 36.619518226023615, 
		lng: 138.08204564637464,
		icon: 'ic2.png'
	}, {
		//	https://www.google.co.jp/maps/@36.6198641,138.0813395,18.5z
		name: '筒先',
		lat: 36.6198641,
		lng: 138.0813395,
		icon: 'ic3.png'
	}
];
var aryDirection = new Array();		//	距離を格納するための配列
var aryElevation = new Array();		//	標高を格納するための配列
var bFinish = 0;

//var ds = google.maps.DirectionsStatus;//ルート結果のステータス
//var directionsErr = new Array(); //ルート結果のエラーメッセージ
//directionsErr[ds.INVALID_REQUEST] = "指定された DirectionsRequest が無効です。";
//directionsErr[ds.MAX_WAYPOINTS_EXCEEDED] = "DirectionsRequest に指定された DirectionsWaypoint が多すぎます。ウェイポイントの最大許容数は 8 に出発地点と到着地点を加えた数です。";
//directionsErr[ds.NOT_FOUND] = "出発地点、到着地点、ウェイポイントのうち、少なくとも 1 つがジオコード化できませんでした。";
//directionsErr[ds.OVER_QUERY_LIMIT] = "ウェブページは、短期間にリクエストの制限回数を超えました。";
//directionsErr[ds.REQUEST_DENIED] = "ウェブページではルート サービスを使用できません。";
//directionsErr[ds.UNKNOWN_ERROR] = "サーバー エラーのため、ルート リクエストを処理できませんでした。もう一度試すと正常に処理される可能性があります。";
//directionsErr[ds.ZERO_RESULTS] = "出発地点と到着地点間でルートを見つけられませんでした。";



function initMap() {
	var opts = {
		zoom: 16,
		center: new google.maps.LatLng(36.617714,138.0834171)
	};

	map = new google.maps.Map(document.getElementById("map"), opts);
	var directionsService = new google.maps.DirectionsService();
	var directionsRenderer = new google.maps.DirectionsRenderer();
	directionsRenderer.setPanel(document.getElementById('panel'));	//	DirectionsRenderer　結果のテキスト表示
	directionsRenderer.setMap(map);	 //  mapとDirectionsServiceを紐づける
	
	// 経路検索用リクエスト（べた書き・・・）
	//var request = {
	//	origin: new google.maps.LatLng(34.364991, 132.470085),
	//	destination: new google.maps.LatLng(34.366, 132.471),
	//	travelMode: google.maps.TravelMode.DRIVING
	//};

	// 経路表示（べた書き・・・）
	//directionsService.route(request, function(result, status) {
	//	alert(status);
	//	directionsRenderer.setDirections(result);
	//});	

	//var	origin		= new google.maps.LatLng(34.364991, 132.470085);
	//var	destination	= new google.maps.LatLng(34.366, 132.471);
	//var	travelMode	= google.maps.TravelMode.DRIVING;
	//
	//directionsService.route(
	//	{ // ルート リクエスト
	//		'origin'     : origin,     //出発地点
	//		'destination': destination,//到着地点
	//		'travelMode' : google.maps.DirectionsTravelMode.WALKING //ルートタイプ:徒歩
	//	},
	//	function(results, status) { // ルート結果callback関数
	//		if (status == "OK" /*ds.OK --*/) {  // 結果がOK ??
	//			// 結果をレンダラに渡し、ルートをマップに表示
	//			directionsRenderer.setDirections(results);
	//		} else {
	//			// 結果がOKではない場合
	//			alert("ルート検索が失敗しました。理由: " + /*directionsErr[*/ status /*]*/);
	//		}
	//	}
	//);
	
	map.addListener('drag', dispLatLng);

	//	標高差取得用の緯度経度を格納する配列
	var aryLatLon = new Array();

	// マーカー毎の処理
	for (var i = 0; i < markerData.length; i++) {
		markerLatLng = new google.maps.LatLng({lat: markerData[i]['lat'], lng: markerData[i]['lng']}); // 緯度経度のデータ作成
		aryLatLon.push(markerLatLng);			//	緯度経度を配列に格納
		marker[i] = new google.maps.Marker({	//	マーカーの追加
			position: markerLatLng, // マーカーを立てる位置を指定
			map: map, // マーカーを立てる地図を指定
			icon: {
				url: markerData[i]['icon'],	// マーカーの画像を変更
				labelOrigin: new google.maps.Point(40, 40)  //ラベルの基点
			},
			label: {
				text: markerData[i]['name'],                           //ラベル文字
				color: '#804040',                    //文字の色
				fontSize: '12px'                     //文字のサイズ
			}
		});

		infoWindow[i] = new google.maps.InfoWindow({ // 吹き出しの追加
			content: '<div class="sample">' + markerData[i]['name'] + '</div>' // 吹き出しに表示する内容
		});

		//marker[i].setOptions({	// マーカーのオプション設定
		//	icon: {
		//		url: markerData[i]['icon']// マーカーの画像を変更
		//	}
		//});
		markerEvent(i); // マーカーにクリックイベントを追加
		
		
		//	道のり計算リクエスト
		//if(i > 0) {
		//	var request = {
		//		origin: aryLatLon[i-1], //入力地点の緯度、経度
		//		destination: aryLatLon[i], //到着地点の緯度、経度
		//		travelMode: google.maps.DirectionsTravelMode.WALKING //ルートの種類は徒歩
		//	}
		//	directionsService.route(request,directionResultCallback);
		//}
	}

	//	中継点の配列を作成
	//var aryWayPoint = new Array(aryLatLon[1],aryLatLon[2],aryLatLon[3],aryLatLon[4]);
	//	道順を取得
	var request = {
		origin: aryLatLon[0], //入力地点の緯度、経度
		destination: aryLatLon[5], //到着地点の緯度、経度
		//waypoints: aryWayPoint
		waypoints: [
			{ location: new google.maps.LatLng({lat: markerData[1]['lat'], lng: markerData[1]['lng']}) },
			{ location: new google.maps.LatLng({lat: markerData[2]['lat'], lng: markerData[2]['lng']}) },
			{ location: new google.maps.LatLng({lat: markerData[3]['lat'], lng: markerData[3]['lng']}) },
			{ location: new google.maps.LatLng({lat: markerData[4]['lat'], lng: markerData[4]['lng']}) }
		],
		travelMode: google.maps.DirectionsTravelMode.WALKING, //ルートの種類は徒歩
	}
	directionsService.route(request,directionResultCallback);
	
	//	*=============================*
	//	*==	標高を求める					==*
	//	*=============================*
	// ElevationServiceのコンストラクタ
	var elevation = new google.maps.ElevationService();
	var req = {
		locations: aryLatLon,
	};
	elevation.getElevationForLocations(req, elevResultCallback);


	//	*=============================*
	//	*==	結果を編集					==*
	//	*=============================*
	
}

//	ルートを求めるためのコールバック
function directionResultCallback(results, status) 
{
	if (status != google.maps.ElevationStatus.OK) {
		alert(status);
		return;
	}

	if (status == 'OK') {
		//directionsRenderer.setDirections(response); // Add route to the map
		for (var i=0; i<results.routes[0].legs.length; i++) {
			aryDirection.push(results.routes[0].legs[i].distance.value);
		}
	}
	bFinish |= 1;
	if(bFinish == 3) {
		dispLatLng();
	}
}

//	標高を求めるためのコールバック
function elevResultCallback(results, status) 
{
	if (status != google.maps.ElevationStatus.OK) {
		alert(status);
		return;
	}

	if (status == google.maps.ElevationStatus.OK) {
		//var nEva = int( * 100) / 100.0;
		for (var i=0; i<results.length; i++) {
			//	結果表示文字列に編集する
			aryElevation.push(results[i].elevation);
		}
	}
	else {
		alert(status);
	}
	bFinish |= 2;
	if(bFinish == 3) {
		dispLatLng();
	}
}
	
function dispLatLng(){
	
	var msg = "地点 : 距離 : 標高<br>";
	for(var ix=0;ix < markerData.length; ix++) {
		msg += markerData[ix]['name'] + " : ";
		if(ix == 0) {
			msg += "000";
			msg += String.sprintf("m : %3.2lfm <br>\n",  aryElevation[ix]);
		}
		else {
			msg += aryDirection[ix - 1];
			msg += String.sprintf("m : %3.2lfm (%3.2lfm)<br>\n",  
						aryElevation[ix],aryElevation[ix]-aryElevation[ix-1]);
		}
	}
	document.getElementById("latlng").innerHTML = msg;
}

 
// マーカーにクリックイベントを追加
function markerEvent(i) {
    marker[i].addListener('click', function() { // マーカーをクリックしたとき
      infoWindow[i].open(map, marker[i]); // 吹き出しの表示
  });
}
