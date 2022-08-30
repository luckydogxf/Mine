
对后端的infobright做health check ,之简单的检查tcp 3306不够放心，毕竟好多情况下端口开启，但服务不正常。因此写了个php，思路是：通过自定义检查方式，
在monitor里填写目的ip/port然后 "GET /xxx.php?server=xxx",首先检查端口是否alive，然后判断该机器是否是维护状态（人为的在database写入一个记录READ/WRITE)，
最后返给Netscaler , NSC 根据这个判断该service是否正常。

<?php


/* Logic of this script

if( 1088 is alive)

        {check xxx_scheduler…@fwmrm_status

        return READ or WRITE
        }

else { return WRITE}

Note: when it's WRITE, NSC would take it OOS

*/

$status="HTTP/1.1 500 Internal Server Error"; // error 500 by default

    if(stristr($_GET["server"],'Forecast13')){ $instance_id=1; }

        elseif(stristr($_GET["server"],'Forecast12')){ $instance_id=2; }

        else{
        header($status);
        print "ERROR: unknown scheduler server";
        die(1);
}


function check_1088($host)
{

$fp = fsockopen($host,1088,$errno,$errstr,30);

if(!$fp){

   return 0;

} else {
    $out = "GET / HTTP/1.1rn";
    $out .= "Host: forecast12.xxx.net\r\n";
    $out .= "User-Agent: freewheel\r\n";
    $out .= "Connection: Close\r\n\r\n";
    fwrite($fp,$out);

    fclose($fp);

/* Scheduler is alive */

return 1; }

}

if (check_1088($_GET["server"]))

{

$link=mysql_connect('forecast12','user','xxx') // create connection to MySQL Server
        or die("ERROR: cannot connect to MySQL Server!".mysql_error());

$query_str=mysql_real_escape_string("SELECT status FROM forecast_scheduler_instance WHERE instance_id=$instance_id"); // prevent SQL injection

if(!mysql_select_db('fwmrm_status', $link)){ // make sure you can connect to AND select DB...or die
        header($status);
        print "ERROR: cannot select database";
        mysql_close($link);
        die(1);
}

$result=mysql_query($query_str) or die("Error:...".mysql_error());


if(!$result or empty($result)) {
        header($status);
        print "ERROR: null query response";
        mysql_close($link);
        die(1);
}


// Looks good...set HTTP status code 200 and print query response

list($mysql_return_str)=mysql_fetch_row($result);
$status="HTTP/1.1 200 OK";
header($status);
print $mysql_return_str;
mysql_close($link);

} else {

/* Scheduler:1088 is not in service,hence mark it 'WRITE' so that NSC would take it OOS. */

print "WRITE";}
?>


