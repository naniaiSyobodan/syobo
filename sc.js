function setSelIdx(idname, idx){
  var obj = document.getElementById(idname);
  obj.selectedIndex = idx;
}
function setSelVal(idname, val){
  var obj = document.getElementById(idname);
  obj.value = val;
}
function ListNendoChange() {
	target = document.getElementById("cmbYear");

	selindex = document.formNendoList.cmbYear.selectedIndex;
	switch (selindex) {
	case 1:
		target.innerHTML = "要素1が選択されています。<br/>";
		break;
	case 2:
		target.innerHTML = "要素2が選択されています。<br/>";
		break;
	case 3:
		target.innerHTML = "要素3が選択されています。<br/>";
		break;
	case 4:
		target.innerHTML = "要素4が選択されています。<br/>";
		break;
	case 5:
		target.innerHTML = "要素5が選択されています。<br/>";
		break;
	}
}