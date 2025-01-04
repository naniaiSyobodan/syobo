# Copyright (C) 2001-2003 All right reserved by Shinya Kondo ( CGI KON )

# アドレス帳の表示

print "Content-type: text/html\n\n";
print qq!
<HTML>
<HEAD>
	<TITLE>アドレス帳</TITLE>
	<META Http-Equiv="Content-Type" Content="text/html;charset=EUC-JP">
</HEAD>
<BODY>
<CENTER>
<FORM ACTION="address_1.cgi" METHOD="post">
	<INPUT TYPE="hidden" NAME="gid" VALUE="$gid">
!;

	&Print_Index($gid);

print qq!
<TABLE BORDER=0 WIDTH="80%" BGCOLOR="#40E0D0" CELLPADDING="0" CELLSPACING="3">
<TR>
<TD ALIGN="center">
	<TABLE BORDER=0 WIDTH="100%" BGCOLOR="#DEEEEE" CELLPADDING="1" CELLSPACING="1">
		<TR BGCOLOR="#FFFFFF">
			<TD NOWRAP ALIGN="center">
				<FONT SIZE="2"><B>名　前</B></FONT>
			</TD>
			<TD NOWRAP ALIGN="center">
				<FONT SIZE="2"><B>電　話</B></FONT>
			</TD>
			<TD NOWRAP ALIGN="center">
				<FONT SIZE="2"><B>メール</B></FONT>
			</TD>
			<TD NOWRAP ALIGN="center">
				<FONT SIZE="2"><B>住　所</B></FONT>
			</TD>
		</TR>
!;

	if(open(IFILE,"address_1.tsv")) {
		while($line = <IFILE>) {
			chomp($line);
			@column = split("\t",$line);
			next if($column[0] ne $gid);

			print qq!
			<TR BGCOLOR="#FFFFFF">
				<TD NOWRAP>
					<FONT SIZE="2">　$column[1]</FONT>
				</TD>
				<TD NOWRAP>
					<FONT SIZE="2">　$column[2]</FONT>
				</TD>
				<TD NOWRAP>
					<FONT SIZE="2">　$column[3]</FONT>
				</TD>
				<TD NOWRAP>
					<FONT SIZE="2">　$column[4]</FONT>
				</TD>
			</TR>
			!;
		}
		close(IFILE);
	}

print qq!
		<TR BGCOLOR="#FFFFFF">
			<TD NOWRAP ALIGN="center">
				<INPUT TYPE="text" NAME="name" VALUE="$name">
			</TD>
			<TD NOWRAP ALIGN="center">
				<INPUT TYPE="text" NAME="tel" VALUE="$tel">
			</TD>
			<TD NOWRAP ALIGN="center">
				<INPUT TYPE="text" NAME="mail" VALUE="$mail">
			</TD>
			<TD NOWRAP ALIGN="center">
				<INPUT TYPE="text" NAME="address" VALUE="$address">
			</TD>
		</TR>
	</TABLE>
</TD>
</TR>
</TABLE>
	<FONT COLOR="#FF0000">$error</FONT><BR>
	<INPUT TYPE="submit" NAME="insert" VALUE="登録する">
</FORM>
<P>
<FONT SIZE=2><I>
Copyright (C) 2001-2003 All right reserved by <A HREF="http://cgikon.com">CGI KON</A>
</I></FONT>
</CENTER>
</BODY>
</HTML>
!;

# Copyright (C) 2001-2003 All right reserved by Shinya Kondo ( CGI KON )
