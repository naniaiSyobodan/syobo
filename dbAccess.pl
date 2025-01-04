#vデータベース接続
#my $server = "localhost";
my $server = "mysql303.phy.lolipop.lan";
#my $userName = "kyum";
my $userName = "LAA1590428";
#my $password = "k1lt7Ovl";
my $password = "k1lt7Ovl";
#my $dbName = "kyum";
my $dbName = "LAA1590428-kyum";
my $dbConnect = "DBI:mysql:" . $dbName . ":" . $server;
