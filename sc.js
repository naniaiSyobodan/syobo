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
		target.innerHTML = "�v�f1���I������Ă��܂��B<br/>";
		break;
	case 2:
		target.innerHTML = "�v�f2���I������Ă��܂��B<br/>";
		break;
	case 3:
		target.innerHTML = "�v�f3���I������Ă��܂��B<br/>";
		break;
	case 4:
		target.innerHTML = "�v�f4���I������Ă��܂��B<br/>";
		break;
	case 5:
		target.innerHTML = "�v�f5���I������Ă��܂��B<br/>";
		break;
	}
}