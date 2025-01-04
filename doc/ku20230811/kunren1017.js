var map;
var marker = [];
var infoWindow = [];
var markerData = [ // マーカーを立てる場所名・緯度・経度
	{	//	0
		name: '防火水槽１',	lat: 36.628612, lng: 138.077799,	icon: 'ic3.png'
	}, {	//	1
		name: '防火水槽２',	lat: 36.628163, lng: 138.076846,	icon: 'ic3.png'
	}, {	//	2
		name: '第１ポンプ',	lat: 36.628586, lng: 138.077729,	icon: 'ic4.png'
	}, {	//	3
		name: '第２ポンプ',	lat: 36.628133,	lng: 138.076847,	icon: 'ic4.png'
	}, {	//	4
		name: '積載車',		lat: 36.627548, lng: 138.077439,	icon: 'ic1.png'
	}, {	//	5
		name: '筒先１',		lat: 36.628636,	lng: 138.077201,	icon: 'ic2.png'
	}, {	//	6
		name: '筒先２',		lat: 36.628494, lng: 138.076920,	icon: 'ic2.png'
	}, {	//	7
		name: '筒先３',		lat: 36.628426, lng: 138.076570,	icon: 'ic2.png'
	}, {	//	8
		name: '水源１',		lat: 36.627960, lng: 138.076954,	icon: 'ic5.png'
	}, {	//	9
		name: '第３ポンプ',	lat: 36.628133,	lng: 138.076847,	icon: 'ic4.png'
	}, {	//	10
		name: '第４ポンプ',	lat: 36.628182, 	lng: 138.078957,icon: 'ic4.png'
	}, {	//	11
		name: '水源２',		lat: 36.629167, 	lng: 138.078652,icon: 'ic5.png'	, 
	}
];
var aryDirection = new Array();		//	距離を格納するための配列
var aryElevation = new Array();		//	標高を格納するための配列
var bFinish = 0;


function initMap() {
	var opts = {
		zoom: 18,
		center: new google.maps.LatLng(36.628269, 138.077584)
	};

	map = new google.maps.Map(document.getElementById("map"), opts);
	var directionsService = new google.maps.DirectionsService();
	var directionsRenderer = new google.maps.DirectionsRenderer();
	directionsRenderer.setPanel(document.getElementById('panel'));	//	DirectionsRenderer　結果のテキスト表示
	directionsRenderer.setMap(map);	 //  mapとDirectionsServiceを紐づける
	
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
		markerEvent(i); // マーカーにクリックイベントを追加
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
	//	*==	接続線を編集					==*
	//	*=============================*
	LineDraw(map,"#FF0000",[2,0,5]);
	LineDraw(map,"#00FF00",[0,6]);
	LineDraw(map,"#0000FF",[8,3,7]);
}

//	ポイント間の線を引く
function LineDraw(map,lineColor, arrMarkerIx) 
{
 	var flightPlanCoordinates = [];	//	ポイント用配列
	tempData.forEach( (arrMarkerIx, index) => {
	    flightPlanCoordinates.push(new google.maps.LatLng(markerData[arrMarkerIx].lat, markerData[arrMarkerIx].lng);
	});
    flightPath = new google.maps.Polyline({
        path: flightPlanCoordinates,
        strokeColor: lineColor,
        strokeOpacity: 1.0,
        strokeWeight: 2
    });
    flightPath.setMap(map);
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
	
//	var msg = "地点 : 距離 : 標高<br>";
//	for(var ix=0;ix < markerData.length; ix++) {
//		msg += markerData[ix]['name'] + " : ";
//		if(ix == 0) {
//			msg += "000";
//			msg += String.sprintf("m : %3.2lfm <br>\n",  aryElevation[ix]);
//		}
//		else {
//			msg += aryDirection[ix - 1];
//			msg += String.sprintf("m : %3.2lfm (%3.2lfm)<br>\n",  
//						aryElevation[ix],aryElevation[ix]-aryElevation[ix-1]);
//		}
//	}
//	document.getElementById("latlng").innerHTML = msg;
}

 
// マーカーにクリックイベントを追加
function markerEvent(i) {
    marker[i].addListener('click', function() { // マーカーをクリックしたとき
      infoWindow[i].open(map, marker[i]); // 吹き出しの表示
  });
}
