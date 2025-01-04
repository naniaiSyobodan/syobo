const infDanin = {
  no: 0,
  name: ""
};

function RotaeMember() {
	inpLast=0;
	var listDanin = new Array();

	//	団員番号をワイルドカードで取得
	DaninList = document.querySelector('input[name="rdDaninNo*"]')
	
	DaninList.forEach(function(item,index) {
		ctl = 'rdDaninName' + index;
		nameCtl = getElementsByName(ctl);
		infDanin = {
			no:item.value;
			name:nameCtl.value;
		}
		listDanin.push(infDanin);
	}
		
	txt[0] = document.forms.id_form1.rdDanin1.value;
	txt[1] = document.forms.id_form1.rdDanin2.value;
	txt[2] = document.forms.id_form1.rdDanin3.value;
	txt[3] = document.forms.id_form1.rdDanin4.value;
	txt[4] = document.forms.id_form1.rdDanin5.value;
	txt[5] = document.forms.id_form1.rdDanin6.value;
	txt[6] = document.forms.id_form1.rdDanin7.value;
	txt[7] = document.forms.id_form1.rdDanin8.value;
	txt[8] = document.forms.id_form1.rdDanin9.value;
	txt[9] = document.forms.id_form1.rdDanin10.value;
	for(ix=0;ix<10;ix++) {
		if(txt[ix] != "") {
			inpLast=ix;
		}
	}
	topTxt = txt[0];
	for(ix=0;ix<inpLast;ix++) {
		txt[ix] = txt[ix+1];
	}
	txt[inpLast] = topTxt;
	document.forms.id_form1.rdDanin1.value = txt[0];
	document.forms.id_form1.rdDanin2.value = txt[1];
	document.forms.id_form1.rdDanin3.value = txt[2];
	document.forms.id_form1.rdDanin4.value = txt[3];
	document.forms.id_form1.rdDanin5.value = txt[4];
	document.forms.id_form1.rdDanin6.value = txt[5];
	document.forms.id_form1.rdDanin7.value = txt[6];
	document.forms.id_form1.rdDanin8.value = txt[7];
	document.forms.id_form1.rdDanin9.value = txt[8];
	document.forms.id_form1.rdDanin10.value = txt[9];
}
//	固定のファイルは読めないとのことで諦めた
function ResetMember(FName) {

	//FileReaderの作成
	var reader = new FileReader();
	//テキスト形式で読み込む
	reader.readAsText(FName);

	//読込終了後の処理
	reader.onload = function(ev){
		var data = reader.result;
		var txt = data.split('<>');
		document.forms.id_form1.rdDanin1.value = txt[0];
		document.forms.id_form1.rdDanin2.value = txt[1];
		document.forms.id_form1.rdDanin3.value = txt[2];
		document.forms.id_form1.rdDanin4.value = txt[3];
		document.forms.id_form1.rdDanin5.value = txt[4];
		document.forms.id_form1.rdDanin6.value = txt[5];
		document.forms.id_form1.rdDanin7.value = txt[6];
		document.forms.id_form1.rdDanin8.value = txt[7];
		document.forms.id_form1.rdDanin9.value = txt[8];
		document.forms.id_form1.rdDanin10.value = txt[9];
	}
}
